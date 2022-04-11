import { ethers, waffle, upgrades } from 'hardhat'
import { BigNumber, BigNumberish, Wallet } from 'ethers'
import { createScaledNumber as scaleNum, createValidExpiry } from './OpynUtils'
const provider = waffle.provider

import {
  MockERC20,
  MarginCalculator,
  AddressBook,
  MockOracle,
  Otoken as OtokenInstance,
  Controller,
  Whitelist,
  MarginPool,
  OtokenFactory, // Renamed from OtokenFactory for easy compatibility with hardhat-typechain, which generates a factory for the Otoken contract
  PotionLiquidityPool,
  CurveManager,
  CriteriaManager,
} from '../../typechain'

export const usdcDecimals = 6
export const wethDecimals = 18
export const EMPTY_HASH = '0x0000000000000000000000000000000000000000000000000000000000000000'

const startingEthPrice = 1500
export interface TestContracts {
  addressBook: AddressBook
  potionLiquidityPool: PotionLiquidityPool
  usdc: MockERC20
  weth: MockERC20
  marginPool: MarginPool
  otokenFactory: OtokenFactory
  oracle: MockOracle
  curveManager: CurveManager
  criteriaManager: CriteriaManager
  whitelist: Whitelist
}

export interface MintDestination {
  wallet: Wallet
  amount: BigNumberish
}

export async function mintTokens(
  token: MockERC20,
  mintings: MintDestination[],
  approveFullAllowanceToAddress: string,
): Promise<void> {
  for (const m of mintings) {
    await token.mint(m.wallet.address, m.amount)
    if (approveFullAllowanceToAddress) {
      await token.connect(m.wallet).approve(approveFullAllowanceToAddress, m.amount)
    }
  }
}

export async function deployTestContracts(): Promise<TestContracts> {
  const OtokenInstanceFactory = await ethers.getContractFactory('Otoken')
  const AddressBookFactory = await ethers.getContractFactory('AddressBook')
  const MockOracleFactory = await ethers.getContractFactory('MockOracle')
  const MockERC20Factory = await ethers.getContractFactory('MockERC20')
  const MarginCalculatorFactory = await ethers.getContractFactory('MarginCalculator')
  const WhitelistFactory = await ethers.getContractFactory('Whitelist')
  const MarginPoolFactory = await ethers.getContractFactory('MarginPool')
  const MarginVaultFactory = await ethers.getContractFactory('MarginVault')
  const OTokenFactoryFactory = await ethers.getContractFactory('OtokenFactory')
  const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
  const CriteriaManagerFactory = await ethers.getContractFactory('CriteriaManager')
  const PotionLiquidityPoolFactory = await ethers.getContractFactory('PotionLiquidityPool')

  // setup usdc and weth
  const usdc = (await MockERC20Factory.deploy('USDC', 'USDC', usdcDecimals)) as MockERC20
  const weth = (await MockERC20Factory.deploy('WETH', 'WETH', wethDecimals)) as MockERC20

  // initiate addressbook first.
  const addressBook = (await AddressBookFactory.deploy()) as AddressBook
  // setup mock Oracle module
  const oracle = (await MockOracleFactory.deploy()) as MockOracle
  await oracle.setRealTimePrice(weth.address, scaleNum(startingEthPrice))
  await oracle.setRealTimePrice(usdc.address, scaleNum(1))
  // setup calculator
  const calculator = (await MarginCalculatorFactory.deploy(oracle.address)) as MarginCalculator
  // setup margin pool
  const marginPool = (await MarginPoolFactory.deploy(addressBook.address)) as MarginPool
  // setup margin vault
  const lib = await MarginVaultFactory.deploy()
  // setup controllerProxy module
  const ControllerFactory = await ethers.getContractFactory('Controller', {
    libraries: {
      MarginVault: lib.address,
    },
  })
  const controllerImplementation = (await ControllerFactory.deploy()) as Controller

  // setup whitelist module
  const whitelist = (await WhitelistFactory.deploy(addressBook.address)) as Whitelist
  await whitelist.whitelistCollateral(usdc.address)
  await whitelist.whitelistCollateral(weth.address)
  await whitelist.whitelistProduct(weth.address, usdc.address, usdc.address, true)
  await whitelist.whitelistProduct(weth.address, usdc.address, weth.address, false)
  // setup otoken
  const otokenImplementation = (await OtokenInstanceFactory.deploy()) as OtokenInstance
  // setup factory
  const otokenFactory = ((await OTokenFactoryFactory.deploy(addressBook.address)) as unknown) as OtokenFactory

  // setup address book
  await addressBook.setOracle(oracle.address)
  await addressBook.setMarginCalculator(calculator.address)
  await addressBook.setWhitelist(whitelist.address)
  await addressBook.setMarginPool(marginPool.address)
  await addressBook.setOtokenFactory(otokenFactory.address)
  await addressBook.setOtokenImpl(otokenImplementation.address)
  await addressBook.setController(controllerImplementation.address)

  const controllerProxyAddress = await addressBook.getController()
  // controllerProxy = (await ControllerFactory.attach(controllerProxyAddress)) as Controller
  await ControllerFactory.attach(controllerProxyAddress)

  // Opyn contrafcts deployed. Now deploy the Potion contracts.
  const curveManager = (await CurveManagerFactory.deploy()) as CurveManager
  const criteriaManager = (await CriteriaManagerFactory.deploy()) as CriteriaManager
  const potionLiquidityPool = (await upgrades.deployProxy(PotionLiquidityPoolFactory, [
    addressBook.address,
    usdc.address,
    curveManager.address,
    criteriaManager.address,
  ])) as PotionLiquidityPool

  return {
    addressBook,
    potionLiquidityPool,
    usdc,
    weth,
    marginPool,
    otokenFactory,
    curveManager,
    criteriaManager,
    oracle,
    whitelist,
  }
}

export interface TestOtokens {
  put: OtokenInstance
  putAddress: string
  expiry: number
  scaledStrike: BigNumber
}

interface GetTestOtokenParams {
  otokenFactory: OtokenFactory
  strikeAsset: string
  underlyingAsset: string
  deploy: boolean
  strikeInDollars: number
  durationInDays?: number
  collateralAsset?: string
}

export const DEFAULT_DURATION_IN_DAYS = 30

export async function getTestOtoken({
  otokenFactory,
  strikeAsset,
  underlyingAsset,
  strikeInDollars,
  deploy,
  durationInDays,
  collateralAsset,
}: GetTestOtokenParams): Promise<TestOtokens> {
  collateralAsset = collateralAsset ? collateralAsset : strikeAsset
  const now = (await provider.getBlock('latest')).timestamp
  const expiry = createValidExpiry(now, durationInDays ? durationInDays : DEFAULT_DURATION_IN_DAYS)
  const scaledStrike = scaleNum(strikeInDollars)
  const OtokenInstanceFactory = await ethers.getContractFactory('Otoken')

  let address: string
  if (deploy) {
    await otokenFactory.createOtoken(underlyingAsset, strikeAsset, collateralAsset, scaledStrike, expiry, true)
    address = await otokenFactory.getOtoken(underlyingAsset, strikeAsset, collateralAsset, scaledStrike, expiry, true)
  } else {
    address = await otokenFactory.getTargetOtokenAddress(
      // const higherStrikePutAddress = await otokenFactory.getOtoken(
      underlyingAsset,
      strikeAsset,
      collateralAsset,
      scaledStrike,
      expiry,
      true,
    )
  }
  const put = (await OtokenInstanceFactory.attach(address)) as OtokenInstance
  const putAddress = put.address
  return { put, putAddress, expiry, scaledStrike }
}
