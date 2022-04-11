import { waffle } from 'hardhat'
import { expect } from 'chai'
import { BigNumber, ethers, Wallet, utils } from 'ethers'
import { deployTestContracts, getTestOtoken, mintTokens, usdcDecimals } from './helpers/testSetup'
import { createTokenAmount, createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { PotionLiquidityPool, Otoken as OtokenInstance, CurveManager, MockERC20, MockOracle } from '../typechain'
import { CounterpartyDetails } from '../scripts/lib/purchaseHelpers'
import { CurveCriteria, HyperbolicCurve } from '../scripts/lib/typeHelpers'
import { deployDefaultCriteria } from '../scripts/lib/postDeployActions/CurveAndCriteriaActions'

const provider = waffle.provider
const test = it
const { formatUnits } = utils

/**
 * This set of tests check if the pricing code reacts correctly to receiving incorrect or corrupted input values.
 */
describe('CurvePricing', function () {
  const wallets = provider.getWallets()

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [potionBuyer1, potionLp1] = wallets

  const ETH_SPOT_PRICE_IN_DOLLARS = 250 // $ per ETH
  const lowerStrikeInDollars = 10 // $ per ETH
  const INITIAL_BUYER_BALANCE = createTokenAmount(50000000, usdcDecimals)
  const POOL_ID = 0

  let potionLiquidityPool: PotionLiquidityPool
  let singleLpSeller1: CounterpartyDetails
  let curveManager: CurveManager

  // @dev This test suite requires 10k in total liquidity and 0 locked liquidity before getting the premiums
  describe('Order Too Large (Total)', () => {
    const A = 1
    const B = 1
    const C = 1
    const D = 1

    const TOTAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)

    const curve = new HyperbolicCurve(A, B, C, D)

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria

    beforeEach(async () => {
      ;({ lowerStrikePut, criteria1, potionLiquidityPool } = await setupTests({
        curve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: ETH_SPOT_PRICE_IN_DOLLARS,
        lowerStrikeInDollars,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))
    })

    test('Calculate premiums', async () => {
      const orderSize = 1000
      const expectedPremiumResult = BigNumber.from('0x05ebcb4f4c')

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Order Too Large', async () => {
      const orderSize = 1000000
      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      await expect(potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])).to.be.revertedWith(
        'revert util calc: >100% locked',
      )
    })
  })

  // @dev This test suite requires 10k in total liquidity and 10k locked liquidity before getting the premiums
  describe('Order Too Large (Locked)', () => {
    const A = 1
    const B = 1
    const C = 1
    const D = 1

    const TOTAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)
    const TOTAL_LIQUIDITY_AFTER_LOCKING = createTokenAmount(10000, usdcDecimals) // Since users pay the same amount that is locked, it remains 10k
    const LOCKED_LIQUIDITY = createTokenAmount(5000, usdcDecimals)
    const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 1000

    const curve = new HyperbolicCurve(A, B, C, D)

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria

    beforeEach(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 5
      ;({ lowerStrikePut, criteria1, potionLiquidityPool } = await setupTests({
        curve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: ETH_SPOT_PRICE_IN_DOLLARS,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID), 'total amount incorrect').to.equal(
        TOTAL_LIQUIDITY_AFTER_LOCKING,
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID), 'locked amount incorrect').to.equal(
        LOCKED_LIQUIDITY,
      )
    })

    test('Order within limits', async () => {
      const orderSize = 1000
      const expectedPremiumResult = BigNumber.from(17611741435)

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Order Too Large', async () => {
      const orderSize = 6000
      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      await expect(potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])).to.be.revertedWith(
        'revert util calc: >100% locked',
      )
    })
  })

  describe('Locked Liquidity Too Large', () => {
    const A = 1
    const B = 1
    const C = 1
    const D = 1

    const curve = new HyperbolicCurve(A, B, C, D)

    // @dev This test case requires 10k in total liquidity and 5k locked liquidity before getting the premiums
    test('Order within limits', async () => {
      const INITIAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)

      const { lowerStrikePut, criteria1, potionLiquidityPool } = await setupTests({
        curve,
        initialLiquidity: INITIAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: ETH_SPOT_PRICE_IN_DOLLARS,
        lowerStrikeInDollars,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      })

      const LOCKED_LIQUIDITY = createTokenAmount(5000, usdcDecimals)
      const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 500

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      // double check balance is updated
      expect(
        await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID),
        'total liquidity after locking',
      ).to.equal(INITIAL_LIQUIDITY.add(totalPremiumInCollateralTokens))

      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID)).to.equal(LOCKED_LIQUIDITY)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)

      expect(
        await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID),
        'total liquidity after withdraw',
      ).to.equal(INITIAL_LIQUIDITY)
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID)).to.equal(LOCKED_LIQUIDITY)

      // get premiums
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(22596905)

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])
      expect(expectedPremium, "premiums don't match").to.equal(expectedPremiumResult)
    })

    // @dev This test case requires 10k in total liquidity and 20k locked liquidity before getting the premiums
    // Note: this case is not possible, so it will revert trying to decrease the total liquidity to 10k
    test('Locked liquidity too large', async () => {
      const INITIAL_LIQUIDITY = createTokenAmount(30000, usdcDecimals) // we need to add extra initial liquidity to be able to have 20k locked

      const { lowerStrikePut, criteria1, potionLiquidityPool } = await setupTests({
        curve,
        initialLiquidity: INITIAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: ETH_SPOT_PRICE_IN_DOLLARS,
        lowerStrikeInDollars,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      })

      const LOCKED_LIQUIDITY = createTokenAmount(20000, usdcDecimals)
      const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 2000

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // usdc balance LPpool
      // buy OTokens so we can have LOCKED_LIQUIDITY=20000 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      // usdc after balance LPpool

      // check current total liquidity is the initial deposit + totalPremiumInCollateralTokens
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID)).to.equal(
        INITIAL_LIQUIDITY.add(totalPremiumInCollateralTokens),
      )

      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID)).to.equal(LOCKED_LIQUIDITY)

      // trying to withdraw so we can have 10k in Liquidity (if possible)
      await expect(
        potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens.add(LOCKED_LIQUIDITY)),
      ).to.revertedWith('revert')
    })
  })

  // @dev The following tests are based in the [routing-simulator](https://github.com/potion-labs/routing-simulator/blob/mike-dev/templates/notebooks/TestCurve_Notebook.ipynb) notebook.
  describe('Premiums are calculated correctly', () => {
    const A = 0
    const B = 0
    const C = 0
    const D = 1

    const TOTAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)
    const TOTAL_LIQUIDITY_AFTER_LOCKING = createTokenAmount(10000, usdcDecimals) // Since users pay the same amount that is locked, it remains 10k
    const LOCKED_LIQUIDITY = createTokenAmount(5000, usdcDecimals)
    const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 50
    const SIMULATOR_SPOT_PRICE = 100
    const curve = new HyperbolicCurve(A, B, C, D)

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria

    before(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 100
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: SIMULATOR_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID), 'total amount incorrect').to.equal(
        TOTAL_LIQUIDITY_AFTER_LOCKING,
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID), 'locked amount incorrect').to.equal(
        LOCKED_LIQUIDITY,
      )
    })

    test('Curve [0, 0, 0, 1]', async () => {
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(100000000) // 100 % and six significant digits

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, curve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Curve [1, 0, 0, 1]', async () => {
      // update curve
      const NEW_A_VALUE = 1
      const newCurve = new HyperbolicCurve(NEW_A_VALUE, B, C, D)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(201000000) // 201 % and six significant digits

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Curve [1, 1, 0, 1]', async () => {
      // update curve
      const NEW_A_VALUE = 1
      const NEW_B_VALUE = 1
      const newCurve = new HyperbolicCurve(NEW_A_VALUE, NEW_B_VALUE, C, D)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(255851144) // 255 % and six significant digits

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Curve [1, 1, 1, 1]', async () => {
      // update curve
      const NEW_A_VALUE = 1
      const NEW_B_VALUE = 1
      const NEW_C_VALUE = 1
      const newCurve = new HyperbolicCurve(NEW_A_VALUE, NEW_B_VALUE, NEW_C_VALUE, D)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(227590786) // 227 % and six significant digits

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    test('Curve [0.2, 0.2, 0.3, 0.4]', async () => {
      // update curve
      const NEW_A_VALUE = 0.1
      const NEW_B_VALUE = 0.2
      const NEW_C_VALUE = 0.3
      const NEW_D_VALUE = 0.4

      const newCurve = new HyperbolicCurve(NEW_A_VALUE, NEW_B_VALUE, NEW_C_VALUE, NEW_D_VALUE)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = 1
      const expectedPremiumResult = BigNumber.from(50274767) // From Jupyter notebook 50.27476665024051 -> 50274766

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      expect(expectedPremium).to.equal(expectedPremiumResult)
    })

    const addAndSetNewCurve = async (newCurve: HyperbolicCurve) => {
      const curveHash = await curveManager.hashCurve(newCurve.asSolidityStruct())
      await curveManager.addCurve(newCurve.asSolidityStruct())
      await potionLiquidityPool.connect(potionLp1).setCurve(POOL_ID, curveHash)
    }
  })

  describe('Real world premiums are calculated correctly', () => {
    const PRECISION = 0.01 // +/- expected value
    const TOTAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)
    const TOTAL_LIQUIDITY_AFTER_LOCKING = createTokenAmount(10000, usdcDecimals) // Since users pay the same amount that is locked, it remains 10k
    const LOCKED_LIQUIDITY = createTokenAmount(5000, usdcDecimals)
    const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 12.5
    const SIMULATOR_SPOT_PRICE = 400
    const COLLATERAL_ORDER = 2500

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria
    const initialCurve = new HyperbolicCurve(0.000654, 2.529136, 22.279453, 0.001034)

    beforeEach(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 400
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve: initialCurve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: SIMULATOR_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        initialCurve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID), 'total amount incorrect').to.equal(
        TOTAL_LIQUIDITY_AFTER_LOCKING,
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID), 'locked amount incorrect').to.equal(
        LOCKED_LIQUIDITY,
      )
    })

    test('Curve [0.000654, 2.529136, 22.279453, 0.001034]', async () => {
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(4630021) // 4.630021 - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, initialCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.001103, 2.291495, 22.218365, 0.002583]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.001103, 2.291495, 22.218365, 0.002583)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(9903598) // 9.903598 - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.002327, 1.858716, 22.406037, 0.017385]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.002327, 1.858716, 22.406037, 0.017385)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(50734626) // 50.734626 - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.003450, 1.603399, 23.255067, 0.102200]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.00345, 1.603399, 23.255067, 0.1022)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(266279729) // 266.279729 - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })
  })

  describe('Real world premiums are calculated correctly [100X values]', () => {
    const MULTIPLIER = 100
    const PRECISION = 0.2 // +/- expected value
    const TOTAL_LIQUIDITY = createTokenAmount(10000 * MULTIPLIER, usdcDecimals)
    const TOTAL_LIQUIDITY_AFTER_LOCKING = createTokenAmount(10000 * MULTIPLIER, usdcDecimals) // Since users pay the same amount that is locked, it remains 10k
    const LOCKED_LIQUIDITY = createTokenAmount(5000 * MULTIPLIER, usdcDecimals)
    const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 12.5 * MULTIPLIER
    const SIMULATOR_SPOT_PRICE = 400
    const COLLATERAL_ORDER = 2500 * MULTIPLIER

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria
    const initialCurve = new HyperbolicCurve(0.000654, 2.529136, 22.279453, 0.001034)

    beforeEach(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 400
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve: initialCurve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: SIMULATOR_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE.mul(MULTIPLIER),
      }))

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        initialCurve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000*100 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID), 'total amount incorrect').to.equal(
        TOTAL_LIQUIDITY_AFTER_LOCKING,
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID), 'locked amount incorrect').to.equal(
        LOCKED_LIQUIDITY,
      )
    })

    test('Curve [0.000654, 2.529136, 22.279453, 0.001034]', async () => {
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(4630021 * MULTIPLIER) // 4.630021 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, initialCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.001103, 2.291495, 22.218365, 0.002583]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.001103, 2.291495, 22.218365, 0.002583)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(9903598 * MULTIPLIER) // 9.903598 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.002327, 1.858716, 22.406037, 0.017385]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.002327, 1.858716, 22.406037, 0.017385)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(50734626 * MULTIPLIER) // 50.734626 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.003450, 1.603399, 23.255067, 0.102200]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.00345, 1.603399, 23.255067, 0.1022)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(266279729 * MULTIPLIER) // 266.279729 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })
  })

  describe('Real world premiums are calculated correctly [1000X values]', () => {
    const MULTIPLIER = 1000
    const PRECISION = 1.6 // +/- expected value
    const TOTAL_LIQUIDITY = createTokenAmount(10000 * MULTIPLIER, usdcDecimals)
    const TOTAL_LIQUIDITY_AFTER_LOCKING = createTokenAmount(10000 * MULTIPLIER, usdcDecimals) // Since users pay the same amount that is locked, it remains 10k
    const LOCKED_LIQUIDITY = createTokenAmount(5000 * MULTIPLIER, usdcDecimals)
    const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = 12.5 * MULTIPLIER
    const SIMULATOR_SPOT_PRICE = 400
    const COLLATERAL_ORDER = 2500 * MULTIPLIER

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria
    const initialCurve = new HyperbolicCurve(0.000654, 2.529136, 22.279453, 0.001034)

    beforeEach(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 400
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve: initialCurve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: SIMULATOR_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE.mul(MULTIPLIER),
      }))

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        initialCurve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      // buy OTokens so we can have LOCKED_LIQUIDITY=5000*100 locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)

      await potionLiquidityPool.connect(potionLp1).withdraw(POOL_ID, totalPremiumInCollateralTokens)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID), 'total amount incorrect').to.equal(
        TOTAL_LIQUIDITY_AFTER_LOCKING,
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID), 'locked amount incorrect').to.equal(
        LOCKED_LIQUIDITY,
      )
    })

    test('Curve [0.000654, 2.529136, 22.279453, 0.001034]', async () => {
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(4630021 * MULTIPLIER) // 4.630021 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, initialCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.001103, 2.291495, 22.218365, 0.002583]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.001103, 2.291495, 22.218365, 0.002583)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from(9903598 * MULTIPLIER) // 9.903598 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.002327, 1.858716, 22.406037, 0.017385]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.002327, 1.858716, 22.406037, 0.017385)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(50734626 * MULTIPLIER) // 50.734626 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })

    test('Curve [0.003450, 1.603399, 23.255067, 0.102200]', async () => {
      // update curve
      const newCurve = new HyperbolicCurve(0.00345, 1.603399, 23.255067, 0.1022)
      await addAndSetNewCurve(newCurve)

      // get premiums
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE
      const expectedPremiumResult = BigNumber.from(266279729 * MULTIPLIER) // 266.279729 * MULTIPLIER - value generated in Jupyter notebook

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, newCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })
  })

  describe('Real world premiums are calculated correctly [MAX CURVE VALUES]', () => {
    const MULTIPLIER = 1000000
    const PRECISION = 1.6 // +/- expected value
    const TOTAL_LIQUIDITY = createTokenAmount(1000000 * MULTIPLIER, usdcDecimals)
    const SIMULATOR_SPOT_PRICE = 4000000
    const COLLATERAL_ORDER = 2500 * MULTIPLIER

    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria

    const initialCurve = new HyperbolicCurve(
      HyperbolicCurve.MAX_A,
      HyperbolicCurve.MAX_B,
      HyperbolicCurve.MAX_C,
      HyperbolicCurve.MAX_D,
    )

    beforeEach(async () => {
      const LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE = 4000000
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve: initialCurve,
        initialLiquidity: TOTAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: SIMULATOR_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_FOR_THIS_TEST_SUITE,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE.mul(MULTIPLIER),
      }))
    })

    test('Curve [10, 20, 1000, 20]', async () => {
      const orderSize = COLLATERAL_ORDER / SIMULATOR_SPOT_PRICE

      const expectedPremiumResult = BigNumber.from('50062500000000000')

      singleLpSeller1 = new CounterpartyDetails(potionLp1, POOL_ID, initialCurve, criteria1, scaleNum(orderSize))

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])

      const premiumInUSDC = convertToUSDC(expectedPremium)

      expect(premiumInUSDC).to.approximately(convertToUSDC(expectedPremiumResult), PRECISION)
    })
  })

  describe('Max utility reached', () => {
    const A = 1
    const B = 1
    const C = 1
    const D = 1
    const MAX_UTIL = 0.5
    const curve = new HyperbolicCurve(A, B, C, D, MAX_UTIL)
    const ETH_PRICE_FOR_TEST = 1
    const TEST_ORDER_SIZE = 5000
    const INITIAL_LIQUIDITY = createTokenAmount(10000, usdcDecimals)
    const LOCKED_LIQUIDITY = createTokenAmount(TEST_ORDER_SIZE, usdcDecimals)
    let initialPremiumInCollateralTokens: BigNumber
    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria

    beforeEach(async () => {
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager } = await setupTests({
        curve,
        initialLiquidity: INITIAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: ETH_PRICE_FOR_TEST,
        lowerStrikeInDollars: ETH_PRICE_FOR_TEST,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))

      const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = TEST_ORDER_SIZE

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      initialPremiumInCollateralTokens = totalPremiumInCollateralTokens

      // buy OTokens so we can have LOCKED_LIQUIDITY=TEST_ORDER_SIZE locked
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256)
    })

    test('conditions', async () => {
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, POOL_ID)).to.equal(
        INITIAL_LIQUIDITY.add(initialPremiumInCollateralTokens),
      )
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, POOL_ID)).to.equal(LOCKED_LIQUIDITY)
    })

    test('Utility exceeded', async () => {
      const ORDER_SIZE_TO_EXCEED_UTIL = 4000
      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_TO_EXCEED_UTIL),
      )

      await expect(
        potionLiquidityPool
          .connect(potionBuyer1)
          .buyOtokens(lowerStrikePut.address, [singleLpSeller1], ethers.constants.MaxUint256),
      ).to.revertedWith('Max util exceeded')
    })
  })

  describe('Spot prices change', () => {
    const A = 1
    const B = 1
    const C = 1
    const D = 1

    const curve = new HyperbolicCurve(A, B, C, D)
    const INITIAL_SPOT_PRICE = 4000
    const FINAL_SPOT_PRICE = 2000
    const LOWER_STRIKE_PRICE_IN_DOLLARS = 3700
    const TEST_ORDER_SIZE = 10
    const INITIAL_LIQUIDITY = createTokenAmount(100000, usdcDecimals)
    let lowerStrikePut: OtokenInstance
    let criteria1: CurveCriteria
    let potionLiquidityPool: PotionLiquidityPool
    let oracle: MockOracle
    let weth: MockERC20

    test('ETH price doesn"t change premium calculation', async () => {
      ;({ lowerStrikePut, criteria1, potionLiquidityPool, curveManager, oracle, weth } = await setupTests({
        curve,
        initialLiquidity: INITIAL_LIQUIDITY,
        poolId: POOL_ID,
        ethSpotPriceInDollars: INITIAL_SPOT_PRICE,
        lowerStrikeInDollars: LOWER_STRIKE_PRICE_IN_DOLLARS,
        lp: potionLp1,
        buyer: potionBuyer1,
        initialBuyerBalance: INITIAL_BUYER_BALANCE,
      }))

      const ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT = TEST_ORDER_SIZE

      singleLpSeller1 = new CounterpartyDetails(
        potionLp1,
        POOL_ID,
        curve,
        criteria1,
        scaleNum(ORDER_SIZE_REQUIRED_TOHAVE_LOCKED_AMOUNT),
      )

      const { totalPremiumInCollateralTokens: premium1 } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      await oracle.setRealTimePrice(weth.address, scaleNum(FINAL_SPOT_PRICE))

      const { totalPremiumInCollateralTokens: premium2 } = await potionLiquidityPool.premiums(lowerStrikePut.address, [
        singleLpSeller1,
      ])

      expect(premium1).to.equal(premium2)
    })
  })

  const addAndSetNewCurve = async (newCurve: HyperbolicCurve) => {
    const curveHash = await curveManager.hashCurve(newCurve.asSolidityStruct())
    await curveManager.addCurve(newCurve.asSolidityStruct())
    await potionLiquidityPool.connect(potionLp1).setCurve(POOL_ID, curveHash)
  }
})

const convertToUSDC = (value: BigNumber) => {
  return Number(formatUnits(value, usdcDecimals))
}

interface SetupTestProps {
  curve: HyperbolicCurve
  initialLiquidity: BigNumber
  poolId: number
  ethSpotPriceInDollars: number
  lowerStrikeInDollars: number
  lp: Wallet
  initialBuyerBalance: BigNumber
  buyer: Wallet
}

interface SetupTestResult {
  lowerStrikePut: OtokenInstance
  potionLiquidityPool: PotionLiquidityPool
  criteria1: CurveCriteria
  curveManager: CurveManager
  oracle: MockOracle
  weth: MockERC20
}

const setupTests = async ({
  curve,
  initialLiquidity,
  poolId,
  ethSpotPriceInDollars,
  lowerStrikeInDollars,
  lp,
  buyer,
  initialBuyerBalance,
}: SetupTestProps): Promise<SetupTestResult> => {
  const testContracts = await deployTestContracts()

  const { potionLiquidityPool, usdc, weth, oracle, otokenFactory, curveManager, criteriaManager } = testContracts

  await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars))

  const curveHash = await curveManager.hashCurve(curve.asSolidityStruct())
  await curveManager.addCurve(curve.asSolidityStruct())

  const { criteria, criteriaSets } = await deployDefaultCriteria(criteriaManager, weth.address, usdc.address)
  const criteria1 = criteria[0]
  const criteriaSetHash = criteriaSets[0].toKeccak256()

  const { put: lowerStrikePut } = await getTestOtoken({
    otokenFactory,
    strikeAsset: usdc.address,
    underlyingAsset: weth.address,
    deploy: true,
    strikeInDollars: lowerStrikeInDollars,
  })

  // mint usdc to users
  const usdcStartAmount = initialBuyerBalance
  const mintings = [
    { wallet: buyer, amount: usdcStartAmount },
    { wallet: lp, amount: usdcStartAmount },
  ]
  await mintTokens(usdc, mintings, potionLiquidityPool.address)

  // Have LPs deposit collateral
  const depositAmount1 = initialLiquidity

  await potionLiquidityPool.connect(lp).deposit(poolId, depositAmount1)
  await potionLiquidityPool.connect(lp).setCurveCriteria(poolId, criteriaSetHash)
  await potionLiquidityPool.connect(lp).setCurve(poolId, curveHash)

  return {
    lowerStrikePut,
    criteria1,
    potionLiquidityPool,
    curveManager,
    oracle,
    weth,
  }
}
