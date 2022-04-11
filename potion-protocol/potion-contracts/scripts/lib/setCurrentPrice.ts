import { Deployment } from '../../deploy/deploymentConfig'
import { createScaledNumber as scaleNum } from '../../test/helpers/OpynUtils'

export async function setPrice(tokenAddress: string, priceInDollars: number): Promise<void> {
  const depl = await Deployment.getConfig()
  const mockOracle = await depl.mockedOracle()

  // Set price for underlying
  const trx = await mockOracle.setRealTimePrice(tokenAddress, scaleNum(priceInDollars))
  await trx.wait()
  console.log(` - Token (${tokenAddress}) price set to $${priceInDollars}`)
}
