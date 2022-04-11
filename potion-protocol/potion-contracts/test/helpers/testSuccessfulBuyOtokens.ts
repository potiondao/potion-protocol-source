import { ethers } from 'hardhat'
import { PurchaseParams } from '../../scripts/lib/purchaseHelpers'
import { TestContracts } from './testSetup'
import { BigNumber } from 'ethers'
import { expect } from 'chai'

export default async ({ potionLiquidityPool, usdc, marginPool }: TestContracts, tc: PurchaseParams): Promise<void> => {
  // Note the state BEFORE our purchase transaction; we will test that the deltas at the end of the test are as expected
  const startTotalSupply = await tc.otoken.totalSupply()
  const startOptBal = await tc.otoken.balanceOf(tc.buyer.address)
  const startPoolBalance = await usdc.balanceOf(potionLiquidityPool.address)
  const startOpynCollateralBalance = await usdc.balanceOf(marginPool.address)

  // Figure out the expected deltas
  // TODO: we should do collateral and premium calculations off chain, in typescript, and compare the results to on-chain results
  // That could be part of this test, but is probably better done as separate tests of the collateralNeededForPuts and premiumForLp functions
  const collateralAmountsNeeded = []
  const startLpLockedAmounts = []
  const startLpTotalAmounts = []
  let totalCollateralNeeded = BigNumber.from(0)

  const { totalPremiumInCollateralTokens, perLpPremiumsInCollateralTokens } = await potionLiquidityPool.premiums(
    tc.otoken.address,
    tc.sellers,
  )
  for (const seller of tc.sellers) {
    const collateralAmount = await potionLiquidityPool.collateralNeededForPuts(
      tc.otoken.address,
      seller.orderSizeInOtokens,
    )
    collateralAmountsNeeded.push(collateralAmount)
    totalCollateralNeeded = totalCollateralNeeded.add(collateralAmount)

    startLpLockedAmounts.push(await potionLiquidityPool.lpLockedAmount(seller.lp, seller.poolId))
    startLpTotalAmounts.push(await potionLiquidityPool.lpTotalAmount(seller.lp, seller.poolId))
  }
  // console.log( `[startLpTotalAmounts],(perLpPremiumsInCollateralTokens),{collateralAmountsNeeded},startOptBal,<startLpLockedAmounts>,startPoolBalance,startOpynCollateralBalance,[startLpTotalAmounts]`, )
  // console.log( `[${startLpTotalAmounts.toString()}],(${perLpPremiumsInCollateralTokens.toString()}),{${collateralAmountsNeeded.toString()}},${startOptBal.toString()},<${startLpLockedAmounts.toString()}>,${startPoolBalance.toString()},${startOpynCollateralBalance.toString()},[${startLpTotalAmounts}]`, )
  // console.log(`startPoolBalance,totalPremiumInCollateralTokens,totalCollateralNeeded`)
  // console.log( `${startPoolBalance.toString()},${totalPremiumInCollateralTokens.toString()},${totalCollateralNeeded.toString()}`, )

  // Transact on chain
  const receipt = await potionLiquidityPool
    .connect(tc.buyer)
    .buyOtokens(tc.otoken.address, tc.sellers, ethers.constants.MaxUint256)

  // Now compare the on-chain deltas to our expectations
  const totalOptionAmount = tc.sellers.reduce((acc, val) => acc.add(val.orderSizeInOtokens), BigNumber.from(0))
  expect(await tc.otoken.totalSupply(), 'totalSupply').to.equal(startTotalSupply.add(totalOptionAmount))
  expect(await tc.otoken.balanceOf(tc.buyer.address), 'optBal').to.equal(startOptBal.add(totalOptionAmount))
  expect(await usdc.balanceOf(marginPool.address), 'endOpynCollateralBalance').to.equal(
    startOpynCollateralBalance.add(totalCollateralNeeded),
  )
  expect(await usdc.balanceOf(potionLiquidityPool.address), 'endPoolBalance').to.equal(
    startPoolBalance.add(totalPremiumInCollateralTokens).sub(totalCollateralNeeded),
  )
  for (let i = 0; i < tc.sellers.length; i++) {
    expect(
      await potionLiquidityPool.lpLockedAmount(tc.sellers[i].lp, tc.sellers[i].poolId),
      'endLpLockedAmount',
    ).to.equal(startLpLockedAmounts[i].add(collateralAmountsNeeded[i]))
    expect(
      await potionLiquidityPool.lpTotalAmount(tc.sellers[i].lp, tc.sellers[i].poolId),
      'endLpTotalAmount',
    ).to.equal(startLpTotalAmounts[i].add(perLpPremiumsInCollateralTokens[i]))

    expect(receipt)
      .to.emit(potionLiquidityPool, 'OptionsBought')
      .withArgs(tc.buyer.address, tc.otoken.address, totalOptionAmount, totalPremiumInCollateralTokens)
      .to.emit(potionLiquidityPool, 'OptionsSold')
      .withArgs(
        tc.sellers[i].lp,
        tc.sellers[i].poolId,
        tc.otoken.address,
        tc.sellers[i].curveAs64x64.toKeccak256(),
        tc.sellers[i].orderSizeInOtokens,
        collateralAmountsNeeded[i],
        perLpPremiumsInCollateralTokens[i],
      )
  }
}
