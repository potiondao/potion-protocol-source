import { waffle } from 'hardhat'
import { expect } from 'chai'
import { BigNumber } from 'ethers'
import { CounterpartyDetails } from '../scripts/lib/purchaseHelpers'
import { usdcDecimals, deployTestContracts, getTestOtoken, mintTokens, TestContracts } from './helpers/testSetup'
import { CurveCriteria, HyperbolicCurve } from '../scripts/lib/typeHelpers'

const provider = waffle.provider

import {
  MockERC20,
  MockOracle,
  Otoken as OtokenInstance,
  OtokenFactory, // Renamed from OtokenFactory for easy compatibility with hardhat-typechain, which generates a factory for the Otoken contract
  PotionLiquidityPool,
  CurveManager,
  CriteriaManager,
} from '../typechain'
import { createTokenAmount, createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { deployDefaultCurves, deployDefaultCriteria } from '../scripts/lib/postDeployActions/CurveAndCriteriaActions'

// When testing purchases and settlements, we often want to run the same set of operations and the same set of checks.
// This suite of tests does that, by generating a set of nearly-identical tests in the before() block.
//
// To add additional tests, add additional data to the arrays: successfulPurchaseParams, createAndPurchaseParams & successfulSettleTestCases
// To change what the generated tests *do*, edit the code that iterates through those arrays
describe('PotionLiquidityPool - Edge and Error cases', function () {
  const wallets = provider.getWallets()
  const [potionBuyer1, potionLp1, potionLp2, potionLp3, potionLp4, potionLp5] = wallets
  let usdcStartAmount: BigNumber

  let testContracts: TestContracts
  let otokenFactory: OtokenFactory
  let potionLiquidityPool: PotionLiquidityPool
  let curveManager: CurveManager
  let criteriaManager: CriteriaManager

  // oracle module mock
  let oracle: MockOracle

  let usdc: MockERC20
  let weth: MockERC20

  const ethSpotPriceInDollars = 250 // $ per ETH
  const lowerStrikeInDollars = 200 // $ per ETH
  const higherStrikeInDollars = 300 // $ per ETH
  let lowerStrikePut: OtokenInstance
  let higherStrikePut: OtokenInstance
  let curve1: HyperbolicCurve
  let curveHash1: string
  let poolId1: number
  let criteria1: CurveCriteria
  let criteriaSetHash: string

  before('set up contracts', async () => {
    testContracts = await deployTestContracts()
    ;({ potionLiquidityPool, usdc, weth, oracle, otokenFactory, curveManager, criteriaManager } = testContracts)

    await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars))

    // Create a single curve, criteria, and criteriaSet for testing
    poolId1 = 0
    const curves = await deployDefaultCurves(curveManager)
    const { criteria, criteriaSets } = await deployDefaultCriteria(criteriaManager, weth.address, usdc.address)
    curve1 = curves[0]
    curveHash1 = curve1.toKeccak256()
    criteria1 = criteria[0]
    criteriaSetHash = criteriaSets[0].toKeccak256()

    // Add some options; one is deployed and one is not deployed yet
    ;({ put: lowerStrikePut } = await getTestOtoken({
      otokenFactory,
      strikeAsset: usdc.address,
      underlyingAsset: weth.address,
      deploy: true,
      strikeInDollars: lowerStrikeInDollars,
    }))
    ;({ put: higherStrikePut } = await getTestOtoken({
      otokenFactory,
      strikeAsset: usdc.address,
      underlyingAsset: weth.address,
      deploy: true,
      strikeInDollars: higherStrikeInDollars,
    }))

    // mint usdc to users
    usdcStartAmount = createTokenAmount(100000000, usdcDecimals)
    const mintings = wallets.map((w) => ({ wallet: w, amount: usdcStartAmount }))
    await mintTokens(usdc, mintings, potionLiquidityPool.address)

    // Have LPs deposit collateral
    const depositAmount1 = createTokenAmount(1000000, usdcDecimals)
    await potionLiquidityPool.connect(potionLp1).deposit(poolId1, depositAmount1)
    await potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash)
    await potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)

    const depositAmount2 = createTokenAmount(2000000, usdcDecimals)
    for (const w of [potionLp2, potionLp3, potionLp4, potionLp5]) {
      await potionLiquidityPool.connect(w).depositAndConfigurePool(poolId1, depositAmount2, curveHash1, criteriaSetHash)
    }
  })

  describe('Single LP: premium check', function () {
    let singleLpSeller1: CounterpartyDetails
    let expectedPremium: BigNumber

    before('establish expectations', async () => {
      singleLpSeller1 = new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, scaleNum(8))
      ;[expectedPremium] = await potionLiquidityPool.premiums(lowerStrikePut.address, [singleLpSeller1])
    })

    it('Max premium (0) insufficient', async () => {
      await expect(
        potionLiquidityPool.connect(potionBuyer1).buyOtokens(lowerStrikePut.address, [singleLpSeller1], 0),
      ).to.be.revertedWith('Premium higher than max')
    })

    it('Max premium (expected - 1) insufficient', async () => {
      await expect(
        potionLiquidityPool
          .connect(potionBuyer1)
          .buyOtokens(higherStrikePut.address, [singleLpSeller1], expectedPremium.sub(1)),
      ).to.be.revertedWith('Premium higher than max')
    })

    it('Max premium (expected) is sufficient', async () => {
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(lowerStrikePut.address, [singleLpSeller1], expectedPremium)
    })
  })

  describe('Single LP: small orders', function () {
    let singleLpSellerOfZero: CounterpartyDetails
    const maxPremium = scaleNum(5000) // Too high is fine for this test

    before('establish expectations', async () => {
      singleLpSellerOfZero = new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, scaleNum(0))
    })

    it('Order size of zero not allowed', async () => {
      await expect(
        potionLiquidityPool
          .connect(potionBuyer1)
          .buyOtokens(lowerStrikePut.address, [singleLpSellerOfZero], maxPremium),
      ).to.be.revertedWith('Order tranche is zero')
    })

    it('Order size of zero cannot calc premium', async () => {
      await expect(
        potionLiquidityPool.connect(potionBuyer1).premiums(lowerStrikePut.address, [singleLpSellerOfZero]),
      ).to.be.revertedWith('Order tranche too small')
    })
  })

  describe('Five LPs: premium checks', function () {
    let fiveLpSellers: CounterpartyDetails[]
    let expectedPremium: BigNumber
    const heterogeneousTokenAmounts = [scaleNum(8), scaleNum(42), scaleNum(1), scaleNum(33), scaleNum(6)]
    const fiveLps = [potionLp1, potionLp2, potionLp3, potionLp4, potionLp5]

    before('establish expectations', async () => {
      const fiveCriteria = [criteria1, criteria1, criteria1, criteria1, criteria1]
      const fivePoolIds = [poolId1, poolId1, poolId1, poolId1, poolId1]
      const fiveCurves = [curve1, curve1, curve1, curve1, curve1]
      fiveLpSellers = CounterpartyDetails.fromLists(
        fiveLps,
        fivePoolIds,
        fiveCurves,
        fiveCriteria,
        heterogeneousTokenAmounts,
      )
      ;[expectedPremium] = await potionLiquidityPool.premiums(higherStrikePut.address, fiveLpSellers)
    })

    it('Max premium (1000) insufficient', async () => {
      await expect(
        potionLiquidityPool.connect(potionBuyer1).buyOtokens(higherStrikePut.address, fiveLpSellers, 1000),
      ).to.be.revertedWith('Premium higher than max')
    })

    it('Max premium (expected - 1) insufficient', async () => {
      await expect(
        potionLiquidityPool
          .connect(potionBuyer1)
          .buyOtokens(higherStrikePut.address, fiveLpSellers, expectedPremium.sub(1)),
      ).to.be.revertedWith('Premium higher than max')
    })

    it('Max premium (expected) is sufficient', async () => {
      await potionLiquidityPool
        .connect(potionBuyer1)
        .buyOtokens(higherStrikePut.address, fiveLpSellers, expectedPremium)
    })
  })
})
