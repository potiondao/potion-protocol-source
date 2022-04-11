import { SettleTestCase } from '../../scripts/lib/purchaseHelpers'
import { ethers, waffle } from 'hardhat'
import { TestContracts } from './testSetup'
import { BigNumber } from 'ethers'
import { expect } from 'chai'
import { createScaledNumber as scaleNum } from '../helpers/OpynUtils'
const provider = waffle.provider

export default async (
  { potionLiquidityPool, usdc, weth, oracle }: TestContracts,
  tc: SettleTestCase,
): Promise<void> => {
  const startPoolBalance = await usdc.balanceOf(potionLiquidityPool.address)
  const lpTotalBalancesBefore: BigNumber[] = []
  const lpLockedBalancesBefore: BigNumber[] = []

  for (const pot of tc.redistributeToPools) {
    lpTotalBalancesBefore.push(await potionLiquidityPool.lpTotalAmount(pot.lp, pot.poolId))
    lpLockedBalancesBefore.push(await potionLiquidityPool.lpLockedAmount(pot.lp, pot.poolId))
  }

  const scaledETHPrice = scaleNum(tc.expiryPriceUnderlyingInDollars)
  const scaledUSDCPrice = scaleNum(1)

  const expiry = (await tc.otoken.expiryTimestamp()).toNumber()
  await oracle.setExpiryPriceFinalizedAllPeiodOver(weth.address, expiry, scaledETHPrice, true)
  await oracle.setExpiryPriceFinalizedAllPeiodOver(usdc.address, expiry, scaledUSDCPrice, true)

  const now = (await ethers.provider.getBlock('latest')).timestamp

  if (now < expiry) {
    await provider.send('evm_setNextBlockTimestamp', [expiry + 2])
    await provider.send('evm_mine', [])
  }

  if (tc.doSettle) {
    const receipt = await potionLiquidityPool.settleAfterExpiry(tc.otoken.address)
    expect(receipt).to.emit(potionLiquidityPool, 'OptionSettled')
  }

  let totalOtokensBought = BigNumber.from(0)
  for (const value of tc.contributions.values()) {
    totalOtokensBought = totalOtokensBought.add(value)
  }

  // The pool gets back the lower of the strike price and the price at expiry
  expect(await usdc.balanceOf(potionLiquidityPool.address), 'endPoolBalance').to.equal(
    // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
    startPoolBalance.add(
      totalOtokensBought.mul(Math.min(tc.expiryPriceUnderlyingInDollars, tc.strikePriceInDollars)).div(100),
    ),
  )
  const expectedRefundsItems: BigNumber[] = []
  for (let i = 0; i < tc.redistributeToPools.length; i++) {
    const expectedRefund = await potionLiquidityPool.outstandingSettlement(tc.otoken.address, tc.redistributeToPools[i])
    expectedRefundsItems.push(expectedRefund)
    const expectedContribution = tc.contributions.get(tc.redistributeToPools[i].key) || BigNumber.from(0)
    // console.log( `Contribution from ${String(tc.redistributeToPools[i].key)} ${ tc.contributions.has(tc.redistributeToPools[i].key) ? `exists` : `does not exist` } and is ${expectedContribution}`, )

    // The expected refund is the value of the unused collateral, which is derived from the spot price of
    // the underlying
    expect(expectedRefund, `expectedRefund[${i}]`).to.equal(
      expectedContribution
        .mul(Math.min(tc.expiryPriceUnderlyingInDollars, tc.strikePriceInDollars))
        // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
        .div(100),
    )
  }

  if (tc.redistributeToPools.length > 0) {
    const receipt = await potionLiquidityPool.redistributeSettlement(tc.otoken.address, tc.redistributeToPools)

    for (let i = 0; i < tc.redistributeToPools.length; i++) {
      const { lp, poolId } = tc.redistributeToPools[i]
      expect(receipt)
        .to.emit(potionLiquidityPool, 'OptionSettlementDistributed')
        .withArgs(tc.otoken.address, lp, poolId, expectedRefundsItems[i])
    }
  }

  for (let i = 0; i < tc.redistributeToPools.length; i++) {
    const expectedContribution = tc.contributions.get(tc.redistributeToPools[i].key) || BigNumber.from(0)
    const pot = tc.redistributeToPools[i]
    const beforeTotal = lpTotalBalancesBefore[i]
    const beforeLocked = lpLockedBalancesBefore[i]
    const afterTotal = await potionLiquidityPool.lpTotalAmount(pot.lp, pot.poolId)
    const afterLocked = await potionLiquidityPool.lpLockedAmount(pot.lp, pot.poolId)
    // console.log( `pool balance of LP ${i} was ${beforeTotal.toString()} and is now ${afterTotal.toString()} (diff = ${afterTotal .sub(beforeTotal) .toString()})`, )
    // console.log( `locked pool balance of LP ${i} was ${beforeLocked.toString()} and is now ${afterLocked.toString()} (diff = ${afterLocked .sub(beforeLocked) .toString()}; expected ${tokenAmount8.mul(higherStrikeInDollars)} or ${tokenAmount55.mul(higherStrikeInDollars)})`, )

    // The TOTAL collateral should be reduced by the collateral that was NOT recovered (i.e. the value of options at expiry)
    // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
    const optionValueAtExpiry = BigNumber.from(Math.max(tc.strikePriceInDollars - tc.expiryPriceUnderlyingInDollars, 0))

    expect(afterTotal, `afterTotal[${i}]`).to.equal(
      beforeTotal.sub(
        expectedContribution
          .mul(optionValueAtExpiry)
          // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
          .div(100),
      ),
    )

    // The LOCKED collateral should be reduced by the full amount of collateral that was deposited
    // None of it should be locked any more (some may be unlocked and returned, and some may have been sent to the option holder)
    // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
    expect(afterLocked, `afterLocked[${i}]`).to.equal(
      // We divide by 100 because otokens use 8 decimal places and usdc only uses 6
      beforeLocked.sub(expectedContribution.mul(tc.strikePriceInDollars).div(100)),
    )
  }
}
