import { ethers } from 'hardhat'
import { BigNumber, BigNumberish } from 'ethers'
import { CurveCriteria, HyperbolicCurve, CriteriaSet } from './typeHelpers'
import { DepositParams } from './lpHelpers'
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import { Wallet } from 'ethers'
import { Deployment } from '../../deploy/deploymentConfig'
import { Otoken as OtokenInstance } from '../../typechain/'
import { CounterpartyDetails, PurchaseParams } from './purchaseHelpers'
import { SettlementRecord } from './postDeployActions/SettleAllExpiredOtokens'

export function parseUsdcAmount(dollars: BigNumberish): BigNumber {
  return BigNumber.from(dollars).mul(1e6)
}

export class AccountValue {
  constructor(public account: Wallet | SignerWithAddress | string, public value: BigNumber) {}
}

export enum ActionWithoutParams {
  MockOracle,
  Whitelist,
  CurveAndCriteriaActions,
}

type PostDeployActionSingleResult =
  | OtokenInstance
  | DepositParams
  | CurveCriteria
  | PurchaseParams
  | HyperbolicCurve
  | CriteriaSet
  | SettlementRecord
  | void
export type PostDeployActionResult = PostDeployActionSingleResult | PostDeployActionSingleResult[]

// eslint-disable-next-line  @typescript-eslint/no-explicit-any
type Constructor<T> = { new (...args: any[]): T }

class UnsettledOtoken {
  public constructor(public address: string, public expiry: number, public contributors: CounterpartyDetails[] = []) {}
}

export class PostDeployActionsResults {
  private results: PostDeployActionSingleResult[] = []

  // map from otoken address to otoken properties
  private unsettledOtokens: Record<string, UnsettledOtoken> = {}

  // Add a post-deploy action result to our state
  public async push(res: PostDeployActionResult): Promise<void> {
    if (Array.isArray(res)) {
      for (const r of res) {
        this._push(r)
      }
    } else {
      this._push(res)
    }
  }

  private async _push(res: PostDeployActionSingleResult): Promise<void> {
    if (res) {
      this.results.push(res)

      // New otokens are added to our unsettledOtokens map
      if (PostDeployActionsResults.isOtoken(res)) {
        this.unsettledOtokens[res.address] = new UnsettledOtoken(res.address, (await res.expiryTimestamp()).toNumber())
      }

      // New purchases update our unsettledOtokens map
      if (res instanceof PurchaseParams) {
        const otokenAddress = res.otoken.address
        if (!this.unsettledOtokens[otokenAddress]) {
          throw Error(`Purchase of unrecognised otoken: ${otokenAddress}`)
        }
        this.unsettledOtokens[otokenAddress].contributors = this.unsettledOtokens[otokenAddress].contributors.concat(
          res.sellers,
        )
      }

      // New settlements remove entries from our unsettledOtokens map
      if (res instanceof SettlementRecord) {
        delete this.unsettledOtokens[res.settledOtokenAddress]
      }
    }
  }

  private static typeGuard<T extends PostDeployActionSingleResult>(o: unknown, className: Constructor<T>): o is T {
    return o instanceof className
  }

  public allDataOfType<T extends PostDeployActionSingleResult>(className: Constructor<T>): T[] {
    const result: T[] = []

    for (const r of this.results) {
      if (PostDeployActionsResults.typeGuard(r, className)) result.push(<T>r)
    }

    return result
  }

  public mostRecentDatumOfType<T extends PostDeployActionSingleResult>(className: Constructor<T>): T | undefined {
    for (const r of this.results.slice().reverse()) {
      if (PostDeployActionsResults.typeGuard(r, className)) return r
    }
  }

  private static isOtoken(o: unknown): o is OtokenInstance {
    return (o as OtokenInstance).expiryTimestamp !== undefined && (o as OtokenInstance).isPut !== undefined
  }

  public async unsettledExpiredOtokens(): Promise<UnsettledOtoken[]> {
    return this.unsettledOtokensExpiringBefore((await ethers.provider.getBlock('latest')).timestamp)
  }

  // If no timestamp, all unsettled otokens are returned
  public async unsettledOtokensExpiringBefore(timestamp?: number): Promise<UnsettledOtoken[]> {
    const result: UnsettledOtoken[] = []
    for (const t in this.unsettledOtokens) {
      if (!timestamp || this.unsettledOtokens[t].expiry < timestamp) {
        result.push(this.unsettledOtokens[t])
      }
    }
    return result
  }
}

export interface PostDeployAction {
  executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult>
}

// N.B. depl may be updated by some post deploy actions
export async function executePostDeployActions(
  actions: PostDeployAction[],
  depl: Deployment,
  printProgress = false,
): Promise<void> {
  printProgress && console.log(`Executing ${actions.length} Post-Deployment Actions (PDAs)...`)
  const digits = actions.length.toString().length
  const pdaHistory = new PostDeployActionsResults()
  for (let i = 0; i < actions.length; i++) {
    printProgress &&
      process.stdout.write(`PDA_${(i + 1).toLocaleString(undefined, { minimumIntegerDigits: digits })}: `)
    await pdaHistory.push(await actions[i].executePostDeployAction(depl, pdaHistory, printProgress))
    await depl.persist()
  }
  printProgress && console.log(`${actions.length}/${actions.length} post-deploy actions complete.`)
}

export interface CriteriaAndCriteriaSets {
  criteria: CurveCriteria[]
  criteriaSets: CriteriaSet[]
}

// Generator functions are used to generate new data to be deployed
export type CriteriaGenerator = { (underlying: string, collateral: string): CriteriaAndCriteriaSets }
export type CurveGenerator = { (): HyperbolicCurve[] }

export interface OtokenParams {
  underlyingAsset: string
  strikeAsset: string
  collateralAsset: string
  strikePrice: BigNumber
  expiry: BigNumberish
  isPut: boolean
}
