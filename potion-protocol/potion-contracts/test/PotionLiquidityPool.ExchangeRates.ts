import { ethers } from 'hardhat'
import { expect } from 'chai'
import { BigNumber, BigNumberish, ContractFactory } from 'ethers'
import {
  MockERC20,
  MockOracle,
  Otoken as OtokenInstance,
  OtokenFactory,
  PotionLiquidityPool,
  Whitelist,
  AddressBook,
} from '../typechain'
import { createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { deployTestContracts, getTestOtoken, TestContracts } from './helpers/testSetup'
import BigDecimal from 'bignumber.js'

// Don't use exponential notation or it screws with conversions to BigNumber
BigDecimal.config({ EXPONENTIAL_AT: 50 })

const OTOKEN_DECIMALS = 8
const OTOKEN_WEI_PER_OTOKEN = 1e8

const strikePriceToHumanReadable = (input: BigNumberish, decimals: BigNumberish): number => {
  const inp = new BigDecimal(BigNumber.from(input).toString())
  const shift = Math.abs(BigNumber.from(decimals).toNumber()) * -1
  return inp.shiftedBy(shift).toNumber()
}

// To shift right, supply a negative value for placesLeft
const shift = (input: BigNumberish, placesLeft: number): BigNumber => {
  const inp = new BigDecimal(BigNumber.from(input).toString())
  const resultIntAsString = inp.shiftedBy(placesLeft).integerValue().toString()
  return BigNumber.from(resultIntAsString)
}

// Tests functions that use the Oracle to convert some value denominated in one asset to an
// equivalent value of some other asset.
describe('PotionLiquidityPool (Exchange Rates)', function () {
  let MockERC20Factory: ContractFactory

  let testContracts: TestContracts
  let otokenFactory: OtokenFactory
  let potionLiquidityPool: PotionLiquidityPool
  let addressBook: AddressBook
  let whitelist: Whitelist

  // oracle module mock
  let oracle: MockOracle

  let usdc: MockERC20
  let weth: MockERC20

  // nickleCoin is a token I just made up
  // It's stable value is 5c, and it uses 18 decimals
  let nickleCoin: MockERC20

  const lowerStrikeInDollars = 210 // $ per ETH
  const middleStrikeInDollars = 1000 // $ per ETH
  const higherStrikeInDollars = 14800 // $ per ETH
  const nickleCoinStrikeInDollars = 500 // $ per ETH
  const strikePricesInDollars = [
    lowerStrikeInDollars,
    middleStrikeInDollars,
    higherStrikeInDollars,
    nickleCoinStrikeInDollars,
  ]

  const otokens: OtokenInstance[] = []
  const numOptions = 4

  before('set up contracts', async () => {
    MockERC20Factory = await ethers.getContractFactory('MockERC20')
    testContracts = await deployTestContracts()
    ;({ addressBook, potionLiquidityPool, usdc, weth, oracle, otokenFactory, whitelist } = testContracts)

    // The proper whitelist contract no longer (as of 2021-05) allows separate collateral and strike tokens for puts
    // But we already had a test for that, and it's a useful test of exchange rate calculations, so for these tests
    // we use a MockWhitelist
    const MockWhitelistFactory = await ethers.getContractFactory('MockWhitelistModule')
    whitelist = (await MockWhitelistFactory.deploy()) as Whitelist
    await whitelist.whitelistCollateral(usdc.address)
    await whitelist.whitelistCollateral(weth.address)
    await whitelist.whitelistProduct(weth.address, usdc.address, usdc.address, true)
    await whitelist.whitelistProduct(weth.address, usdc.address, weth.address, false)
    await addressBook.setWhitelist(whitelist.address)

    // Dummy up Nicklecoin and whitelist the relevant products
    nickleCoin = (await MockERC20Factory.deploy('Nickle', 'NICKL', 18)) as MockERC20
    await oracle.setRealTimePrice(nickleCoin.address, scaleNum(0.05))
    await whitelist.whitelistCollateral(nickleCoin.address)
    await whitelist.whitelistProduct(weth.address, usdc.address, nickleCoin.address, true)

    // Test some otokens where strike and collateral both = USDC
    for (let i = 0; i < 3; i++) {
      const { put } = await getTestOtoken({
        otokenFactory,
        strikeAsset: usdc.address,
        underlyingAsset: weth.address,
        deploy: true,
        strikeInDollars: strikePricesInDollars[i],
      })
      otokens.push(put)
    }

    // Test an otoken where strike=USDC and collateral = nickleCoin
    for (let i = 3; i < strikePricesInDollars.length; i++) {
      const { put } = await getTestOtoken({
        otokenFactory,
        strikeAsset: usdc.address,
        underlyingAsset: weth.address,
        deploy: true,
        strikeInDollars: strikePricesInDollars[i],
        collateralAsset: nickleCoin.address,
      })
      otokens.push(put)
    }

    // Check that we have created the same number of options expected by our test-generation loops
    expect(otokens.length, 'number of test otokens').to.equal(numOptions)
  })

  describe('collateralNeededForPuts', async () => {
    const ONE_OTOKEN = scaleNum(1)
    const PI_OTOKENS = BigNumber.from(314159265)
    const MANY_OTOKENS = scaleNum(98765)
    const OTOKEN_QUANTITIES = [ONE_OTOKEN, PI_OTOKENS, MANY_OTOKENS]

    // One consequence of this method of test generation is that anything created asyn in the before block cannot be accessed
    // outside of the `it` test definitions.
    // E.g. none of the `for` loop code can access the `otokens` list or its length, hence the hacky `numOptions` constant.
    for (let j = 0; j < OTOKEN_QUANTITIES.length; j++) {
      const qty = OTOKEN_QUANTITIES[j]
      for (let i = 0; i < numOptions; i++) {
        it(`strike=${strikePricesInDollars[i]},qty=${qty}`, async () => {
          const otoken = otokens[i]

          // otoken.strikePrice() has 8 decimals. We want the answer with however many decimals our collateral token uses
          const strikePriceWith8Decimals = await otoken.strikePrice()
          const strikePriceInDollars = strikePriceToHumanReadable(strikePriceWith8Decimals, 8)

          const collateralToken = MockERC20Factory.attach(await otoken.collateralAsset())
          const collateralDecimals = await collateralToken.decimals()
          const strikeToken = MockERC20Factory.attach(await otoken.strikeAsset())

          // When multiplying by otoken quantity in wei, we divide by OTOKEN_WEI_PER_OTOKEN to use otoken quantity in human units
          const expectedCollateralInUsdWith8Decimals = strikePriceWith8Decimals.mul(qty).div(OTOKEN_WEI_PER_OTOKEN)

          if (collateralToken.address === strikeToken.address) {
            // Same token, so we need only adjust the number of decimals up or down from the 8 used in the strike price
            const shiftPlacesLeft = collateralDecimals - OTOKEN_DECIMALS
            const expectedVal = shift(expectedCollateralInUsdWith8Decimals, shiftPlacesLeft)
            expect(await potionLiquidityPool.collateralNeededForPuts(otoken.address, qty)).to.equal(expectedVal)
          } else {
            // Strike asset is different from collateral asset
            // We now need to take into account the exchange rate between these assets
            expect(strikeToken.address).to.equal(usdc.address)
            expect(collateralToken.address).to.equal(nickleCoin.address)

            const NICKELS_PER_DOLLAR = 20
            const strikePriceInNumberOfNickels = BigNumber.from(NICKELS_PER_DOLLAR).mul(strikePriceInDollars)
            const strikePriceInNicklecoinWei = shift(strikePriceInNumberOfNickels, await nickleCoin.decimals())

            // When multiplying by otoken quantity in wei, we divide by OTOKEN_WEI_PER_OTOKEN to use otoken quantity in human units
            const totalCollateralInNickelcoinWei = strikePriceInNicklecoinWei.mul(qty).div(OTOKEN_WEI_PER_OTOKEN)
            const result = await potionLiquidityPool.collateralNeededForPuts(otoken.address, qty)
            expect(result).to.equal(totalCollateralInNickelcoinWei)
          }
        })
      }
    }
  })

  describe('percentStrike', async () => {
    const ETH_SPOT_PRICES = [300, 250, 120, 11, 99750]

    // One consequence of this method of test generation is that anything created asyn in the before block cannot be accessed
    // outside of the `it` test definitions.
    // E.g. none of the `for` loop code can access the `otokens` list or its length, hence the hacky `numOptions` constant.
    for (let j = 0; j < ETH_SPOT_PRICES.length; j++) {
      const ethSpotInDollars = ETH_SPOT_PRICES[j]
      for (let i = 0; i < numOptions; i++) {
        it(`strike=${strikePricesInDollars[i]},spot=$${ethSpotInDollars}`, async () => {
          await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotInDollars))
          await oracle.setRealTimePrice(usdc.address, scaleNum(1))
          const otoken = otokens[i]
          const strikeInDollars = strikePriceToHumanReadable(await otoken.strikePrice(), 8)
          const expectedPercent = Math.ceil((100 * strikeInDollars) / ethSpotInDollars)
          const result = await potionLiquidityPool.percentStrike(otoken.address)
          expect(result).to.equal(expectedPercent)
        })
        it(`[USDC devalued] strike=${strikePricesInDollars[i]},spot=$${ethSpotInDollars}`, async () => {
          // Test what happens if USDC is suddenly worth only 50cents
          // The real value of hte underlying is unchanged, but the real value of the strike price is halved
          // So percentStrike should be half of what it was in the above test
          await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotInDollars))
          await oracle.setRealTimePrice(usdc.address, 5e7)
          const otoken = otokens[i]
          const strikeInUSDC = strikePriceToHumanReadable(await otoken.strikePrice(), 8)
          const strikeInDollars = strikeInUSDC / 2
          const expectedPercent = Math.ceil((100 * strikeInDollars) / ethSpotInDollars)
          const result = await potionLiquidityPool.percentStrike(otoken.address)
          expect(result).to.equal(expectedPercent)
        })
      }
    }
  })
})
