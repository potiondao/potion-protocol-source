import type { Contract } from 'ethers'
import { network, ethers, upgrades } from 'hardhat'
import { PotionLiquidityPool } from '../typechain/'
import { config as deployConfiguration } from './lib/deployConfig'
import { Deployment } from '../deploy/deploymentConfig'
import { executePostDeployActions } from './lib/postDeploy'

const deployConfig = deployConfiguration[network.name]
if (!deployConfig) {
  throw new Error(`No deploy config found for network '${network.name}'`)
}
const ADDRESS_BOOK_CONTRACT_NAME = 'AddressBook'
const OTOKEN_FACTORY_CONTRACT_NAME = 'OtokenFactory'
const OTOKEN_CONTRACT_NAME = 'Otoken'
const WHITELIST_CONTRACT_NAME = 'Whitelist'
const ORACLE_CONTRACT_NAME = 'Oracle'
const MARGIN_POOL_CONTRACT_NAME = 'MarginPool'
const MARGIN_CALCULATOR_CONTRACT_NAME = 'MarginCalculator'
const CONTROLLER_CONTRACT_NAME = 'Controller'
const MARGIN_VAULT_LIB_NAME = 'MarginVaultLib'
const CONTRACTS_TO_DEPLOY_WITH_NO_PARAM = [OTOKEN_CONTRACT_NAME, ORACLE_CONTRACT_NAME]
const CONTRACTS_TO_DEPLOY_WITH_ORACLE_PARAM = [MARGIN_CALCULATOR_CONTRACT_NAME]
const CONTRACTS_TO_DEPLOY_WITH_ADDRESSBOOK_PARAM = [
  OTOKEN_FACTORY_CONTRACT_NAME,
  WHITELIST_CONTRACT_NAME,
  MARGIN_POOL_CONTRACT_NAME,
]
const contractAddresses = new Map()

async function init() {
  const deployer = (await ethers.provider.listAccounts())[0]
  console.log(`Using network ${network.name}`)
  console.log(`Deploying from ${deployer}`)
}

// Deploys a faucet token for use as test collateral, and returns its address
async function deployCollateralToken(): Promise<string> {
  const tokenFactory = await ethers.getContractFactory('PotionTestUSD')
  const tokenTrx = await tokenFactory.deploy()
  process.stdout.write(`Deploying test collateral token (PUSDC)...`)
  const token = await tokenTrx.deployed()
  console.log(` deployed at ${token.address}`)
  return token.address
}

async function updateAddressBook(addressbook: Contract) {
  console.log(`Updating address book at ${addressbook.address}:`)
  let trx = await addressbook.setOtokenFactory(contractAddresses.get(OTOKEN_FACTORY_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${OTOKEN_FACTORY_CONTRACT_NAME}         to ${await addressbook.getOtokenFactory()}`)
  trx = await addressbook.setOtokenImpl(contractAddresses.get(OTOKEN_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${OTOKEN_CONTRACT_NAME}                to ${await addressbook.getOtokenImpl()}`)
  trx = await addressbook.setWhitelist(contractAddresses.get(WHITELIST_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${WHITELIST_CONTRACT_NAME}             to ${await addressbook.getWhitelist()}`)
  trx = await addressbook.setOracle(contractAddresses.get(ORACLE_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${ORACLE_CONTRACT_NAME}                to ${await addressbook.getOracle()}`)
  trx = await addressbook.setMarginPool(contractAddresses.get(MARGIN_POOL_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${MARGIN_POOL_CONTRACT_NAME}            to ${await addressbook.getMarginPool()}`)
  trx = await addressbook.setMarginCalculator(contractAddresses.get(MARGIN_CALCULATOR_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${MARGIN_CALCULATOR_CONTRACT_NAME}      to ${await addressbook.getMarginCalculator()}`)
  trx = await addressbook.setController(contractAddresses.get(CONTROLLER_CONTRACT_NAME))
  await trx.wait()
  console.log(` - Set ${CONTROLLER_CONTRACT_NAME}            to ${await addressbook.getController()}`)
}

// Deploys all of the Opyn contracts and returns the address of the addressbook contract
async function deployOpynContracts(): Promise<string> {
  // Deploy the address book and other Opyn contracts
  const AddressBookFactory = await ethers.getContractFactory(ADDRESS_BOOK_CONTRACT_NAME)
  const addressBookDeployTrx = await AddressBookFactory.deploy()
  const addressbook = await addressBookDeployTrx.deployed()

  // Deploy contracts that take no constructor params
  for (const contractName of CONTRACTS_TO_DEPLOY_WITH_NO_PARAM) {
    const factory = await ethers.getContractFactory(contractName)
    const deployTrx = await factory.deploy()
    await deployTrx.deployed()
    contractAddresses.set(contractName, (await deployTrx.deployed()).address)
  }

  // Deploy contracts that take the oracle as a constructor param
  for (const contractName of CONTRACTS_TO_DEPLOY_WITH_ORACLE_PARAM) {
    const factory = await ethers.getContractFactory(contractName)
    const deployTrx = await factory.deploy(contractAddresses.get(ORACLE_CONTRACT_NAME))
    await deployTrx.deployed()
    contractAddresses.set(contractName, (await deployTrx.deployed()).address)
  }

  // Deploy contracts that take the address book as a constructor param
  for (const contractName of CONTRACTS_TO_DEPLOY_WITH_ADDRESSBOOK_PARAM) {
    const factory = await ethers.getContractFactory(contractName)
    const deployTrx = await factory.deploy(addressbook.address)
    await deployTrx.deployed()
    contractAddresses.set(contractName, (await deployTrx.deployed()).address)
  }

  // Deploy Controller including linked library
  const MarginVaultFactory = await ethers.getContractFactory('MarginVault')
  const marginVaultLib = await MarginVaultFactory.deploy()
  contractAddresses.set(MARGIN_VAULT_LIB_NAME, (await marginVaultLib.deployed()).address)

  const ControllerFactory = await ethers.getContractFactory(CONTROLLER_CONTRACT_NAME, {
    libraries: {
      MarginVault: marginVaultLib.address,
    },
  })
  const controllerDeployTrx = await ControllerFactory.deploy()
  await controllerDeployTrx.deployed()
  contractAddresses.set(CONTROLLER_CONTRACT_NAME, (await controllerDeployTrx.deployed()).address)

  await updateAddressBook(addressbook)
  return addressbook.address
}

async function main() {
  await init()

  if (!deployConfig.opynAddressBook) {
    deployConfig.opynAddressBook = await deployOpynContracts()
  }
  const AddressBookFactory = await ethers.getContractFactory('AddressBook')
  const addressBook = await AddressBookFactory.attach(deployConfig.opynAddressBook)
  const otokenFactoryAddress = await addressBook.getOtokenFactory()
  const whitelistAddress = await addressBook.getWhitelist()

  if (!deployConfig.collateralToken) {
    deployConfig.collateralToken = await deployCollateralToken()
  }

  process.stdout.write(`Deploying CurveManager... `)
  const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
  const curveManager = await CurveManagerFactory.deploy()
  await curveManager.deployed()
  console.log(`deployed at ${curveManager.address}`)
  process.stdout.write(`Deploying CriteriaManager... `)
  const CriteriaManagerFactory = await ethers.getContractFactory('CriteriaManager')
  const criteriaManager = await CriteriaManagerFactory.deploy()
  await criteriaManager.deployed()
  console.log(`deployed at ${criteriaManager.address}`)

  process.stdout.write(`Deploying PotionLiquidityPool... `)
  const PotionLiquidityPoolFactory = await ethers.getContractFactory('PotionLiquidityPool')
  const potionLiquidityPool = (await upgrades.deployProxy(PotionLiquidityPoolFactory, [
    deployConfig.opynAddressBook,
    deployConfig.collateralToken,
    curveManager.address,
    criteriaManager.address,
  ])) as PotionLiquidityPool
  await potionLiquidityPool.deployed()
  const configToPersist = new Deployment({
    opynAddressBookAddress: deployConfig.opynAddressBook,
    collateralTokenAddress: deployConfig.collateralToken,
    potionLiquidityPoolAddress: potionLiquidityPool.address,
    curveManagerAddress: curveManager.address,
    criteriaManagerAddress: criteriaManager.address,
    marginVaultLibAddress: contractAddresses.get(MARGIN_VAULT_LIB_NAME),
    otokenFactoryAddress: otokenFactoryAddress,
    whitelistAddress: whitelistAddress,
  })
  console.log(`deployed at ${potionLiquidityPool.address}`)

  // We persist now in case the post-deploy actions are long-running
  await configToPersist.persist()

  if (deployConfig.postDeployActions && deployConfig.postDeployActions.length > 0) {
    // Note that executePostDeployActions may persist updated config after every successful action
    await executePostDeployActions(deployConfig.postDeployActions, configToPersist, true)
  }

  // We persist again in case the post-deploy actions changed config
  await configToPersist.persist()
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })
