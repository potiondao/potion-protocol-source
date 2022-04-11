import { network, ethers, upgrades } from 'hardhat'
import { getConfig } from '../deploy/deploymentConfig'

async function main() {
  const deploymentConfig = await getConfig()
  if (!deploymentConfig.potionLiquidityPool) {
    throw Error(`No deployed instance available to upgrade on network ${network.name}`)
  }

  const LatestPotionLiquidityPoolFactory = await ethers.getContractFactory('PotionLiquidityPool')
  const prepResult = await upgrades.prepareUpgrade(
    deploymentConfig.potionLiquidityPool,
    LatestPotionLiquidityPoolFactory,
  )
  console.log(`Latest logic is deployed at: ${prepResult}`)
  console.log(
    `Upgrading PotionLiquidityPool contract at ${deploymentConfig.potionLiquidityPool} to point at latest logic...`,
  )
  // const newProxyInterface = await upgrades.upgradeProxy( deploymentConfig.potionLiquidityPool, LatestPotionLiquidityPoolFactory, )
  await upgrades.upgradeProxy(deploymentConfig.potionLiquidityPool, LatestPotionLiquidityPoolFactory)
  console.log('Done')

  // No need to persist updated config because the address of the PotionLiquidityPool proxy has not changed.
  // The underlying implementation address will have been updated in .openzeppelin/<network>.json
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })
