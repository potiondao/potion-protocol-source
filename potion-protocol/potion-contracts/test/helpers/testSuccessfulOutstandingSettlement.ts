import { BigNumber } from 'ethers'
import { expect } from 'chai'

import { OutstandingSettlementTestCase } from '../../scripts/lib/purchaseHelpers'
import { createScaledNumber as scaleNum } from '../helpers/OpynUtils'
import { TestContracts } from './testSetup'

export default async (
  { potionLiquidityPool, oracle, weth, usdc }: TestContracts,
  tc: OutstandingSettlementTestCase,
): Promise<void> => {
  const lpTotalBalancesBefore: BigNumber[] = []
  const lpLockedBalancesBefore: BigNumber[] = []

  for (const pot of tc.redistributeToPools) {
    lpTotalBalancesBefore.push(await potionLiquidityPool.lpTotalAmount(pot.lp, pot.poolId))
    lpLockedBalancesBefore.push(await potionLiquidityPool.lpLockedAmount(pot.lp, pot.poolId))
  }

  const expiry = (await tc.otoken.expiryTimestamp()).toNumber()
  const scaledETHPrice = scaleNum(tc.expiryPriceUnderlyingInDollars)
  const scaledUSDCPrice = scaleNum(1)

  await oracle.setExpiryPriceFinalizedAllPeiodOver(weth.address, expiry, scaledETHPrice, true)
  await oracle.setExpiryPriceFinalizedAllPeiodOver(usdc.address, expiry, scaledUSDCPrice, true)

  const expectedRefundsItems: BigNumber[] = []
  for (let i = 0; i < tc.redistributeToPools.length; i++) {
    const expectedRefund = await potionLiquidityPool.outstandingSettlement(tc.otoken.address, tc.redistributeToPools[i])

    expectedRefundsItems.push(expectedRefund)

    expect(expectedRefund, `expectedRefund[${i}]`).to.equal(0)
  }
}
