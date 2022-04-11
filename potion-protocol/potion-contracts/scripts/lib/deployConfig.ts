import { BigNumber, BigNumberish } from 'ethers'
import { AccountValue, PostDeployAction } from './postDeploy'
import {
  AllocateCollateralTokensFromFaucet,
  AllocateCollateralTokensToWalletsFromFaucet,
} from './postDeployActions/AllocateCollateralTokens'
import { FastForwardDays, FastForwardPastNextActiveOtokenExpiry } from './postDeployActions/FastForwardActions'
import {
  DeployCriteriaAndCriteriaSets,
  DeployCurves,
  generateOneCriteriaAndOneCriteriaSet,
  generateOneCurve,
} from './postDeployActions/CurveAndCriteriaActions'
import { InitializeSamplePoolsOfCapital } from './postDeployActions/InitializeSamplePoolsOfCapital'
import { InitializeMockOracle, UpdateMockOraclePrices } from './postDeployActions/MockOracleActions'
import { WhitelistCollateral } from './postDeployActions/WhitelistCollateral'
import { DeploySampleUnderlyingToken } from './postDeployActions/DeploySampleUnderlyingToken'
import { CreateOtokens, InitializeSamplePurchases } from './postDeployActions/OtokensAndPurchaseActions'
import { SettleAllExpiredOtokens } from './postDeployActions/SettleAllExpiredOtokens'
import { priceHistory1 } from './postDeployActions/dataForImport/priceHistory.json'

function parseUsdcAmount(dollars: BigNumberish): BigNumber {
  return BigNumber.from(dollars).mul(1e6)
}
interface NetworkConfig {
  collateralToken?: string
  opynAddressBook?: string
  sampleUnderlyingToken?: string
  postDeployActions: PostDeployAction[]
  whitelistedTokenAddresses?: string[]
}
interface NetworkConfigMap {
  [networkName: string]: NetworkConfig
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const basicDataForTesting = (): PostDeployAction[] => {
  return [
    new WhitelistCollateral(),
    new DeploySampleUnderlyingToken('WETH'),
    new DeploySampleUnderlyingToken('WBTC'),
    new DeploySampleUnderlyingToken('UNI'),
    new DeploySampleUnderlyingToken('SUSHI'),
    new DeploySampleUnderlyingToken('AAVE'),
    new DeploySampleUnderlyingToken('DPI'),
    new AllocateCollateralTokensFromFaucet(EXTERNAL_COLLATERAL_ALLOCATIONS),
    new AllocateCollateralTokensToWalletsFromFaucet(parseUsdcAmount('1000000')),
    new DeployCurves(),
    new DeployCriteriaAndCriteriaSets(),
    new FastForwardDays(2),
    new InitializeSamplePoolsOfCapital(),
    new InitializeMockOracle(1500),
    new CreateOtokens(),
    new InitializeSamplePurchases(),
    new SettleAllExpiredOtokens(),
    new FastForwardDays(60),
    new UpdateMockOraclePrices(1400),
    new SettleAllExpiredOtokens(),
    new FastForwardPastNextActiveOtokenExpiry(),
    new UpdateMockOraclePrices(1300),
    new SettleAllExpiredOtokens(),
  ]
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const priceHistoryData = (): PostDeployAction[] => {
  const priceHistory = priceHistory1
  let price = 1500
  const pdas: PostDeployAction[] = [
    new WhitelistCollateral(),
    new DeploySampleUnderlyingToken(),
    new AllocateCollateralTokensFromFaucet(EXTERNAL_COLLATERAL_ALLOCATIONS),
    new AllocateCollateralTokensToWalletsFromFaucet(parseUsdcAmount('1000000')),
    new DeployCurves(generateOneCurve),
    new DeployCriteriaAndCriteriaSets(generateOneCriteriaAndOneCriteriaSet),
    new FastForwardDays(2),
    new InitializeSamplePoolsOfCapital(),
    new InitializeMockOracle(priceHistory[0]),
  ]
  for (let i = 1; i < priceHistory.length; i++) {
    price = priceHistory[i]
    pdas.push(
      new CreateOtokens(),
      new InitializeSamplePurchases(1),
      new FastForwardPastNextActiveOtokenExpiry(),
      new UpdateMockOraclePrices(price),
      new SettleAllExpiredOtokens(),
    )
  }
  return pdas
}

const EXTERNAL_COLLATERAL_ALLOCATIONS = [
  // Team
  new AccountValue('0x2c5eDB7F0EF80C7aBea2D2b7bF9Da96823Ec935d', parseUsdcAmount('1000000')), // G
  new AccountValue('0x46BD46A8C0DcB4Ca501c4A5624B1F09Ba86ff8F6', parseUsdcAmount('1000000')), // N
  new AccountValue('0x614B7f7Ed8E93260B6EA33BB081073036F73F9E9', parseUsdcAmount('1000000')), // E
]

const newSelfContainedEcosystemConfig = {
  postDeployActions: basicDataForTesting(),
  // postDeployActions: priceHistoryData(),
}

export const config: NetworkConfigMap = {
  // The default kovan network deploys Potion on top of contracts that were deployed and are controlled by Opyn
  kovan: {
    collateralToken: '0x7e6edA50d1c833bE936492BF42C1BF376239E9e2',
    opynAddressBook: '0x8812f219f507e8cfe9d2f1e790164714c5e06a73',
    postDeployActions: [
      new AllocateCollateralTokensFromFaucet(EXTERNAL_COLLATERAL_ALLOCATIONS),
      new AllocateCollateralTokensToWalletsFromFaucet(parseUsdcAmount('1000000'), false),
    ],
    whitelistedTokenAddresses: ['0x50570256f0da172a1908207aAf0c80d4b279f303'],
  },
  // The kovan.independent deployment deploys Opyn and Potion from the ground up, so that we control even the Opyn contracts
  'kovan.independent': {
    postDeployActions: [
      new WhitelistCollateral(),
      new DeploySampleUnderlyingToken('PTNETH'),
      new DeploySampleUnderlyingToken('PTNUNI'),
      new DeploySampleUnderlyingToken('PTNLINK'),
      new AllocateCollateralTokensFromFaucet(EXTERNAL_COLLATERAL_ALLOCATIONS),
      new AllocateCollateralTokensToWalletsFromFaucet(parseUsdcAmount('1000000')),
      new DeployCurves(),
      new DeployCriteriaAndCriteriaSets(),
      new InitializeMockOracle(1500),
      new InitializeSamplePoolsOfCapital(),
      new UpdateMockOraclePrices(1400),
    ],
  },
  goerli: newSelfContainedEcosystemConfig,
  localhost: newSelfContainedEcosystemConfig,
  ganache: newSelfContainedEcosystemConfig,
  hardhat: newSelfContainedEcosystemConfig,
  mainnet: {
    collateralToken: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    opynAddressBook: '0x1E31F2DCBad4dc572004Eae6355fB18F9615cBe4',
    postDeployActions: [],
  },
}
