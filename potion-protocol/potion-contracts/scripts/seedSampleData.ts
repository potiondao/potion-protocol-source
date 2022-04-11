import { Deployment } from '../deploy/deploymentConfig'
import { PostDeployAction, executePostDeployActions } from './lib/postDeploy'
import { DeployCurves, DeployCriteriaAndCriteriaSets } from './lib/postDeployActions/CurveAndCriteriaActions'
import { DeploySampleUnderlyingToken } from './lib/postDeployActions/DeploySampleUnderlyingToken'
import { WhitelistCollateral } from './lib/postDeployActions/WhitelistCollateral'

async function main() {
  const deploymentConfig = await Deployment.getConfig()
  const actions: PostDeployAction[] = []
  if (!deploymentConfig.sampleUnderlyingTokenAddress) {
    actions.push(new WhitelistCollateral())
    actions.push(new DeploySampleUnderlyingToken())
  }

  console.log(`Deploying sample data to PotionLiquidityPool contract at ${deploymentConfig.potionLiquidityPoolAddress}`)
  actions.push(new DeployCurves())
  actions.push(new DeployCriteriaAndCriteriaSets())
  await executePostDeployActions(actions, deploymentConfig, true)
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })
