import { ethers } from 'hardhat'
import { BigNumber, BigNumberish, ContractFactory } from 'ethers'
import { CurveCriteria, HyperbolicCurve, CriteriaSet } from '../typeHelpers'
import { MockOracle, Otoken as OtokenInstance, OtokenFactory } from '../../../typechain'
import { DepositParams } from '../lpHelpers'
import { CounterpartyDetails, PurchaseParams } from '../purchaseHelpers'
import { createValidExpiry } from '../../../test/helpers/OpynUtils'
import { Deployment } from '../../../deploy/deploymentConfig'
import { PostDeployAction, PostDeployActionResult, PostDeployActionsResults, OtokenParams } from '../postDeploy'
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import BigDecimal from 'bignumber.js'

// We select buyers from from the back of the list (in reverse), so for a small number of LPs and buyers they will not overlap
export async function getBuyers(count?: number): Promise<SignerWithAddress[]> {
  const signers = await (await ethers.getSigners()).slice().reverse()
  count = count || signers.length
  if (count > signers.length) {
    throw Error(`${count} LPs requested but only ${signers.length} signers available`)
  }
  return signers.slice(0, count)
}

// Uses the max possible otoken price and max possible duration, for the given criteria
const defaultOtokenParamsForCriteria = async (
  timeNow: number,
  oracle: MockOracle,
  c: CurveCriteria,
): Promise<OtokenParams> => {
  const { underlyingAsset, strikeAsset, isPut, maxStrikePercent, maxDurationInDays } = c
  const expiry = createValidExpiry(timeNow, BigNumber.from(maxDurationInDays).toNumber())
  const scaledUnderlyingPrice = await oracle.getPrice(underlyingAsset)
  const scaledStrike = scaledUnderlyingPrice.mul(maxStrikePercent).div(100)
  return {
    underlyingAsset,
    strikeAsset: strikeAsset,
    collateralAsset: strikeAsset,
    strikePrice: scaledStrike,
    expiry,
    isPut,
  }
}

export type OtokenParamsGenerator = {
  (depl: Deployment, dataSoFar: PostDeployActionsResults): Promise<OtokenParams[]>
}

const generateDefaultOtokenParams: OtokenParamsGenerator = async (depl, dataAlreadyDeployed) => {
  const now = (await ethers.provider.getBlock('latest')).timestamp
  const oracle = await depl.mockedOracle()
  const criteria = dataAlreadyDeployed.allDataOfType(CurveCriteria)
  const result: OtokenParams[] = []

  for (const c of criteria) {
    result.push(await defaultOtokenParamsForCriteria(now, oracle, c))
  }
  return result
}

const getOrCreateOtokenForParams = async (
  otokenFactory: OtokenFactory,
  OtokenInstanceFactory: ContractFactory,
  p: OtokenParams,
): Promise<OtokenInstance> => {
  let address = await otokenFactory.getOtoken(
    p.underlyingAsset,
    p.strikeAsset,
    p.strikeAsset,
    p.strikePrice,
    p.expiry,
    p.isPut,
  )

  if (address == '0x0000000000000000000000000000000000000000') {
    const trx = await otokenFactory.createOtoken(
      p.underlyingAsset,
      p.strikeAsset,
      p.strikeAsset,
      p.strikePrice,
      p.expiry,
      p.isPut,
    )
    await trx.wait()
    address = await otokenFactory.getOtoken(
      p.underlyingAsset,
      p.strikeAsset,
      p.strikeAsset,
      p.strikePrice,
      p.expiry,
      p.isPut,
    )
  }
  return (await OtokenInstanceFactory.attach(address)) as OtokenInstance
}

const getOtokenForParams = async (
  otokenFactory: OtokenFactory,
  OtokenInstanceFactory: ContractFactory,
  p: OtokenParams,
): Promise<OtokenInstance | void> => {
  const address = await otokenFactory.getOtoken(
    p.underlyingAsset,
    p.strikeAsset,
    p.strikeAsset,
    p.strikePrice,
    p.expiry,
    p.isPut,
  )

  if (address != '0x0000000000000000000000000000000000000000') {
    return (await OtokenInstanceFactory.attach(address)) as OtokenInstance
  }
}

export class CreateOtokens implements PostDeployAction {
  public constructor(public otokenParamGenerator: OtokenParamsGenerator = generateDefaultOtokenParams) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult> {
    const otokens: PostDeployActionResult = []
    const otokenInstanceFactory = await ethers.getContractFactory('Otoken')
    const otokenParams = await this.otokenParamGenerator(depl, dataAlreadyDeployed)
    printProgress && console.log(`Creating up to ${otokenParams.length} otokens on chain`)

    for (const p of otokenParams) {
      otokens.push(await getOrCreateOtokenForParams(await depl.otokenFactory(), otokenInstanceFactory, p))
    }
    return otokens
  }
}

const weiToHumanReadable = (input: BigNumberish, decimals: BigNumberish): string => {
  const inp = new BigDecimal(BigNumber.from(input).toString())
  const shift = Math.abs(BigNumber.from(decimals).toNumber()) * -1
  return inp.shiftedBy(shift).toString()
}
// const humanReadableToWei = (input: BigNumberish, decimals: BigNumberish): BigNumber => {
//   const inp = BigNumber.from(input)
//   return inp.mul(BigNumber.from(10).pow(decimals))
// }

const getOtokenAmountForTargetUtil = async (
  otoken: OtokenInstance,
  depl: Deployment,
  poolOfCapital: DepositParams,
  targetUtilPercent: BigNumberish,
): Promise<BigNumber> => {
  const potionLiquidityPool = await depl.potionLiquidityPool()
  const totalInPool = await potionLiquidityPool.lpTotalAmount(poolOfCapital.lp.address, poolOfCapital.poolId)
  const lockedInPool = await potionLiquidityPool.lpLockedAmount(poolOfCapital.lp.address, poolOfCapital.poolId)
  const targetCollateralAmountInWei = totalInPool.sub(lockedInPool).mul(targetUtilPercent).div(100)
  const decimals = await (await depl.faucetToken()).decimals()
  const strikePriceWith8Decimals = await otoken.strikePrice()

  // To get the otoken amount in human readable units we do:
  //    (targetCollateralInUSD / strikePriceInUSD)
  // Therefore, to get the otoken amount in otoken wei (decimals = 8) we do:
  //    (targetCollateralInUSD / strikePriceInUSD) * 10^8
  //  =  (targetCollateralInWei / collateralDecimals) / (strikePriceWith8Decimals / 10^8) * 10^8
  // To avoid loss of precision with integers, we re-order this to:
  //  =  (targetCollateralInWei * 10^8 * 10^8 / collateralDecimals) / (strikePriceWith8Decimals)
  const otokenAmount = BigNumber.from(weiToHumanReadable(targetCollateralAmountInWei.mul(1e8).mul(1e8), decimals)).div(
    strikePriceWith8Decimals,
  )

  // Debug info
  // console.log(` - LP's current total collateral is $${weiToHumanReadable(totalInPool, decimals)} (${totalInPool} wei)`)
  // console.log( `Getting collateral amount for strike price of $${weiToHumanReadable( strikePriceWith8Decimals, 8, )} (${strikePriceWith8Decimals})`, )
  // console.log( ` - Targetting collateral of $${weiToHumanReadable( targetCollateralAmountInWei, decimals, )} (${targetCollateralAmountInWei}) by buying ${otokenAmount}`, )

  // CHECK
  // const collateralNeededForPuts = await potionLiquidityPool.collateralNeededForPuts(otoken.address, otokenAmount)
  // console.log( `This will use            $${weiToHumanReadable( collateralNeededForPuts, decimals, )} (${collateralNeededForPuts}) collateral`, )

  return otokenAmount
}

export type PurchaseGenerator = {
  (depl: Deployment, dataSoFar: PostDeployActionsResults, count: number, targetUtilPercent: number): Promise<
    PurchaseParams[]
  >
}

const generateDefaultPurchases: PurchaseGenerator = async (depl, dataAlreadyDeployed, count, targetUtilPercent) => {
  const buyers = await getBuyers()
  const purchases: PurchaseParams[] = []
  const deposits = dataAlreadyDeployed.allDataOfType(DepositParams)
  const now = (await ethers.provider.getBlock('latest')).timestamp

  let i_deposit = 0
  let i = 0
  while (i < count) {
    const poolOfCapital = deposits[i_deposit % deposits.length]
    const curve = HyperbolicCurve.registry.get(poolOfCapital.curveHash) as HyperbolicCurve
    const criteria = (CriteriaSet.registry.get(poolOfCapital.criteriaSetHash) as Set<CurveCriteria>).values().next()
      .value // TODO: check criteria compatibility with chosen otoken
    const otokenInstanceFactory = await ethers.getContractFactory('Otoken')
    const oracle = await depl.mockedOracle()
    const otokenParams = await defaultOtokenParamsForCriteria(now, oracle, criteria)
    const otoken = await getOtokenForParams(await depl.otokenFactory(), otokenInstanceFactory, otokenParams)
    if (!otoken) throw `No existing otoken found for params: ${JSON.stringify(otokenParams, null, 2)}`
    const otokenAmount = await getOtokenAmountForTargetUtil(otoken, depl, poolOfCapital, targetUtilPercent)
    purchases.push(
      new PurchaseParams(`sampleData iteration ${i}`, buyers[i % buyers.length], otoken, [
        new CounterpartyDetails(poolOfCapital.lp, poolOfCapital.poolId, curve, criteria, otokenAmount),
      ]),
    )

    // Now increment counter(s)
    if (++i == buyers.length) {
      // We've looped around all buyers (again)
      i_deposit++
    }
  }
  return purchases
}

export class InitializeSamplePurchases implements PostDeployAction {
  public constructor(
    public purchaseCount = 5,
    public targetUtilPercent = 50,
    public purchaseGenerator: PurchaseGenerator = generateDefaultPurchases,
  ) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult> {
    printProgress && console.log(`Writing purchase transaction(s) to the chain`)
    const purchases = await this.purchaseGenerator(
      depl,
      dataAlreadyDeployed,
      this.purchaseCount,
      this.targetUtilPercent,
    )
    const lpContract = await depl.potionLiquidityPool()
    const maxPremium = ethers.constants.MaxUint256

    for (const p of purchases) {
      printProgress && console.log(` - Purchasing otoken ${p.otoken.address} with ${p.buyer.address}`)
      const blockTime = (await ethers.provider.getBlock('latest')).timestamp
      const expiry = (await p.otoken.expiryTimestamp()).toNumber()
      printProgress && console.log(`       Otoken expires (${(expiry - blockTime) / (24 * 3600)} days from now`)
      printProgress && console.log(`       Buying from ${await p.sellers.length} LPs/curves`)
      const trx = await lpContract.connect(p.buyer).buyOtokens(p.otoken.address, p.sellers, maxPremium)
      await trx.wait()
    }
    return purchases
  }
}
