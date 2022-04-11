import { Deployment } from '../../../deploy/deploymentConfig'
import { PostDeployAction, PostDeployActionsResults } from '../postDeploy'

export class SettlementRecord {
  public constructor(public settledOtokenAddress: string) {}
}

export class SettleAllExpiredOtokens implements PostDeployAction {
  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<SettlementRecord[]> {
    const results: SettlementRecord[] = []
    printProgress && console.log(`Settling expired otokens`)
    const otokens = await dataAlreadyDeployed.unsettledExpiredOtokens()
    printProgress && console.log(` - Found ${otokens.length} expired otokens`)
    const potionLiquidityPool = await depl.potionLiquidityPool()

    for (const o of otokens) {
      if (o.contributors.length > 0) {
        printProgress &&
          console.log(` - Settling otoken at ${o.address} with expiry ${new Date(o.expiry * 1000).toISOString()}`)
        let trx = await potionLiquidityPool.settleAfterExpiry(o.address)
        await trx.wait()
        printProgress &&
          console.log(` - Redistributing funds to ${o.contributors.map((c) => `${c.lp}[${c.poolId}]`).join()}`)
        trx = await potionLiquidityPool.redistributeSettlement(o.address, o.contributors)
        await trx.wait()
      } else {
        printProgress && console.log(` - No sales of otoken at ${o.address}; skipping`)
      }

      // Either we have settled all LPs, or there were no LPs to settle. Either way, this otoken is no longer active
      results.push(new SettlementRecord(o.address))
    }
    return results
  }
}
