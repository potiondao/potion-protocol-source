import { ethers } from 'hardhat'
import { Deployment } from '../../deploy/deploymentConfig'
import { createScaledNumber as scaleNum } from '../../test/helpers/OpynUtils'

import { Otoken as OtokenInstance } from '../../typechain'

export async function setExpiryPrice(otokenAddress: string, priceInDollars: number): Promise<void> {
  const depl = await Deployment.getConfig()
  const mockOracle = await depl.mockedOracle()
  const OtokenInstanceFactory = await ethers.getContractFactory('Otoken')

  const otoken = (await OtokenInstanceFactory.attach(otokenAddress)) as OtokenInstance
  const stablePriceInDollars = 1

  const [collateralAsset, underlyingAsset, strikeAsset, , expiryTimestamp] = await otoken.getOtokenDetails()
  console.log(`Updating prices in Oracle ${mockOracle.address} for timestamp ${expiryTimestamp}`)

  // Set price for underlying
  let trx = await mockOracle.setExpiryPriceFinalizedAllPeiodOver(
    underlyingAsset,
    expiryTimestamp,
    scaleNum(priceInDollars),
    true,
  )
  await trx.wait()
  console.log(` - Underlying asset (${underlyingAsset}) set to $${priceInDollars}`)

  // Set price for strike asset. Opyn's Controller expects the dispute period to be marked as over even for stable assets. Might be a bug? If tht code is changed this call will not be necessary.
  trx = await mockOracle.setExpiryPriceFinalizedAllPeiodOver(
    strikeAsset,
    expiryTimestamp,
    scaleNum(stablePriceInDollars),
    true,
  )
  await trx.wait()
  console.log(` - Strike asset (${strikeAsset}) set to $${stablePriceInDollars}`)

  // Set price for collateral asset. Opyn's Controller expects the dispute period to be marked as over even for stable assets. Might be a bug? If tht code is changed this call will not be necessary.
  trx = await mockOracle.setExpiryPriceFinalizedAllPeiodOver(
    collateralAsset,
    expiryTimestamp,
    scaleNum(stablePriceInDollars),
    true,
  )
  await trx.wait()
  console.log(` - Collateral asset (${collateralAsset}) set to $${stablePriceInDollars}`)
}
