import { AccountValue, PostDeployAction } from './lib/postDeploy'
import { BigNumber, BigNumberish } from 'ethers'

import { AllocateCollateralTokensFromFaucet } from './lib/postDeployActions/AllocateCollateralTokens'
import { Deployment } from '../deploy/deploymentConfig'
import { executePostDeployActions } from './lib/postDeploy'

function parseUsdcAmount(dollars: BigNumberish): BigNumber {
  return BigNumber.from(dollars).mul(1e6)
}

const EXTERNAL_COLLATERAL_ALLOCATIONS = [
  // Team
  new AccountValue('0x2c5eDB7F0EF80C7aBea2D2b7bF9Da96823Ec935d', parseUsdcAmount('1000000')), // Aur
  new AccountValue('0x46BD46A8C0DcB4Ca501c4A5624B1F09Ba86ff8F6', parseUsdcAmount('1000000')), // Nim
  new AccountValue('0x614B7f7Ed8E93260B6EA33BB081073036F73F9E9', parseUsdcAmount('1000000')), // Eds
  new AccountValue('0x0d7876a0b4e240FE5F09944A7cA87a90987c2274', parseUsdcAmount('1000000')), // Raz
  new AccountValue('0x09610ad200Ca80f8cC1B30f73AaA0e5408e27220', parseUsdcAmount('1000000')), // Alb
]

async function main() {
  const deploymentConfig = await Deployment.getConfig()
  const actions: PostDeployAction[] = []
  if (!deploymentConfig.collateralTokenAddress) {
    throw 'No collateral address for this network'
  }

  console.log(`Allocating collateral tokens (token address = ${deploymentConfig.collateralTokenAddress})...`)
  actions.push(new AllocateCollateralTokensFromFaucet(EXTERNAL_COLLATERAL_ALLOCATIONS))
  await executePostDeployActions(actions, deploymentConfig, true)
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error('ERROR:', error)
    process.exit(1)
  })
