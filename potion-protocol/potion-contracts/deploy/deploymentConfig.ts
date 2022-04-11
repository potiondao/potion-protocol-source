import { ethers, network } from 'hardhat'
import fs from 'fs'
import {
  AddressBook,
  Controller,
  CriteriaManager,
  CurveManager,
  FaucetToken,
  MockERC20,
  MockOracle,
  OtokenFactory,
  PotionLiquidityPool,
  Whitelist,
} from '../typechain'
const fsPromises = fs.promises

export interface DeploymentAddresses {
  collateralTokenAddress: string
  opynAddressBookAddress: string
  potionLiquidityPoolAddress: string
  curveManagerAddress: string
  criteriaManagerAddress: string
  marginVaultLibAddress: string
  otokenFactoryAddress: string // Required by subgraph config
  whitelistAddress: string // Required by subgraph config
  network?: string // hardhat network name
  theGraphNetworkName?: string // for subgraph definition; n/a on localhost
  sampleUnderlyingTokenAddress?: string // Populated iff we have deployed a single, sample underlying token for testing purposes
  oracleIsMock?: boolean
  whitelistedTokens?: string[]
}

export class Deployment implements DeploymentAddresses {
  public collateralTokenAddress: string
  public opynAddressBookAddress: string
  public potionLiquidityPoolAddress: string
  public curveManagerAddress: string
  public criteriaManagerAddress: string
  public marginVaultLibAddress: string
  public otokenFactoryAddress: string // Required by subgraph config
  public whitelistAddress: string // Required by subgraph config
  public network?: string // hardhat network name
  public theGraphNetworkName?: string // for subgraph definition; n/a on localhost
  public sampleUnderlyingTokenAddress?: string // Populated iff we have deployed a single, sample underlying token for testing purposes
  public mockOracleAddress?: string
  public oracleIsMock?: boolean

  public constructor(a: DeploymentAddresses) {
    this.collateralTokenAddress = a.collateralTokenAddress
    this.opynAddressBookAddress = a.opynAddressBookAddress
    this.potionLiquidityPoolAddress = a.potionLiquidityPoolAddress
    this.curveManagerAddress = a.curveManagerAddress
    this.criteriaManagerAddress = a.criteriaManagerAddress
    this.marginVaultLibAddress = a.marginVaultLibAddress
    this.otokenFactoryAddress = a.otokenFactoryAddress
    this.whitelistAddress = a.whitelistAddress
    this.network = a.network
    this.theGraphNetworkName = a.theGraphNetworkName
    this.sampleUnderlyingTokenAddress = a.sampleUnderlyingTokenAddress
    this.oracleIsMock = a.oracleIsMock
  }

  public static async getConfig(_network = network.name): Promise<Deployment> {
    try {
      const config = await import(`${__dirname}/${_network}.json`)
      return new Deployment(config as DeploymentAddresses)
    } catch (err) {
      throw new Error(`No valid config found for network '${_network}'`)
    }
  }

  public async faucetToken(): Promise<FaucetToken> {
    const FauctetTokenFactory = await ethers.getContractFactory('FaucetToken')
    const contract = await FauctetTokenFactory.attach(this.collateralTokenAddress)
    return contract as FaucetToken
  }

  public async faucetTokenAsMock(): Promise<MockERC20> {
    const MockERC20Factory = await ethers.getContractFactory('MockERC20')
    const contract = await MockERC20Factory.attach(this.collateralTokenAddress)
    return contract as MockERC20
  }

  public async potionLiquidityPool(): Promise<PotionLiquidityPool> {
    const PotionLiquidityPool = await ethers.getContractFactory('PotionLiquidityPool')
    const contract = await PotionLiquidityPool.attach(this.potionLiquidityPoolAddress)
    return contract as PotionLiquidityPool
  }

  public async addressBook(): Promise<AddressBook> {
    const AddressBook = await ethers.getContractFactory('AddressBook')
    const contract = await AddressBook.attach(this.opynAddressBookAddress)
    return contract as AddressBook
  }

  public async curveManager(): Promise<CurveManager> {
    const CurveManager = await ethers.getContractFactory('CurveManager')
    const contract = await CurveManager.attach(this.curveManagerAddress)
    return contract as CurveManager
  }

  public async criteriaManager(): Promise<CriteriaManager> {
    const CriteriaManager = await ethers.getContractFactory('CriteriaManager')
    const contract = await CriteriaManager.attach(this.criteriaManagerAddress)
    return contract as CriteriaManager
  }

  public async otokenFactory(): Promise<OtokenFactory> {
    const OtokenFactory = await ethers.getContractFactory('OtokenFactory')
    const address = await (await this.addressBook()).getOtokenFactory()
    const contract = await OtokenFactory.attach(address)
    return contract as OtokenFactory
  }

  public async whitelist(): Promise<Whitelist> {
    const Whitelist = await ethers.getContractFactory('Whitelist')
    const address = await (await this.addressBook()).getWhitelist()
    const contract = await Whitelist.attach(address)
    return contract as Whitelist
  }

  public async mockedOracle(): Promise<MockOracle> {
    if (!this.oracleIsMock) {
      throw new Error('Not a mock oracle!')
    }
    const Factory = await ethers.getContractFactory('MockOracle')
    const address = await (await this.addressBook()).getOracle()
    const contract = await Factory.attach(address)
    return contract as MockOracle
  }

  public async controller(): Promise<Controller> {
    const ControllerFactory = await ethers.getContractFactory('Controller', {
      libraries: {
        MarginVault: this.marginVaultLibAddress,
      },
    })
    const address = await (await this.addressBook()).getController()
    const contract = await ControllerFactory.attach(address)
    return contract as Controller
  }

  public async persist(_network = network.name): Promise<void> {
    this.network = this.network || _network
    this.theGraphNetworkName = this.theGraphNetworkName || Deployment.theGraphNetworkName(_network)
    await fsPromises.writeFile(`${__dirname}/${_network}.json`, JSON.stringify(this, Deployment.skipDefaultKey, 2))
  }

  private static theGraphNetworkName(_networkName: string): string {
    if (['ganache', 'localhost', 'hardhat'].includes(_networkName)) {
      // These networks are not supported by thegraph's hosted service, but we are running locally so we don't care
      // Default to 'mainnet' so that thegraph's subgraph can be deployed
      return 'mainnet'
    } else if (_networkName.startsWith('kovan')) {
      return 'kovan'
    } else {
      return _networkName
    }
  }

  private static skipDefaultKey(key: string, value: string): string | undefined {
    if (key == 'default') return undefined
    else return value
  }
}
