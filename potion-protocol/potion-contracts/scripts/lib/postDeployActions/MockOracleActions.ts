import { ethers } from 'hardhat'
import { MockOracle, MarginCalculator } from '../../../typechain'
import { createScaledNumber as scaleNum } from '../../../test/helpers/OpynUtils'
import { Deployment } from '../../../deploy/deploymentConfig'
import { PostDeployAction, PostDeployActionsResults } from '../postDeploy'

export class InitializeMockOracle implements PostDeployAction {
  public constructor(public initialEthPriceInDollars: number) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    printProgress && console.log(`Initializing a mock oracle`)
    if (!depl.sampleUnderlyingTokenAddress) {
      throw new Error('Cannot mock prices in oracle without sample underlying token address')
    }
    // Deploy a mock oracle and set asset prices (without prices, purchases cannot be made)
    const MockOracleFactory = await ethers.getContractFactory('MockOracle')
    const mockOracle = (await MockOracleFactory.deploy()) as MockOracle
    await mockOracle.deployed()
    const addressbook = await depl.addressBook()
    let trx = await addressbook.setOracle(mockOracle.address)
    await trx.wait()
    printProgress && console.log(` - Mock Oracle deployed to ${await addressbook.getOracle()}`)
    trx = await mockOracle.setRealTimePrice(depl.sampleUnderlyingTokenAddress, scaleNum(this.initialEthPriceInDollars))
    await trx.wait()
    trx = await mockOracle.setStablePrice(depl.collateralTokenAddress, scaleNum(1))
    await trx.wait()

    // After deploying any new Oracle, we must redeploy a new MarginCalculator
    const MarginCalculatorFactory = await ethers.getContractFactory('MarginCalculator')
    const marginCalculator = (await MarginCalculatorFactory.deploy(mockOracle.address)) as MarginCalculator
    await marginCalculator.deployed()
    trx = await addressbook.setMarginCalculator(marginCalculator.address)
    await trx.wait()

    // We need to kick the controller to pick up the new oracle address
    printProgress && console.log(` - Updating controller to use new oracle`)
    const controller = await depl.controller()
    trx = await controller.refreshConfiguration()
    await trx.wait()
    depl.oracleIsMock = true
    printProgress && console.log(` - Mock oracle configured`)
  }
}

export class UpdateMockOraclePrices implements PostDeployAction {
  public constructor(public priceInDollars: number) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    if (!depl.sampleUnderlyingTokenAddress) {
      throw new Error('Cannot mock prices in oracle without sample underlying token address')
    }
    const otokens = await dataAlreadyDeployed.unsettledExpiredOtokens()
    if (otokens.length > 0) {
      printProgress &&
        console.log(
          `Setting mock oracle price to $${this.priceInDollars}, including expiry prices for otokens: ${otokens
            .map((o) => o.address)
            .join()}`,
        )
    } else {
      printProgress && console.log(`Setting current mock oracle spot price to $${this.priceInDollars}`)
    }

    const mockOracle = await depl.mockedOracle()
    let trx = await mockOracle.setRealTimePrice(depl.sampleUnderlyingTokenAddress, scaleNum(this.priceInDollars))
    await trx.wait()

    for (const o of otokens) {
      printProgress &&
        console.log(
          ` - Setting expiry ${new Date(o.expiry * 1000).toISOString()} price for otoken ${
            o.address
          } (assuming assets ${depl.sampleUnderlyingTokenAddress} and ${depl.collateralTokenAddress})`,
        )

      trx = await mockOracle.setExpiryPriceFinalizedAllPeiodOver(
        depl.sampleUnderlyingTokenAddress,
        o.expiry,
        scaleNum(this.priceInDollars),
        true,
      )
      await trx.wait()

      // Opyn's Controller expects the dispute period to be marked as over even for stable assets. Might be a bug? If tht code is changed this call will not be necessary.
      trx = await mockOracle.setExpiryPriceFinalizedAllPeiodOver(
        depl.collateralTokenAddress,
        o.expiry,
        scaleNum(1),
        true,
      )
      await trx.wait()
    }
  }
}
