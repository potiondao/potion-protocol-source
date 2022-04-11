import { ethers, waffle, upgrades } from 'hardhat'
import { expect } from 'chai'
import { BigNumber, ContractFactory } from 'ethers'
import { CounterpartyDetails } from '../scripts/lib/purchaseHelpers'
import { HyperbolicCurve, CurveCriteria } from '../scripts/lib/typeHelpers'
import { usdcDecimals, deployTestContracts, getTestOtoken, mintTokens } from './helpers/testSetup'
const provider = waffle.provider

import {
  MockERC20,
  AddressBook,
  MockOracle,
  PotionLiquidityPool,
  PotionLiquidityPoolUpgradeTest,
  Otoken as OtokenInstance,
  OtokenFactory,
  CurveManager,
  CriteriaManager,
} from '../typechain'
import { createTokenAmount, createScaledNumber as scaleNum } from './helpers/OpynUtils'
import { fail } from 'assert'
import { deployDefaultCurves, deployDefaultCriteria } from '../scripts/lib/postDeployActions/CurveAndCriteriaActions'

describe('PotionLiquidityPool - Upgrades', function () {
  const wallets = provider.getWallets()
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [owner, potionLp1] = wallets
  let usdcStartAmount: BigNumber

  let addressBook: AddressBook
  let otokenFactory: OtokenFactory
  let potionLiquidityPool: PotionLiquidityPool
  let curveManager: CurveManager
  let criteriaManager: CriteriaManager
  let PotionLiquidityPoolUpgradeTestFactory: ContractFactory

  const lowerStrikeInDollars = 200 // $ per ETH
  let lowerStrikePut: OtokenInstance

  // oracle module mock
  let oracle: MockOracle

  let usdc: MockERC20
  let weth: MockERC20

  const depositAmount = createTokenAmount(1000000, usdcDecimals)
  const ethSpotPriceInDollars = 250 // $ per ETH
  let curve1: HyperbolicCurve
  let curveHash1: string
  let poolId1: number
  let criteriaHash1: string
  let criteria1: CurveCriteria
  let criteriaSetHash: string

  before('set up contracts', async () => {
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
    PotionLiquidityPoolUpgradeTestFactory = await ethers.getContractFactory('PotionLiquidityPoolUpgradeTest')
    await oracle.setRealTimePrice(weth.address, scaleNum(ethSpotPriceInDollars))
    await oracle.setRealTimePrice(usdc.address, scaleNum(1))

    poolId1 = 0
    const curves = await deployDefaultCurves(curveManager)
    const { criteria, criteriaSets } = await deployDefaultCriteria(criteriaManager, weth.address, usdc.address)
    curve1 = curves[0]
    curveHash1 = curve1.toKeccak256()
    criteria1 = criteria[0]
    criteriaHash1 = criteria1.toKeccak256()
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

    // Deposit some funds
    await potionLiquidityPool
      .connect(potionLp1)
      .depositAndConfigurePool(poolId1, depositAmount, curveHash1, criteriaSetHash)

    // Create a Potion vault for our test otoken
    potionLiquidityPool.createNewVaultId(lowerStrikePut.address)
  })

  describe('with an initial contract deployed', () => {
    it('addressbook as expected', async () => {
      const addressbookAddr = await potionLiquidityPool.opynAddressBook()
      expect(addressbookAddr).to.equal(addressBook.address)
    })

    it('contract cannot be paused by non-owners', async () => {
      await expect(potionLiquidityPool.connect(potionLp1).pause()).to.be.revertedWith(
        `Ownable: caller is not the owner`,
      )
    })

    it('contract can be paused and unpaused by owner', async () => {
      await potionLiquidityPool.pause()
      await potionLiquidityPool.unpause()
    })

    it('hash registries as expected', async () => {
      expect(await curveManager.isKnownCurveHash(curveHash1), 'isKnownCurveHash').to.equal(true)
      expect(await criteriaManager.registeredCriteria(criteriaHash1), 'registeredCriteria').to.equal(true)
    })

    it('internal balances as expected', async () => {
      expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, poolId1), 'LpLockedAmount').to.equal(0)
      expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, poolId1), 'LpTotalAmount').to.equal(
        depositAmount,
      )
    })

    it('USDC balance is as expected', async () => {
      const bal = await usdc.balanceOf(potionLiquidityPool.address)
      expect(bal).to.equal(depositAmount)
    })

    it('functions fail if not defined in original contract', async () => {
      const upgradedInterface = (await PotionLiquidityPoolUpgradeTestFactory.attach(
        potionLiquidityPool.address,
      )) as PotionLiquidityPoolUpgradeTest
      await expect(upgradedInterface.upgradeTestVal()).to.be.revertedWith(
        `function selector was not recognized and there's no fallback function`,
      )
      await expect(upgradedInterface.setUpgradeTestVal(7)).to.be.revertedWith(
        `function selector was not recognized and there's no fallback function`,
      )
    })

    it('upgrade can be prepared', async () => {
      await upgrades.prepareUpgrade(potionLiquidityPool.address, PotionLiquidityPoolUpgradeTestFactory)
    })

    it('upgrade can be applied', async () => {
      const upgradedContract = await upgrades.upgradeProxy(
        potionLiquidityPool.address,
        PotionLiquidityPoolUpgradeTestFactory,
      )
      await upgradedContract.setUpgradeTestVal(99)
      expect(await upgradedContract.upgradeTestVal(), 'upgradeTestVal').to.equal(99)
    })

    it('upgrade can be prepared and then applied', async () => {
      await upgrades.prepareUpgrade(potionLiquidityPool.address, PotionLiquidityPoolUpgradeTestFactory)
      const upgradedContract = await upgrades.upgradeProxy(
        potionLiquidityPool.address,
        PotionLiquidityPoolUpgradeTestFactory,
      )
      await upgradedContract.setUpgradeTestVal(42)
      expect(await upgradedContract.upgradeTestVal(), 'upgradeTestVal').to.equal(42)
    })

    describe('after contract upgrade', () => {
      before('upgrade contract', async () => {
        potionLiquidityPool = (await upgrades.upgradeProxy(
          potionLiquidityPool.address,
          PotionLiquidityPoolUpgradeTestFactory,
        )) as PotionLiquidityPool
      })

      it('addressbook as expected', async () => {
        const addressbookAddr = await potionLiquidityPool.opynAddressBook()
        expect(addressbookAddr).to.equal(addressBook.address)
      })

      it('hash registries as expected', async () => {
        expect(await curveManager.isKnownCurveHash(curveHash1), 'isKnownCurveHash').to.equal(true)
        expect(await criteriaManager.registeredCriteria(criteriaHash1), 'registeredCriteria').to.equal(true)
      })

      it('internal balances as expected', async () => {
        expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, poolId1), 'LpLockedAmount').to.equal(0)
        expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, poolId1), 'LpTotalAmount').to.equal(
          depositAmount,
        )
      })

      it('USDC balance is as expected', async () => {
        const bal = await usdc.balanceOf(potionLiquidityPool.address)
        expect(bal).to.equal(depositAmount)
      })

      it(`cannot 'prepareUpgrade' back to original contract because it has less state`, async () => {
        const PotionLiquidityPoolFactory = await ethers.getContractFactory('PotionLiquidityPool')
        try {
          await upgrades.prepareUpgrade(potionLiquidityPool.address, PotionLiquidityPoolFactory)
          fail('Upgrade succeeded but should not have!')
        } catch (e) {
          expect(e.message).to.contain('Deleted `upgradeTestVal`')
        }
      })

      it(`cannot 'upgradeProxy' back to original contract because it has less state`, async () => {
        const PotionLiquidityPoolFactory = await ethers.getContractFactory('PotionLiquidityPool')
        try {
          await upgrades.upgradeProxy(potionLiquidityPool.address, PotionLiquidityPoolFactory)
          fail('Upgrade succeeded but should not have!')
        } catch (e) {
          expect(e.message).to.contain('Deleted `upgradeTestVal`')
        }
      })

      it(`LP can withdraw half of their funds (proves continued control of ERC20 balances)`, async () => {
        await potionLiquidityPool.connect(potionLp1).withdraw(poolId1, depositAmount.div(2))
      })

      describe('after LP withdraws the other half of their capital', () => {
        before('upgrade contract', async () => {
          await potionLiquidityPool.connect(potionLp1).withdraw(poolId1, depositAmount.div(2))
        })

        it('internal balances as expected', async () => {
          expect(await potionLiquidityPool.lpLockedAmount(potionLp1.address, poolId1), 'LpLockedAmount').to.equal(0)
          expect(await potionLiquidityPool.lpTotalAmount(potionLp1.address, poolId1), 'LpTotalAmount').to.equal(0)
        })

        it('USDC balance is as expected', async () => {
          const bal = await usdc.balanceOf(potionLiquidityPool.address)
          expect(bal).to.equal(0)
        })
      })
    })

    describe('after changing criteriaManager', () => {
      before('change criteriaManager address to new instance', async () => {
        const CriteriaManagerFactory = await ethers.getContractFactory('CriteriaManager')
        const newCriteriaManager = await CriteriaManagerFactory.deploy()
        await potionLiquidityPool.setCriteriaManager(newCriteriaManager.address)
      })

      after('change criteriaManager address to original one', async () => {
        await potionLiquidityPool.setCriteriaManager(criteriaManager.address)
      })

      // This test seems to cause hardhat some issues (https://github.com/nomiclabs/hardhat/issues/1185) but the test does fail if the message changes
      it('criteria cannot be used', async () => {
        await expect(
          potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash),
        ).to.be.revertedWith(`No such criteriaSet`)
      })

      it('can revert back to old criteriaManager and all works', async () => {
        await potionLiquidityPool.setCriteriaManager(criteriaManager.address)
        await potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash)
      })
    })

    describe('after changing curveManager', () => {
      before('change curveManager address to new instance', async () => {
        const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
        const newCurveManager = await CurveManagerFactory.deploy()
        await potionLiquidityPool.setCurveManager(newCurveManager.address)
      })

      after('change curveManager address to original one', async () => {
        await potionLiquidityPool.setCurveManager(curveManager.address)
      })

      // This test seems to cause hardhat some issues (https://github.com/nomiclabs/hardhat/issues/1185) but the test does fail if the message changes
      it('curve cannot be used', async () => {
        await expect(potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)).to.be.revertedWith(
          `No such curve`,
        )
      })

      it('can revert back to old curveManager and all works', async () => {
        await potionLiquidityPool.setCurveManager(curveManager.address)
        await potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)
      })
    })

    describe('with paused contract', () => {
      before('pause contract', async () => {
        await potionLiquidityPool.pause()
      })

      after('unpause contract', async () => {
        if (await potionLiquidityPool.paused()) {
          await potionLiquidityPool.unpause()
        }
      })

      it('contract cannot be unpaused by non-owners', async () => {
        await expect(potionLiquidityPool.connect(potionLp1).unpause()).to.be.revertedWith(
          `Ownable: caller is not the owner`,
        )
      })

      it('deposits disabled', async () => {
        await expect(potionLiquidityPool.connect(potionLp1).deposit(poolId1, 1)).to.be.revertedWith(`Pausable: paused`)
        await expect(
          potionLiquidityPool.depositAndConfigurePool(poolId1, depositAmount, curveHash1, criteriaSetHash),
        ).to.be.revertedWith(`Pausable: paused`)
      })

      it('withdrawals disabled', async () => {
        await expect(potionLiquidityPool.connect(potionLp1).withdraw(poolId1, 1)).to.be.revertedWith(`Pausable: paused`)
      })

      it('pool config disabled', async () => {
        await expect(
          potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash),
        ).to.be.revertedWith(`Pausable: paused`)
        await expect(potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)).to.be.revertedWith(
          `Pausable: paused`,
        )
      })

      it('creating (but not getting) vaults disabled', async () => {
        await potionLiquidityPool.getVaultId(lowerStrikePut.address)
        await expect(potionLiquidityPool.createNewVaultId(lowerStrikePut.address)).to.be.revertedWith(
          `Pausable: paused`,
        )
      })

      it('buying otokens disabled', async () => {
        const counterparties = [new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, BigNumber.from(1000))]
        await expect(
          potionLiquidityPool
            .connect(potionLp1)
            .createAndBuyOtokens(
              usdc.address,
              weth.address,
              usdc.address,
              12345,
              lowerStrikeInDollars,
              true,
              counterparties,
              ethers.constants.MaxUint256,
            ),
        ).to.be.revertedWith(`Pausable: paused`)
        await expect(
          potionLiquidityPool
            .connect(potionLp1)
            .buyOtokens(lowerStrikePut.address, counterparties, ethers.constants.MaxUint256),
        ).to.be.revertedWith(`Pausable: paused`)
      })

      it('settling after expiry disabled', async () => {
        await expect(
          potionLiquidityPool.connect(potionLp1).settleAfterExpiry(lowerStrikePut.address),
        ).to.be.revertedWith(`Pausable: paused`)
      })

      it('redistributing settlement disabled', async () => {
        await expect(
          potionLiquidityPool.connect(potionLp1).redistributeSettlement(lowerStrikePut.address, []),
        ).to.be.revertedWith(`Pausable: paused`)
      })

      describe('after contract upgrade', () => {
        before('upgrade contract', async () => {
          potionLiquidityPool = (await upgrades.upgradeProxy(
            potionLiquidityPool.address,
            PotionLiquidityPoolUpgradeTestFactory,
          )) as PotionLiquidityPool
        })

        it('contract cannot be unpaused by non-owners', async () => {
          await expect(potionLiquidityPool.connect(potionLp1).unpause()).to.be.revertedWith(
            `Ownable: caller is not the owner`,
          )
        })

        it('deposits disabled', async () => {
          await expect(potionLiquidityPool.connect(potionLp1).deposit(poolId1, 1)).to.be.revertedWith(
            `Pausable: paused`,
          )
          await expect(
            potionLiquidityPool.depositAndConfigurePool(poolId1, depositAmount, curveHash1, criteriaSetHash),
          ).to.be.revertedWith(`Pausable: paused`)
        })

        it('withdrawals disabled', async () => {
          await expect(potionLiquidityPool.connect(potionLp1).withdraw(poolId1, 1)).to.be.revertedWith(
            `Pausable: paused`,
          )
        })

        it('pool config disabled', async () => {
          await expect(
            potionLiquidityPool.connect(potionLp1).setCurveCriteria(poolId1, criteriaSetHash),
          ).to.be.revertedWith(`Pausable: paused`)
          await expect(potionLiquidityPool.connect(potionLp1).setCurve(poolId1, curveHash1)).to.be.revertedWith(
            `Pausable: paused`,
          )
        })

        it('creating (but not getting) vaults disabled', async () => {
          await potionLiquidityPool.getVaultId(lowerStrikePut.address)
          await expect(potionLiquidityPool.createNewVaultId(lowerStrikePut.address)).to.be.revertedWith(
            `Pausable: paused`,
          )
        })

        it('buying otokens disabled', async () => {
          const counterparties = [new CounterpartyDetails(potionLp1, poolId1, curve1, criteria1, BigNumber.from(1000))]
          await expect(
            potionLiquidityPool
              .connect(potionLp1)
              .createAndBuyOtokens(
                usdc.address,
                weth.address,
                usdc.address,
                12345,
                lowerStrikeInDollars,
                true,
                counterparties,
                ethers.constants.MaxUint256,
              ),
          ).to.be.revertedWith(`Pausable: paused`)
          await expect(
            potionLiquidityPool
              .connect(potionLp1)
              .buyOtokens(lowerStrikePut.address, counterparties, ethers.constants.MaxUint256),
          ).to.be.revertedWith(`Pausable: paused`)
        })

        it('settling after expiry disabled', async () => {
          await expect(
            potionLiquidityPool.connect(potionLp1).settleAfterExpiry(lowerStrikePut.address),
          ).to.be.revertedWith(`Pausable: paused`)
        })

        it('redistributing settlement disabled', async () => {
          await expect(
            potionLiquidityPool.connect(potionLp1).redistributeSettlement(lowerStrikePut.address, []),
          ).to.be.revertedWith(`Pausable: paused`)
        })

        it('owner can unpause', async () => {
          await potionLiquidityPool.unpause()
        })
      })
    })
  })
})
