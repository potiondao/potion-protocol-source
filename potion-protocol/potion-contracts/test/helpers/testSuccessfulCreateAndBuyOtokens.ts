import { CreateAndPurchaseParams } from '../../scripts/lib/purchaseHelpers'
import { ethers } from 'hardhat'
import { TestContracts } from './testSetup'
import { Otoken as OtokenInstance } from '../../typechain'
import { BigNumber } from 'ethers'
import { expect } from 'chai'

export default async (
  { potionLiquidityPool, otokenFactory }: TestContracts,
  tc: CreateAndPurchaseParams,
): Promise<void> => {
  // Transact on chain
  const receipt = await potionLiquidityPool
    .connect(tc.buyer)
    .createAndBuyOtokens(
      tc.underlyingAsset,
      tc.strikeAsset,
      tc.collateralAsset,
      tc.strikePrice,
      tc.expiry,
      tc.isPut,
      tc.sellers,
      ethers.constants.MaxUint256,
    )

  const otokenAddr = await otokenFactory.getOtoken(
    tc.underlyingAsset,
    tc.strikeAsset,
    tc.collateralAsset,
    tc.strikePrice,
    tc.expiry,
    tc.isPut,
  )
  const totalOptionAmount = tc.sellers.reduce((acc, val) => acc.add(val.orderSizeInOtokens), BigNumber.from(0))
  const OtokenInstanceFactory = await ethers.getContractFactory('Otoken')
  const otoken = (await OtokenInstanceFactory.attach(otokenAddr)) as OtokenInstance

  expect(await otoken.totalSupply(), 'totalSupply').to.equal(totalOptionAmount)
  expect(await otoken.balanceOf(tc.buyer.address), 'optBal').to.equal(totalOptionAmount)

  // events
  expect(receipt).to.emit(potionLiquidityPool, 'OptionsBought').to.emit(potionLiquidityPool, 'OptionsSold')
}
