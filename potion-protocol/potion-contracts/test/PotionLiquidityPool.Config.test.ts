import { ethers, waffle } from 'hardhat'
import { expect } from 'chai'
import { BigNumber, constants } from 'ethers'

import { CounterpartyDetails, Pool } from '../scripts/lib/purchaseHelpers'
import { CriteriaSet, CurveCriteria, HyperbolicCurve, OrderedCriteria } from '../scripts/lib/typeHelpers'
import {
  usdcDecimals,
  deployTestContracts,
  getTestOtoken,
  mintTokens,
  DEFAULT_DURATION_IN_DAYS,
} from './helpers/testSetup'

const provider = waffle.provider

import {
  MockERC20,
  AddressBook,
  MockOracle,
  Otoken as OtokenInstance,
  OtokenFactory,
  PotionLiquidityPool,
  CurveManager,
  CriteriaManager,
} from '../typechain'
import { createTokenAmount, createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { deployDefaultCriteria, deployDefaultCurves } from '../scripts/lib/postDeployActions/CurveAndCriteriaActions'

describe('PotionLiquidityPool - Config tests', function () {
  const wallets = provider.getWallets()

  const [potionBuyer1, potionLp1, potionLp2, potionLp3, potionLp4, potionLp5] = wallets
  let usdcStartAmount: BigNumber

  let addressBook: AddressBook
  let otokenFactory: OtokenFactory
  let curveManager: CurveManager
  let criteriaManager: CriteriaManager
  let potionLiquidityPool: PotionLiquidityPool

  // oracle module mock
  let oracle: MockOracle

  let usdc: MockERC20
  let weth: MockERC20

  const ethSpotPriceInDollars = 250 // $ per ETH

  const lowerStrikeInDollars = 200 // $ per ETH
  let lowerStrikePut: OtokenInstance
  let curve1: HyperbolicCurve
  let curveHash1: string
  let poolId1: number
  let criteria1: CurveCriteria
  let criteriaSetHash: string

  beforeEach('set up contracts', async () => {
    ;({
      addressBook,
      potionLiquidityPool,
      usdc,
      weth,
      oracle,
      otokenFactory,
      curveManager,
      criteriaManager,
    } = await deployTestContracts())
    await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars))
    await oracle.setRealTimePrice(usdc.address, scaleNum(1))

    poolId1 = 0
    const curves = await deployDefaultCurves(curveManager)
    const { criteria, criteriaSets } = await deployDefaultCriteria(criteriaManager, weth.address, usdc.address)
    curve1 = curves[0]
    curveHash1 = curve1.toKeccak256()
    criteria1 = criteria[0]
    criteriaSetHash = criteriaSets[0].toKeccak256()

    // Add a test otoken
    ;({ put: lowerStrikePut } = await getTestOtoken({
      otokenFactory,
      strikeAsset: usdc.address,
      underlyingAsset: weth.address,
      deploy: true,
      strikeInDollars: lowerStrikeInDollars,
    }))

    // mint usdc to users
    usdcStartAmount = createTokenAmount(100000000, usdcDecimals)
    const mintings = wallets.map((w) => ({ wallet: w, amount: usdcStartAmount }))
    await mintTokens(usdc, mintings, potionLiquidityPool.address)
  })

  describe('Deposit and config tests', () => {
    it('initialised properly', async () => {
      const addressbookAddr = await potionLiquidityPool.opynAddressBook()
      expect(addressbookAddr).to.equal(addressBook.address)
    })

    it('starting balances are as expected', async () => {
      // pool
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(0)
      expect(await weth.balanceOf(potionLiquidityPool.address)).to.equal(0)

      // buyers
      expect(await usdc.balanceOf(potionBuyer1.address)).to.equal(usdcStartAmount)
      expect(await weth.balanceOf(potionBuyer1.address)).to.equal(0)

      // LPs
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount)
      expect(await weth.balanceOf(potionLp1.address)).to.equal(0)
      expect(await usdc.balanceOf(potionLp2.address)).to.equal(usdcStartAmount)
      expect(await weth.balanceOf(potionLp2.address)).to.equal(0)
    })

    it('deposit', async () => {
      const depositAmount1 = createTokenAmount(1000000, usdcDecimals)

      await potionLiquidityPool.connect(potionLp1).deposit(poolId1, depositAmount1)
      await potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash)

      const depositAmount2 = createTokenAmount(2000000, usdcDecimals)
      await potionLiquidityPool
        .connect(potionLp2)
        .depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash)
      await potionLiquidityPool
        .connect(potionLp3)
        .depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash)
      await potionLiquidityPool
        .connect(potionLp4)
        .depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash)
      await potionLiquidityPool
        .connect(potionLp5)
        .depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash)

      // pool balances
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount2.mul(4).add(depositAmount1))
      expect(await weth.balanceOf(potionLiquidityPool.address)).to.equal(0)

      // // buyer balances
      expect(await usdc.balanceOf(potionBuyer1.address)).to.equal(usdcStartAmount)
      expect(await weth.balanceOf(potionBuyer1.address)).to.equal(0)

      // LP balances
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount.sub(depositAmount1))
      expect(await weth.balanceOf(potionLp1.address)).to.equal(0)
      expect(await usdc.balanceOf(potionLp2.address)).to.equal(usdcStartAmount.sub(depositAmount2))
      expect(await weth.balanceOf(potionLp2.address)).to.equal(0)
    })

    it('open vault', async () => {
      await potionLiquidityPool.connect(potionLp2).createNewVaultId(lowerStrikePut.address)
    })

    it('buy with real curve before curve is set', async () => {
      const sellers = [new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, scaleNum(1))]
      await expect(
        potionLiquidityPool.buyOtokens(lowerStrikePut.address, sellers, ethers.constants.MaxUint256),
      ).to.be.revertedWith('Invalid curve')
    })

    it('set curve', async () => {
      await potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)
    })

    it('set criteria to 0x0 (withdraw capital from market)', async () => {
      await potionLiquidityPool
        .connect(potionLp1)
        .setCurveCriteria(poolId1, '0x0000000000000000000000000000000000000000000000000000000000000000')
    })

    it('duration in days is correct', async () => {
      const remainingDays = await potionLiquidityPool.durationInDays(lowerStrikePut.address)
      expect(remainingDays).to.equal(DEFAULT_DURATION_IN_DAYS)

      // time travel
      const now = (await ethers.provider.getBlock('latest')).timestamp
      const NUMBER_OF_DAYS = 1
      const SECONDS_TO_FAST_FORWARD = 86400 * NUMBER_OF_DAYS

      await provider.send('evm_setNextBlockTimestamp', [now + SECONDS_TO_FAST_FORWARD])
      await provider.send('evm_mine', [])

      const remainingDaysAfter = await potionLiquidityPool.durationInDays(lowerStrikePut.address)
      expect(remainingDaysAfter).to.equal(DEFAULT_DURATION_IN_DAYS - NUMBER_OF_DAYS)
    })

    it('settleAndRedistributeSettlement', async () => {
      const expiryPriceUnderlyingInDollars = 200
      const sellers = [new CounterpartyDetails(potionLp2, poolId1, curve1, criteria1, scaleNum(1))]

      await potionLiquidityPool
        .connect(potionLp2)
        .depositAndCreateCurveAndCriteria(poolId1, usdcStartAmount, curve1.asSolidityStruct(), [criteria1])

      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, sellers, ethers.constants.MaxUint256)

      const scaledETHPrice = scaleNum(expiryPriceUnderlyingInDollars)
      const scaledUSDCPrice = scaleNum(1)

      const expiry = (await lowerStrikePut.expiryTimestamp()).toNumber()

      await oracle.setExpiryPriceFinalizedAllPeiodOver(weth.address, expiry, scaledETHPrice, true)
      await oracle.setExpiryPriceFinalizedAllPeiodOver(usdc.address, expiry, scaledUSDCPrice, true)

      await provider.send('evm_setNextBlockTimestamp', [expiry + 2])
      await provider.send('evm_mine', [])

      const pools = [new Pool(potionLp2.address, poolId1)]

      await expect(potionLiquidityPool.settleAndRedistributeSettlement(lowerStrikePut.address, pools))
        .to.emit(potionLiquidityPool, 'OptionSettled')
        .to.emit(potionLiquidityPool, 'OptionSettlementDistributed')
    })

    it('tests sumOfAllLockedBalances', async () => {
      const expiryPriceUnderlyingInDollars = 200
      const sellers = [new CounterpartyDetails(potionLp2, poolId1, curve1, criteria1, scaleNum(1))]

      await potionLiquidityPool
        .connect(potionLp2)
        .depositAndCreateCurveAndCriteria(poolId1, usdcStartAmount, curve1.asSolidityStruct(), [criteria1])

      const lockedBalanceBefore = await potionLiquidityPool.connect(potionBuyer1).sumOfAllLockedBalances()
      expect(lockedBalanceBefore).to.equal(BigNumber.from(0))

      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, sellers, ethers.constants.MaxUint256)

      const lockedBalanceAfterBuying = await potionLiquidityPool.connect(potionBuyer1).sumOfAllLockedBalances()
      expect(lockedBalanceAfterBuying).to.equal(createTokenAmount(expiryPriceUnderlyingInDollars, usdcDecimals))

      const scaledETHPrice = scaleNum(expiryPriceUnderlyingInDollars)
      const scaledUSDCPrice = scaleNum(1)

      const expiry = (await lowerStrikePut.expiryTimestamp()).toNumber()

      await oracle.setExpiryPriceFinalizedAllPeiodOver(weth.address, expiry, scaledETHPrice, true)
      await oracle.setExpiryPriceFinalizedAllPeiodOver(usdc.address, expiry, scaledUSDCPrice, true)

      await provider.send('evm_setNextBlockTimestamp', [expiry + 2])
      await provider.send('evm_mine', [])

      const pools = [new Pool(potionLp2.address, poolId1)]

      await expect(potionLiquidityPool.settleAndRedistributeSettlement(lowerStrikePut.address, pools))
        .to.emit(potionLiquidityPool, 'OptionSettled')
        .to.emit(potionLiquidityPool, 'OptionSettlementDistributed')

      const lockedBalanceAfterSettlement = await potionLiquidityPool.connect(potionBuyer1).sumOfAllLockedBalances()
      expect(lockedBalanceAfterSettlement).to.equal(BigNumber.from(0))
    })

    it('verify max total value locked', async () => {
      const result = await potionLiquidityPool.connect(potionLp1).maxTotalValueLocked()

      expect(result).to.equal(constants.MaxUint256)
    })

    it('modifies max tvl', async () => {
      const MAX_TVL = constants.MaxUint256.div(1000000)

      await potionLiquidityPool.connect(potionBuyer1).setMaxTotalValueLocked(MAX_TVL)

      const result = await potionLiquidityPool.connect(potionBuyer1).maxTotalValueLocked()

      expect(result).to.equal(MAX_TVL)
    })

    it('cannot modify max tvl', async () => {
      const MAX_TVL = constants.MaxUint256.div(1000000)

      await expect(potionLiquidityPool.connect(potionLp1).setMaxTotalValueLocked(MAX_TVL)).to.revertedWith(
        'Ownable: caller is not the owner',
      )
    })

    it('tests cannot buy with premium', async () => {
      const newDepositAmount = createTokenAmount(10000, usdcDecimals)
      // @dev max order to lock all the available liquidity
      const orderSize = newDepositAmount.div(createTokenAmount(lowerStrikeInDollars, usdcDecimals)).toNumber()
      const sellers = [new CounterpartyDetails(potionLp2, poolId1, curve1, criteria1, scaleNum(orderSize))]

      await potionLiquidityPool
        .connect(potionLp2)
        .depositAndCreateCurveAndCriteria(poolId1, newDepositAmount, curve1.asSolidityStruct(), [criteria1])

      const [expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, sellers)
      const newLiquidityAndPremium = newDepositAmount.add(expectedPremium)
      const newOrderSize = newLiquidityAndPremium.div(createTokenAmount(lowerStrikeInDollars, usdcDecimals)).toNumber()
      const sellersWithAmountWithPremium = [
        new CounterpartyDetails(potionLp2, poolId1, curve1, criteria1, scaleNum(newOrderSize)),
      ]

      await expect(
        potionLiquidityPool
          .connect(potionBuyer1)
          .buyOtokens(lowerStrikePut.address, sellersWithAmountWithPremium, ethers.constants.MaxUint256),
      ).to.revertedWith('util calc: >100% locked')
    })
  })

  describe('Withdraw tests', async () => {
    it('withdraws', async () => {
      const depositAmount1 = createTokenAmount(1000000, usdcDecimals)
      const halfDepositAmount = depositAmount1.div(2)
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      await potionLiquidityPoolInstance.deposit(poolId1, depositAmount1)

      // Checking balances after deposit but before withdraw
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount1)
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount.sub(depositAmount1))
      expect(await potionLiquidityPool.sumOfAllUnlockedBalances()).to.equal(depositAmount1)

      // Withdraw
      await expect(potionLiquidityPoolInstance.withdraw(poolId1, halfDepositAmount))
        .to.emit(potionLiquidityPoolInstance, 'Withdrawn')
        .withArgs(potionLp1.address, poolId1, halfDepositAmount)

      // Checking balances after withdraw
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount1.sub(halfDepositAmount))
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(
        usdcStartAmount.sub(depositAmount1).add(halfDepositAmount),
      )
      expect(await potionLiquidityPool.sumOfAllUnlockedBalances()).to.equal(depositAmount1.sub(halfDepositAmount))
    })

    it('cannot withdraw more than unlocked balance', async () => {
      const depositAmount1 = createTokenAmount(1000000, usdcDecimals)
      const exceededAmount = depositAmount1.add(1)
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      await potionLiquidityPoolInstance.deposit(poolId1, depositAmount1)

      // Checking balances after deposit but before withdraw
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount1)
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount.sub(depositAmount1))
      expect(await potionLiquidityPool.sumOfAllUnlockedBalances()).to.equal(depositAmount1)

      // Withdraw
      await expect(potionLiquidityPoolInstance.withdraw(poolId1, exceededAmount)).to.be.reverted

      // Checking balances after attemp to withdraw
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount1)
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount.sub(depositAmount1))
      expect(await potionLiquidityPool.sumOfAllUnlockedBalances()).to.equal(depositAmount1)
    })
  })

  describe('addAndSetCurve tests', () => {
    it('add and set a new curve', async () => {
      const newCurve = new HyperbolicCurve(0, 2.35568, 6.00689, 5.123)

      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      await expect(potionLiquidityPoolInstance.addAndSetCurve(poolId1, newCurve.asSolidityStruct()))
        .to.emit(curveManager, 'CurveAdded')
        .withArgs(newCurve.toKeccak256(), newCurve.toArray())
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
    })

    it('set existing curve', async () => {
      const newCurve = new HyperbolicCurve(0, 2.35568, 6.00689, 5.123)

      // add curve
      await curveManager.addCurve(newCurve.asSolidityStruct())

      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      await expect(potionLiquidityPoolInstance.addAndSetCurve(poolId1, newCurve.asSolidityStruct()))
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
    })
  })

  describe('addAndSetCriterias tests', () => {
    const mockUnderlyingTokenAddress = '0x1122334455667788990011223344556677889900'
    const mockStrikeTokenAddress = '0x0000111122223333444455556666777788889999'

    it('add and set a new criteria', async () => {
      const criteria_30days_100pct = new CurveCriteria(
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        true,
        100,
        30,
      )
      const criteria_10days_110pct = new CurveCriteria(
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        true,
        110,
        10,
      )
      const orderedCriterias = OrderedCriteria.from([criteria_30days_100pct, criteria_10days_110pct])
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()
      const criteriaSetHashes = set.hashes

      await expect(potionLiquidityPoolInstance.addAndSetCriterias(poolId1, orderedCriterias))
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[0].toKeccak256(), orderedCriterias[0].toArray())
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[1].toKeccak256(), orderedCriterias[1].toArray())
        .to.emit(criteriaManager, 'CriteriaSetAdded')
        .withArgs(criteriaSetHash, criteriaSetHashes)
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })

    it('set an existing criteria', async () => {
      const criteria_30days_100pct = new CurveCriteria(
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        true,
        100,
        30,
      )
      const criteria_10days_110pct = new CurveCriteria(
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        true,
        110,
        10,
      )
      const orderedCriterias = OrderedCriteria.from([criteria_30days_100pct, criteria_10days_110pct])
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()

      // add criteria set
      await criteriaManager.addCriteria(criteria_30days_100pct)
      await criteriaManager.addCriteria(criteria_10days_110pct)
      await criteriaManager.addCriteriaSet(set.toArray())

      await expect(potionLiquidityPoolInstance.addAndSetCriterias(poolId1, orderedCriterias))
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })
  })

  describe('depositAndCreateCurveAndCriteria tests', () => {
    const mockUnderlyingTokenAddress = '0x1122334455667788990011223344556677889900'
    const mockStrikeTokenAddress = '0x0000111122223333444455556666777788889999'

    const depositAmount1 = createTokenAmount(1000000, usdcDecimals)

    const criteria_30days_100pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 100, 30)
    const criteria_10days_110pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 110, 10)

    const orderedCriterias = OrderedCriteria.from([criteria_30days_100pct, criteria_10days_110pct])
    const newCurve = new HyperbolicCurve(0, 2.35568, 6.00689, 5.123)

    beforeEach(async () => {
      ;({
        addressBook,
        potionLiquidityPool,
        usdc,
        weth,
        oracle,
        otokenFactory,
        curveManager,
        criteriaManager,
      } = await deployTestContracts())
      await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars))
      await oracle.setRealTimePrice(usdc.address, scaleNum(1))
      poolId1 = 0

      // mint usdc to users
      usdcStartAmount = createTokenAmount(100000000, usdcDecimals)
      const mintings = wallets.map((w) => ({ wallet: w, amount: usdcStartAmount }))
      await mintTokens(usdc, mintings, potionLiquidityPool.address)
    })

    it('deposits and add new curve and new criteria array', async () => {
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)
      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()
      const criteriaSetHashes = set.hashes

      await expect(
        potionLiquidityPoolInstance.depositAndCreateCurveAndCriteria(
          poolId1,
          depositAmount1,
          newCurve.asSolidityStruct(),
          orderedCriterias,
        ),
      )
        .to.emit(potionLiquidityPoolInstance, 'Deposited')
        .withArgs(potionLp1.address, poolId1, depositAmount1)
        .to.emit(curveManager, 'CurveAdded')
        .withArgs(newCurve.toKeccak256(), newCurve.toArray())
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[0].toKeccak256(), orderedCriterias[0].toArray())
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[1].toKeccak256(), orderedCriterias[1].toArray())
        .to.emit(criteriaManager, 'CriteriaSetAdded')
        .withArgs(criteriaSetHash, criteriaSetHashes)
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })

    it('deposits and add existing curve and existing criteria set', async () => {
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()

      // add criteria set
      await criteriaManager.addCriteria(criteria_30days_100pct)
      await criteriaManager.addCriteria(criteria_10days_110pct)
      await criteriaManager.addCriteriaSet(set.toArray())

      // add curve
      await curveManager.addCurve(newCurve.asSolidityStruct())

      await expect(
        potionLiquidityPoolInstance.depositAndCreateCurveAndCriteria(
          poolId1,
          depositAmount1,
          newCurve.asSolidityStruct(),
          orderedCriterias,
        ),
      )
        .to.emit(potionLiquidityPoolInstance, 'Deposited')
        .withArgs(potionLp1.address, poolId1, depositAmount1)
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })

    it('deposits and add existing curve and NEW criteria set', async () => {
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()
      const criteriaSetHashes = set.hashes

      // add curve
      await curveManager.addCurve(newCurve.asSolidityStruct())

      await expect(
        potionLiquidityPoolInstance.depositAndCreateCurveAndCriteria(
          poolId1,
          depositAmount1,
          newCurve.asSolidityStruct(),
          orderedCriterias,
        ),
      )
        .to.emit(potionLiquidityPoolInstance, 'Deposited')
        .withArgs(potionLp1.address, poolId1, depositAmount1)
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[0].toKeccak256(), orderedCriterias[0].toArray())
        .to.emit(criteriaManager, 'CriteriaAdded')
        .withArgs(orderedCriterias[1].toKeccak256(), orderedCriterias[1].toArray())
        .to.emit(criteriaManager, 'CriteriaSetAdded')
        .withArgs(criteriaSetHash, criteriaSetHashes)
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })

    it('deposits and add NEW curve and existing criteria set', async () => {
      const potionLiquidityPoolInstance = potionLiquidityPool.connect(potionLp1)

      const set = new CriteriaSet([criteria_30days_100pct.toKeccak256(), criteria_10days_110pct.toKeccak256()])
      const criteriaSetHash = set.toKeccak256()

      // add criteria set
      await criteriaManager.addCriteria(criteria_30days_100pct)
      await criteriaManager.addCriteria(criteria_10days_110pct)
      await criteriaManager.addCriteriaSet(set.toArray())

      await expect(
        potionLiquidityPoolInstance.depositAndCreateCurveAndCriteria(
          poolId1,
          depositAmount1,
          newCurve.asSolidityStruct(),
          orderedCriterias,
        ),
      )
        .to.emit(potionLiquidityPoolInstance, 'Deposited')
        .withArgs(potionLp1.address, poolId1, depositAmount1)
        .to.emit(curveManager, 'CurveAdded')
        .withArgs(newCurve.toKeccak256(), newCurve.toArray())
        .to.emit(potionLiquidityPoolInstance, 'CurveSelected')
        .withArgs(potionLp1.address, poolId1, newCurve.toKeccak256())
        .to.emit(potionLiquidityPoolInstance, 'CriteriaSetSelected')
        .withArgs(potionLp1.address, poolId1, criteriaSetHash)
    })
  })

  describe('deposit edge cases', () => {
    it('deposit more than tvl', async () => {
      const depositAmount1 = createTokenAmount(1000000, usdcDecimals)

      await potionLiquidityPool.connect(potionLp1).deposit(poolId1, depositAmount1)
      await potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash)

      // pool balances
      expect(await usdc.balanceOf(potionLiquidityPool.address)).to.equal(depositAmount1)
      expect(await weth.balanceOf(potionLiquidityPool.address)).to.equal(0)

      // buyer balances
      expect(await usdc.balanceOf(potionBuyer1.address)).to.equal(usdcStartAmount)
      expect(await weth.balanceOf(potionBuyer1.address)).to.equal(0)

      // LP balances
      expect(await usdc.balanceOf(potionLp1.address)).to.equal(usdcStartAmount.sub(depositAmount1))

      const sumOfAllUnlockedBalances = await potionLiquidityPool.connect(potionLp1).sumOfAllUnlockedBalances()

      const newTVL = sumOfAllUnlockedBalances

      await potionLiquidityPool.connect(potionBuyer1).setMaxTotalValueLocked(newTVL)

      // double check is ok
      const result = await potionLiquidityPool.connect(potionBuyer1).maxTotalValueLocked()

      expect(result).to.equal(newTVL)

      await expect(potionLiquidityPool.connect(potionLp1).deposit(poolId1, depositAmount1)).to.revertedWith(
        'Max TVL exceeded',
      )
    })
  })
})
