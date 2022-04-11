import '@nomiclabs/hardhat-ethers'
import '@nomiclabs/hardhat-waffle'
import '@nomiclabs/hardhat-solhint'
import 'hardhat-typechain'
import 'hardhat-gas-reporter'
import 'solidity-coverage'
import '@openzeppelin/hardhat-upgrades'
import 'hardhat-contract-sizer'
import 'hardhat-abi-exporter'

import { HardhatUserConfig, task, types } from 'hardhat/config'
import accounts from './test/Accounts'
import { config as dotEnvConfig } from 'dotenv'

dotEnvConfig()

task('fastForward', 'Fast forward time (only works for local test networks)')
  .addOptionalParam(
    'seconds',
    'Number of seconds by which the blockchain should advance time (default: one year)',
    31556952,
    types.int,
  )
  .setAction(async (args, hre) => {
    // Default to one year
    await hre.ethers.provider.send('evm_increaseTime', [args.seconds])
    await hre.ethers.provider.send('evm_mine', [])
    console.log(`Fast forwarded time by ${args.seconds} seconds (${args.seconds / (60 * 60 * 24)} days)`)
  })

task('setPrices', 'Call the Oracle to set current prices for tokens, and/or to set expiry prices for otokens')
  .addOptionalParam('token', 'The token to set the price for (optional)', '', types.string)
  .addOptionalParam('otoken', 'The otoken to set the expiry prices for (optional)', '', types.string)
  .addParam('price', 'The price in dollars', undefined, types.float, false)
  .setAction(async (args) => {
    if (args.otoken) {
      // Import using require to avoid circular dependencies
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { setExpiryPrice } = require('./scripts/lib/setExpiryPrice')
      console.log(`Processing otoken ${args.otoken}`)
      await setExpiryPrice(args.otoken, args.price)
    }
    if (args.token) {
      // Import using require to avoid circular dependencies
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { setPrice } = require('./scripts/lib/setCurrentPrice')
      console.log(`Processing token ${args.token}`)
      await setPrice(args.token, args.price)
    }
  })

const config: HardhatUserConfig = {
  defaultNetwork: 'hardhat',
  solidity: {
    compilers: [
      {
        version: '0.8.4',
        settings: {
          optimizer: {
            enabled: true,
          },
        },
      },
      {
        version: '0.6.10',
        settings: {
          optimizer: {
            enabled: true,
          },
        },
      },
    ],
  },
  paths: {
    sources: './contracts',
    artifacts: './artifacts',
  },
  networks: {
    hardhat: {
      loggingEnabled: false,
      accounts: accounts,
    },
    ganache: {
      url: 'http://127.0.0.1:8545',
      loggingEnabled: false,
      accounts: {
        mnemonic: `${process.env.GANACHE_MNEMONIC}`,
        count: 10,
      },
    },
    // The default kovan network deploys Potion on top of contracts that were deployed and are controlled by Opyn
    kovan: {
      url: `${process.env.KOVAN_WEB3_ENDPOINT}`,
      accounts: {
        mnemonic: `${process.env.KOVAN_MNEMONIC}`,
        count: 10,
      },
      chainId: 42,
      loggingEnabled: true,
      gas: 'auto',
      gasPrice: 'auto',
    },
    // The kovan.independent deployment deploys Opyn and Potion from the ground up, so that we control even the Opyn contracts
    'kovan.independent': {
      url: `${process.env.KOVAN_WEB3_ENDPOINT}`,
      accounts: {
        mnemonic: `${process.env.KOVAN_MNEMONIC}`,
        count: 10,
      },
      chainId: 42,
      loggingEnabled: true,
      gas: 'auto',
      gasPrice: 'auto',
    },
    mainnet: {
      url: `${process.env.MAINNET_WEB3_ENDPOINT}`,
      accounts: {
        mnemonic: `${process.env.MAINNET_MNEMONIC}`,
      },
    },
  },
  gasReporter: {
    outputFile: process.env.REPORT_GAS_TO_FILE,
    coinmarketcap: `${process.env.COINMARKETCAP_API_KEY}`,
    enabled: !!(process.env.REPORT_GAS && process.env.REPORT_GAS != 'false'),
  },
  typechain: {
    outDir: 'typechain',
    target: 'ethers-v5',
  },
  abiExporter: {
    path: './abis',
    clear: true,
    flat: true,
    only: [
      // There are lots of contracts, which have many direct and indirect dependencies
      // To avoid clutter, we only export the ABIs that we need
      // As we are flattening the output, we must also take care not to avoid duplicate contract names or one will overwrite the other
      // These are generally used in the vue or subgraph code to test or interact with our contracts
      ':PotionLiquidityPool$',
      ':ICriteriaManager$',
      ':ICurveManager$',
      ':IERC20MetadataUpgradeable$',
      ':ERC20$',
      // scripts/compareAbis.ts checks that our interface definitions are up to date
      // To facilitate this, we dump ABIs for our interfaces and for each of the contracts they represent
      // Some of these are alos required for the vue or subgraph code
      'opynInterface/*',
      'gamma-protocol.*:Otoken$',
      'gamma-protocol.*:OtokenFactory$',
      'gamma-protocol.*:Whitelist$',
      'gamma-protocol.*:Controller$',
      'gamma-protocol.*:AddressBook$',
      'gamma-protocol.*:MarginCalculator$',
      'gamma-protocol.*:Oracle$',
    ],
  },
}

export default config
