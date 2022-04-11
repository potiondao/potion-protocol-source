import type { Wallet } from 'ethers'
import { BigNumber, BigNumberish } from 'ethers'
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'

import { Otoken as OtokenInstance } from '../../typechain'
import { CurveCriteria, CurveParamsAsBigNumbers, HyperbolicCurve } from './typeHelpers'

// When a buyer wants to accept any amount of premium slippage, they can pass this as the max premium
export const MAX_UINT_256 = BigNumber.from(2).pow(256).sub(1)

function assert(input: boolean, message?: string): asserts input {
  if (!input) throw new Error(message ? message : 'assertion failed')
}
export class CounterpartyDetails {
  lp: string
  curve: CurveParamsAsBigNumbers

  constructor(
    public lpWallet: Wallet | SignerWithAddress,
    public poolId: BigNumberish,
    public curveAs64x64: HyperbolicCurve,
    public criteria: CurveCriteria,
    public orderSizeInOtokens: BigNumber,
  ) {
    this.lp = lpWallet.address
    this.curve = curveAs64x64.asSolidityStruct()
  }

  static fromLists(
    lps: Wallet[],
    poolIds: BigNumberish[],
    curves: HyperbolicCurve[],
    criteria: CurveCriteria[],
    orderSizesInOTokens: BigNumber[],
  ): CounterpartyDetails[] {
    assert(lps.length === poolIds.length, 'Different length lists (LPs vs. curves)')
    assert(lps.length === curves.length, 'Different length lists (LPs vs. curves)')
    assert(lps.length === orderSizesInOTokens.length, 'Different length lists (LPs vs. order sizes)')
    assert(lps.length === criteria.length, 'Different length lists (LPs vs. criteria hashes)')
    const retList: CounterpartyDetails[] = []
    for (let i = 0; i < lps.length; i++) {
      retList.push(new CounterpartyDetails(lps[i], poolIds[i], curves[i], criteria[i], orderSizesInOTokens[i]))
    }
    return retList
  }
}

let allContributions = new Map<string, Map<symbol, BigNumber>>()

export const resetContributions = (): void => {
  allContributions = new Map<string, Map<symbol, BigNumber>>()
}

const incrementContribution = (
  otokenAddress: string,
  pool: Pool,
  incrementAmount: BigNumber,
): Map<symbol, BigNumber> => {
  let contributers = new Map<symbol, BigNumber>()
  if (allContributions.has(otokenAddress)) {
    contributers = allContributions.get(otokenAddress) as Map<symbol, BigNumber>
  }

  let newVal = incrementAmount
  if (contributers.has(pool.key)) {
    newVal = (contributers.get(pool.key) as BigNumber).add(incrementAmount)
  }
  allContributions.set(otokenAddress, contributers)
  return contributers.set(pool.key, newVal)
}

export class PurchaseParams {
  constructor(
    public descr: string,
    public buyer: Wallet | SignerWithAddress,
    public otoken: OtokenInstance,
    public sellers: CounterpartyDetails[],
  ) {
    for (const s of sellers) {
      const pool = new Pool(s.lp, s.poolId)
      incrementContribution(otoken.address, pool, s.orderSizeInOtokens)
    }
  }
}
export class CreateAndPurchaseParams {
  constructor(
    public descr: string,
    public buyer: Wallet,
    public underlyingAsset: string,
    public strikeAsset: string,
    public collateralAsset: string,
    public strikePrice: BigNumber,
    public expiry: number,
    public isPut: boolean,
    public sellers: CounterpartyDetails[],
    expectedOtokenAddress: string, // Used only to derive expected contributions
  ) {
    for (const s of sellers) {
      const pool = new Pool(s.lp, s.poolId)
      incrementContribution(expectedOtokenAddress, pool, s.orderSizeInOtokens)
    }
  }
}

export class Pool {
  constructor(public lp: string, public poolId: BigNumberish) {}

  get key(): symbol {
    return Symbol.for(`Pool[${this.lp}:${this.poolId}]`)
  }
}

// Settle test cases must be defined *after* purchase test cases if they are to know the correct expected contributions
export class SettleTestCase {
  public contributions: Map<symbol, BigNumber>
  constructor(
    public descr: string,
    public otoken: OtokenInstance,
    public doSettle: boolean,
    public redistributeToPools: Pool[],
    public expiryPriceUnderlyingInDollars: number,
    public strikePriceInDollars: number,
  ) {
    this.contributions = allContributions.get(otoken.address) || new Map<symbol, BigNumber>()
  }
}

export class OutstandingSettlementTestCase {
  public contributions: Map<symbol, BigNumber>
  constructor(
    public descr: string,
    public otoken: OtokenInstance,
    public redistributeToPools: Pool[],
    public expiryPriceUnderlyingInDollars: number,
    public strikePriceInDollars: number,
  ) {
    this.contributions = allContributions.get(otoken.address) || new Map<symbol, BigNumber>()
  }
}
