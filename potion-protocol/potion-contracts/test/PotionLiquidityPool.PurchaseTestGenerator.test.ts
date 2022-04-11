import { waffle } from 'hardhat'
import { expect } from 'chai'
import { BigNumber } from 'ethers'
import {
  CounterpartyDetails,
  PurchaseParams,
  CreateAndPurchaseParams,
  SettleTestCase,
  Pool,
  OutstandingSettlementTestCase,
} from '../scripts/lib/purchaseHelpers'
import { usdcDecimals, deployTestContracts, getTestOtoken, mintTokens, TestContracts } from './helpers/testSetup'
import { CurveCriteria, HyperbolicCurve } from '../scripts/lib/typeHelpers'

const provider = waffle.provider

import {
  MockERC20,
  MockOracle,
  Otoken as OtokenInstance,
  OtokenFactory,
  PotionLiquidityPool,
  CurveManager,
  CriteriaManager,
} from '../typechain'
import { createTokenAmount, createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { deployDefaultCurves, deployDefaultCriteria } from '../scripts/lib/postDeployActions/CurveAndCriteriaActions'
import testSuccessfulCreateAndBuyOtokens from './helpers/testSuccessfulCreateAndBuyOtokens'
import testSuccessfulBuyOtokens from './helpers/testSuccessfulBuyOtokens'
import testSuccessfulSettleAndRedistribute from './helpers/testSuccessfulSettleAndRedistribute'
import testSuccessfulOutstandingSettlement from './helpers/testSuccessfulOutstandingSettlement'

// When testing purchases and settlements, we often want to run the same set of operations and the same set of checks.
// This suite of tests does that, by generating a set of nearly-identical tests in the before() block.
//
// To add additional tests, add additional data to the arrays: successfulPurchaseParams, createAndPurchaseParams & successfulSettleTestCases
// To change what the generated tests *do*, edit the code that iterates through those arrays
describe('PotionLiquidityPool (Purchase Test Generator)', function () {
  const wallets = provider.getWallets()
  const [potionBuyer1, potionBuyer2, potionLp1, potionLp2, potionLp3, potionLp4, potionLp5] = wallets
  let expiry: number
  let usdcStartAmount: BigNumber

  let testContracts: TestContracts
  let otokenFactory: OtokenFactory
  let potionLiquidityPool: PotionLiquidityPool
  let curveManager: CurveManager
  let criteriaManager: CriteriaManager

  // oracle module mock
  let oracle: MockOracle

  let usdc: MockERC20
  let weth: MockERC20

  const ethSpotPriceInDollars = 300 // $ per ETH
  const lowerStrikeInDollars = 200 // $ per ETH
  const higherStrikeInDollars = 300 // $ per ETH
  let lowerStrikePut: OtokenInstance
  let higherStrikePut: OtokenInstance
  let higherStrikePrice: BigNumber
  let lowerStrikePrice: BigNumber
  let curve1: HyperbolicCurve
  let curve2: HyperbolicCurve
  let curveHash1: string
  let curveHash2: string
  let poolId1: number
  let poolId2: number
  let criteria1: CurveCriteria
  let criteria2: CurveCriteria
  let criteriaSetHash1: string
  let criteriaSetHash2: string

  const tokenAmount8 = scaleNum(8)
  const tokenAmount55 = scaleNum(55)
  const heterogeneousTokenAmounts = [tokenAmount8, tokenAmount55, tokenAmount8, tokenAmount55, scaleNum(4242)]
  const fiveLps = [potionLp1, potionLp2, potionLp3, potionLp4, potionLp5]

  before('set up contracts', async () => {
    testContracts = await deployTestContracts()
    ;({ potionLiquidityPool, usdc, weth, oracle, otokenFactory, curveManager, criteriaManager } = testContracts)

    // TODO: WIBNI the following code, to create test data: (A) was shared between tests and (B) used post-deploy actions just like our deploy script
    await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars)) // TODO: test with other real-time prices

    // Create a single curve, criteria, and criteriaSet for testing
    poolId1 = 0
    poolId2 = 99
    const curves = await deployDefaultCurves(curveManager)
    const { criteria, criteriaSets } = await deployDefaultCriteria(criteriaManager, weth.address, usdc.address)
    curve1 = curves[0]
    curve2 = curves[1]
    curveHash1 = curve1.toKeccak256()
    curveHash2 = curve2.toKeccak256()
    criteria1 = criteria[0]
    criteria2 = criteria[1]
    criteriaSetHash1 = criteriaSets[0].toKeccak256()
    criteriaSetHash2 = criteriaSets[1].toKeccak256()

    // Add some options; one is deployed and one is not deployed yet
    ;({ put: lowerStrikePut, scaledStrike: lowerStrikePrice, expiry } = await getTestOtoken({
      otokenFactory,
      strikeAsset: usdc.address,
      underlyingAsset: weth.address,
      deploy: false,
      strikeInDollars: lowerStrikeInDollars,
    }))
    ;({ put: higherStrikePut, scaledStrike: higherStrikePrice } = await getTestOtoken({
      otokenFactory,
      strikeAsset: usdc.address,
      underlyingAsset: weth.address,
      deploy: false,
      strikeInDollars: higherStrikeInDollars,
    }))

    // mint usdc to users
    usdcStartAmount = createTokenAmount(100000000, usdcDecimals)
    const mintings = wallets.map((w) => ({ wallet: w, amount: usdcStartAmount }))
    await mintTokens(usdc, mintings, potionLiquidityPool.address)

    // Have LPs deposit collateral
    const depositAmount1 = createTokenAmount(1000000, usdcDecimals)
    await potionLiquidityPool.connect(potionLp1).deposit(poolId1, depositAmount1)
    await potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash1)
    await potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)

    const depositAmount2 = createTokenAmount(2000000, usdcDecimals)
    for (const w of [potionLp2, potionLp3, potionLp4]) {
      await potionLiquidityPool
        .connect(w)
        .depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash1)
    }

    await potionLiquidityPool
      .connect(potionLp5)
      .depositAndConfigurePool(poolId2, depositAmount2, curveHash2, criteriaSetHash2)
  })

  describe('Test generator', () => {
    // We (ab)use the before() block to generate dynamic test cases
    before(async () => {
      describe('PotionLiquidityPool (Generated Purchase Tests)', () => {
        describe('Successful create/buy/settle tests', () => {
          const fiveCriteria = [criteria1, criteria1, criteria1, criteria1, criteria2]
          const fivePoolIds = [poolId1, poolId1, poolId1, poolId1, poolId2]
          const fiveCurves = [curve1, curve1, curve1, curve1, curve2]
          const fiveLpSellers1 = CounterpartyDetails.fromLists(
            fiveLps,
            fivePoolIds,
            fiveCurves,
            fiveCriteria,
            heterogeneousTokenAmounts,
          )

          const singleLpSeller0 = new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, tokenAmount55)
          const singleLpSeller1 = new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, tokenAmount8)
          const singleLpSeller2 = new CounterpartyDetails(potionLp2, poolId1, curve1, criteria1, tokenAmount55)

          const createAndPurchaseParams: CreateAndPurchaseParams[] = [
            new CreateAndPurchaseParams(
              'higher strike put, buyer1, 5 LPs',
              potionBuyer1,
              weth.address,
              usdc.address,
              usdc.address,
              higherStrikePrice,
              expiry,
              true,
              fiveLpSellers1,
              higherStrikePut.address,
            ),
            new CreateAndPurchaseParams(
              'lower strike put, buyer1, single LP',
              potionBuyer1,
              weth.address,
              usdc.address,
              usdc.address,
              lowerStrikePrice,
              expiry,
              true,
              [singleLpSeller0],
              lowerStrikePut.address,
            ),
          ]

          const successfulPurchaseParams: PurchaseParams[] = [
            // new PurchaseParams('buyer1, single LP', potionBuyer1, lowerStrikePut, [singleLpSeller1]),
            new PurchaseParams('buyer1, single LP (again; lower gas cost)', potionBuyer1, lowerStrikePut, [
              singleLpSeller1,
            ]),
            new PurchaseParams('buyer2, single LP', potionBuyer2, lowerStrikePut, [singleLpSeller2]),
            new PurchaseParams('buyer1, 5 LPs', potionBuyer1, lowerStrikePut, fiveLpSellers1),
            new PurchaseParams('buyer1, 5 LPs (again; lower gas cost)', potionBuyer1, lowerStrikePut, fiveLpSellers1),
            // new PurchaseParams('buyer1, 5 LPs, higher strike', potionBuyer1, higherStrikePut, fiveLpSellers1),
          ]

          // Settle test cases must be defined *after* purchase test cases if they are to know the correct expected contributions
          const successfulSettleTestCases: SettleTestCase[] = [
            new SettleTestCase(
              'higher price put',
              higherStrikePut,
              true,
              fiveLpSellers1.map((seller) => new Pool(seller.lp, seller.poolId)),
              ethSpotPriceInDollars,
              higherStrikeInDollars,
            ),
            new SettleTestCase(
              'lower price put',
              lowerStrikePut,
              true,
              fiveLpSellers1.map((seller) => new Pool(seller.lp, seller.poolId)),
              ethSpotPriceInDollars,
              lowerStrikeInDollars,
            ),
          ]

          const successfulOutstandingSettlementTestCases: OutstandingSettlementTestCase[] = [
            new OutstandingSettlementTestCase(
              'outstandingSettlement: higher price put',
              higherStrikePut,
              fiveLpSellers1.map((seller) => new Pool(seller.lp, seller.poolId)),
              ethSpotPriceInDollars,
              higherStrikeInDollars,
            ),
            new OutstandingSettlementTestCase(
              'outstandingSettlement: lower price put',
              lowerStrikePut,
              fiveLpSellers1.map((seller) => new Pool(seller.lp, seller.poolId)),
              ethSpotPriceInDollars,
              lowerStrikeInDollars,
            ),
          ]

          // We do all the createAndBuyOtokens before any of the buyOtokens, in case buyOtokens depends on successful creations
          createAndPurchaseParams.forEach((tc) => {
            it(`createAndBuyOtokens: ${tc.descr}`, async () => {
              // We would like to test premiums and collateral needed, like we already do in in the
              // buyOtokens (without creation) test cases, but the former would new function on the
              // contract to predict premiums before otoken existence
              await testSuccessfulCreateAndBuyOtokens(testContracts, tc)
            })
          })

          successfulPurchaseParams.forEach((tc) => {
            it(`buyOtokens: ${tc.descr}`, async () => {
              await testSuccessfulBuyOtokens(testContracts, tc)
            })
          })

          successfulOutstandingSettlementTestCases.forEach((tc) => {
            it(`check outstandingSettlement: ${tc.descr}`, async () => {
              await testSuccessfulOutstandingSettlement(testContracts, tc)
            })
          })

          successfulSettleTestCases.forEach((tc) => {
            it(`settle: ${tc.descr}`, async () => {
              await testSuccessfulSettleAndRedistribute(testContracts, tc)
            })
          })
        })
      })
    })

    it('Generate tests', () => {
      // Dummy test case required to ensure before() runs
      expect(1).to.equal(1)
    })
  })
})
