import { Deployment } from '../../../deploy/deploymentConfig'
import { PostDeployAction, PostDeployActionsResults } from '../postDeploy'

export class WhitelistCollateral implements PostDeployAction {
  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    printProgress && console.log(`Whitelisting collateral: ${depl.collateralTokenAddress}`)
    // Whitelist our products
    const whitelist = await depl.whitelist()
    const trx = await whitelist.whitelistCollateral(depl.collateralTokenAddress)
    await trx.wait()
  }
}
