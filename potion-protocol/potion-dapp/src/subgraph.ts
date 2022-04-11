export type Maybe<T> = T | null;
export type Exact<T extends { [key: string]: unknown }> = {
  [K in keyof T]: T[K];
};
export type MakeOptional<T, K extends keyof T> = Omit<T, K> &
  {
    [SubKey in K]?: Maybe<T[SubKey]>;
  };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> &
  {
    [SubKey in K]: Maybe<T[SubKey]>;
  };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: string;
  String: string;
  Boolean: boolean;
  Int: number;
  Float: number;
  BigDecimal: any;
  BigInt: any;
  Bytes: any;
};

export type Block_Height = {
  hash?: Maybe<Scalars["Bytes"]>;
  number?: Maybe<Scalars["Int"]>;
};

/**
 * This entity exists for unique combination of buyer's wallet address
 * and oToken. It tracks the amount of oTokens purchased (for this specific oToken)
 * and the amount of premium paid to the LPs.
 *
 */
export type BuyerRecord = {
  __typename?: "BuyerRecord";
  id: Scalars["ID"];
  buyer: Scalars["Bytes"];
  otoken: OToken;
  premium: Scalars["BigDecimal"];
  numberOfOTokens: Scalars["BigDecimal"];
};

export type BuyerRecord_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  buyer?: Maybe<Scalars["Bytes"]>;
  buyer_not?: Maybe<Scalars["Bytes"]>;
  buyer_in?: Maybe<Array<Scalars["Bytes"]>>;
  buyer_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  buyer_contains?: Maybe<Scalars["Bytes"]>;
  buyer_not_contains?: Maybe<Scalars["Bytes"]>;
  otoken?: Maybe<Scalars["String"]>;
  otoken_not?: Maybe<Scalars["String"]>;
  otoken_gt?: Maybe<Scalars["String"]>;
  otoken_lt?: Maybe<Scalars["String"]>;
  otoken_gte?: Maybe<Scalars["String"]>;
  otoken_lte?: Maybe<Scalars["String"]>;
  otoken_in?: Maybe<Array<Scalars["String"]>>;
  otoken_not_in?: Maybe<Array<Scalars["String"]>>;
  otoken_contains?: Maybe<Scalars["String"]>;
  otoken_not_contains?: Maybe<Scalars["String"]>;
  otoken_starts_with?: Maybe<Scalars["String"]>;
  otoken_not_starts_with?: Maybe<Scalars["String"]>;
  otoken_ends_with?: Maybe<Scalars["String"]>;
  otoken_not_ends_with?: Maybe<Scalars["String"]>;
  premium?: Maybe<Scalars["BigDecimal"]>;
  premium_not?: Maybe<Scalars["BigDecimal"]>;
  premium_gt?: Maybe<Scalars["BigDecimal"]>;
  premium_lt?: Maybe<Scalars["BigDecimal"]>;
  premium_gte?: Maybe<Scalars["BigDecimal"]>;
  premium_lte?: Maybe<Scalars["BigDecimal"]>;
  premium_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premium_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_not?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum BuyerRecord_OrderBy {
  Id = "id",
  Buyer = "buyer",
  Otoken = "otoken",
  Premium = "premium",
  NumberOfOTokens = "numberOfOTokens",
}

export type Collateral = {
  __typename?: "Collateral";
  id: Scalars["ID"];
  token: Token;
};

export type Collateral_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  token?: Maybe<Scalars["String"]>;
  token_not?: Maybe<Scalars["String"]>;
  token_gt?: Maybe<Scalars["String"]>;
  token_lt?: Maybe<Scalars["String"]>;
  token_gte?: Maybe<Scalars["String"]>;
  token_lte?: Maybe<Scalars["String"]>;
  token_in?: Maybe<Array<Scalars["String"]>>;
  token_not_in?: Maybe<Array<Scalars["String"]>>;
  token_contains?: Maybe<Scalars["String"]>;
  token_not_contains?: Maybe<Scalars["String"]>;
  token_starts_with?: Maybe<Scalars["String"]>;
  token_not_starts_with?: Maybe<Scalars["String"]>;
  token_ends_with?: Maybe<Scalars["String"]>;
  token_not_ends_with?: Maybe<Scalars["String"]>;
};

export enum Collateral_OrderBy {
  Id = "id",
  Token = "token",
}

/**
 * All Criteria's in the registry of criterias.
 *
 */
export type Criteria = {
  __typename?: "Criteria";
  id: Scalars["ID"];
  underlyingAsset: Token;
  strikeAsset: Token;
  isPut: Scalars["Boolean"];
  maxStrikePercent: Scalars["BigDecimal"];
  maxDurationInDays: Scalars["BigInt"];
  criteriaSets: Array<Maybe<CriteriaJoinedCriteriaSet>>;
};

/**
 * All Criteria's in the registry of criterias.
 *
 */
export type CriteriaCriteriaSetsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaJoinedCriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaJoinedCriteriaSet_Filter>;
};

/**
 * Each CriteriaJoinedCriteriaSet entity describes one Criteria that belongs
 * to a CriteriaSet. This entiy allows for searches from Criterias to CriteriaSets
 * to be completed.
 *
 */
export type CriteriaJoinedCriteriaSet = {
  __typename?: "CriteriaJoinedCriteriaSet";
  id: Scalars["ID"];
  criteriaSet: CriteriaSet;
  criteria: Criteria;
};

export type CriteriaJoinedCriteriaSet_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  criteriaSet?: Maybe<Scalars["String"]>;
  criteriaSet_not?: Maybe<Scalars["String"]>;
  criteriaSet_gt?: Maybe<Scalars["String"]>;
  criteriaSet_lt?: Maybe<Scalars["String"]>;
  criteriaSet_gte?: Maybe<Scalars["String"]>;
  criteriaSet_lte?: Maybe<Scalars["String"]>;
  criteriaSet_in?: Maybe<Array<Scalars["String"]>>;
  criteriaSet_not_in?: Maybe<Array<Scalars["String"]>>;
  criteriaSet_contains?: Maybe<Scalars["String"]>;
  criteriaSet_not_contains?: Maybe<Scalars["String"]>;
  criteriaSet_starts_with?: Maybe<Scalars["String"]>;
  criteriaSet_not_starts_with?: Maybe<Scalars["String"]>;
  criteriaSet_ends_with?: Maybe<Scalars["String"]>;
  criteriaSet_not_ends_with?: Maybe<Scalars["String"]>;
  criteria?: Maybe<Scalars["String"]>;
  criteria_not?: Maybe<Scalars["String"]>;
  criteria_gt?: Maybe<Scalars["String"]>;
  criteria_lt?: Maybe<Scalars["String"]>;
  criteria_gte?: Maybe<Scalars["String"]>;
  criteria_lte?: Maybe<Scalars["String"]>;
  criteria_in?: Maybe<Array<Scalars["String"]>>;
  criteria_not_in?: Maybe<Array<Scalars["String"]>>;
  criteria_contains?: Maybe<Scalars["String"]>;
  criteria_not_contains?: Maybe<Scalars["String"]>;
  criteria_starts_with?: Maybe<Scalars["String"]>;
  criteria_not_starts_with?: Maybe<Scalars["String"]>;
  criteria_ends_with?: Maybe<Scalars["String"]>;
  criteria_not_ends_with?: Maybe<Scalars["String"]>;
};

export enum CriteriaJoinedCriteriaSet_OrderBy {
  Id = "id",
  CriteriaSet = "criteriaSet",
  Criteria = "criteria",
}

export type CriteriaSet = {
  __typename?: "CriteriaSet";
  id: Scalars["ID"];
  criterias: Array<CriteriaJoinedCriteriaSet>;
  templates: Array<Maybe<Template>>;
};

export type CriteriaSetCriteriasArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaJoinedCriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaJoinedCriteriaSet_Filter>;
};

export type CriteriaSetTemplatesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Template_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Template_Filter>;
};

export type CriteriaSet_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
};

export enum CriteriaSet_OrderBy {
  Id = "id",
  Criterias = "criterias",
  Templates = "templates",
}

export type Criteria_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  underlyingAsset?: Maybe<Scalars["String"]>;
  underlyingAsset_not?: Maybe<Scalars["String"]>;
  underlyingAsset_gt?: Maybe<Scalars["String"]>;
  underlyingAsset_lt?: Maybe<Scalars["String"]>;
  underlyingAsset_gte?: Maybe<Scalars["String"]>;
  underlyingAsset_lte?: Maybe<Scalars["String"]>;
  underlyingAsset_in?: Maybe<Array<Scalars["String"]>>;
  underlyingAsset_not_in?: Maybe<Array<Scalars["String"]>>;
  underlyingAsset_contains?: Maybe<Scalars["String"]>;
  underlyingAsset_not_contains?: Maybe<Scalars["String"]>;
  underlyingAsset_starts_with?: Maybe<Scalars["String"]>;
  underlyingAsset_not_starts_with?: Maybe<Scalars["String"]>;
  underlyingAsset_ends_with?: Maybe<Scalars["String"]>;
  underlyingAsset_not_ends_with?: Maybe<Scalars["String"]>;
  strikeAsset?: Maybe<Scalars["String"]>;
  strikeAsset_not?: Maybe<Scalars["String"]>;
  strikeAsset_gt?: Maybe<Scalars["String"]>;
  strikeAsset_lt?: Maybe<Scalars["String"]>;
  strikeAsset_gte?: Maybe<Scalars["String"]>;
  strikeAsset_lte?: Maybe<Scalars["String"]>;
  strikeAsset_in?: Maybe<Array<Scalars["String"]>>;
  strikeAsset_not_in?: Maybe<Array<Scalars["String"]>>;
  strikeAsset_contains?: Maybe<Scalars["String"]>;
  strikeAsset_not_contains?: Maybe<Scalars["String"]>;
  strikeAsset_starts_with?: Maybe<Scalars["String"]>;
  strikeAsset_not_starts_with?: Maybe<Scalars["String"]>;
  strikeAsset_ends_with?: Maybe<Scalars["String"]>;
  strikeAsset_not_ends_with?: Maybe<Scalars["String"]>;
  isPut?: Maybe<Scalars["Boolean"]>;
  isPut_not?: Maybe<Scalars["Boolean"]>;
  isPut_in?: Maybe<Array<Scalars["Boolean"]>>;
  isPut_not_in?: Maybe<Array<Scalars["Boolean"]>>;
  maxStrikePercent?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_not?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_gt?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_lt?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_gte?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_lte?: Maybe<Scalars["BigDecimal"]>;
  maxStrikePercent_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  maxStrikePercent_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  maxDurationInDays?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_not?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_gt?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_lt?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_gte?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_lte?: Maybe<Scalars["BigInt"]>;
  maxDurationInDays_in?: Maybe<Array<Scalars["BigInt"]>>;
  maxDurationInDays_not_in?: Maybe<Array<Scalars["BigInt"]>>;
};

export enum Criteria_OrderBy {
  Id = "id",
  UnderlyingAsset = "underlyingAsset",
  StrikeAsset = "strikeAsset",
  IsPut = "isPut",
  MaxStrikePercent = "maxStrikePercent",
  MaxDurationInDays = "maxDurationInDays",
  CriteriaSets = "criteriaSets",
}

/**
 * Describes a curve evaluated at 0 <= x <= maxUtil:
 *   a * x * cosh(b*x^c) + d
 *
 */
export type Curve = {
  __typename?: "Curve";
  id: Scalars["ID"];
  a: Scalars["BigDecimal"];
  b: Scalars["BigDecimal"];
  c: Scalars["BigDecimal"];
  d: Scalars["BigDecimal"];
  maxUtil: Scalars["BigDecimal"];
  templates: Array<Template>;
};

/**
 * Describes a curve evaluated at 0 <= x <= maxUtil:
 *   a * x * cosh(b*x^c) + d
 *
 */
export type CurveTemplatesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Template_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Template_Filter>;
};

export type Curve_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  a?: Maybe<Scalars["BigDecimal"]>;
  a_not?: Maybe<Scalars["BigDecimal"]>;
  a_gt?: Maybe<Scalars["BigDecimal"]>;
  a_lt?: Maybe<Scalars["BigDecimal"]>;
  a_gte?: Maybe<Scalars["BigDecimal"]>;
  a_lte?: Maybe<Scalars["BigDecimal"]>;
  a_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  a_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  b?: Maybe<Scalars["BigDecimal"]>;
  b_not?: Maybe<Scalars["BigDecimal"]>;
  b_gt?: Maybe<Scalars["BigDecimal"]>;
  b_lt?: Maybe<Scalars["BigDecimal"]>;
  b_gte?: Maybe<Scalars["BigDecimal"]>;
  b_lte?: Maybe<Scalars["BigDecimal"]>;
  b_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  b_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  c?: Maybe<Scalars["BigDecimal"]>;
  c_not?: Maybe<Scalars["BigDecimal"]>;
  c_gt?: Maybe<Scalars["BigDecimal"]>;
  c_lt?: Maybe<Scalars["BigDecimal"]>;
  c_gte?: Maybe<Scalars["BigDecimal"]>;
  c_lte?: Maybe<Scalars["BigDecimal"]>;
  c_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  c_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  d?: Maybe<Scalars["BigDecimal"]>;
  d_not?: Maybe<Scalars["BigDecimal"]>;
  d_gt?: Maybe<Scalars["BigDecimal"]>;
  d_lt?: Maybe<Scalars["BigDecimal"]>;
  d_gte?: Maybe<Scalars["BigDecimal"]>;
  d_lte?: Maybe<Scalars["BigDecimal"]>;
  d_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  d_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  maxUtil?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_not?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_gt?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_lt?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_gte?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_lte?: Maybe<Scalars["BigDecimal"]>;
  maxUtil_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  maxUtil_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum Curve_OrderBy {
  Id = "id",
  A = "a",
  B = "b",
  C = "c",
  D = "d",
  MaxUtil = "maxUtil",
  Templates = "templates",
}

/**
 * This entity exists for every unique combination of LP and oToken address.
 * Note that this is aggregated at the LP level and not at the pool level.
 * This is done to make reclaiming done easier.
 *
 * It tracks the number of oTokens underwritten, the total liquidityCollateralized,
 * and the total premiumReceived for all oTokens.
 *
 * It also contains the field poolRecords, for every pool by the same LP that has backed
 * the same oToken, there exists an entry that describes the collateral of each pool.
 *
 */
export type LpRecord = {
  __typename?: "LPRecord";
  id: Scalars["ID"];
  lp: Scalars["Bytes"];
  otoken: OToken;
  numberOfOTokens: Scalars["BigDecimal"];
  liquidityCollateralized: Scalars["BigDecimal"];
  premiumReceived: Scalars["BigDecimal"];
  poolRecords: Array<PoolRecord>;
};

/**
 * This entity exists for every unique combination of LP and oToken address.
 * Note that this is aggregated at the LP level and not at the pool level.
 * This is done to make reclaiming done easier.
 *
 * It tracks the number of oTokens underwritten, the total liquidityCollateralized,
 * and the total premiumReceived for all oTokens.
 *
 * It also contains the field poolRecords, for every pool by the same LP that has backed
 * the same oToken, there exists an entry that describes the collateral of each pool.
 *
 */
export type LpRecordPoolRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolRecord_Filter>;
};

export type LpRecord_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  lp?: Maybe<Scalars["Bytes"]>;
  lp_not?: Maybe<Scalars["Bytes"]>;
  lp_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_contains?: Maybe<Scalars["Bytes"]>;
  lp_not_contains?: Maybe<Scalars["Bytes"]>;
  otoken?: Maybe<Scalars["String"]>;
  otoken_not?: Maybe<Scalars["String"]>;
  otoken_gt?: Maybe<Scalars["String"]>;
  otoken_lt?: Maybe<Scalars["String"]>;
  otoken_gte?: Maybe<Scalars["String"]>;
  otoken_lte?: Maybe<Scalars["String"]>;
  otoken_in?: Maybe<Array<Scalars["String"]>>;
  otoken_not_in?: Maybe<Array<Scalars["String"]>>;
  otoken_contains?: Maybe<Scalars["String"]>;
  otoken_not_contains?: Maybe<Scalars["String"]>;
  otoken_starts_with?: Maybe<Scalars["String"]>;
  otoken_not_starts_with?: Maybe<Scalars["String"]>;
  otoken_ends_with?: Maybe<Scalars["String"]>;
  otoken_not_ends_with?: Maybe<Scalars["String"]>;
  numberOfOTokens?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_not?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityCollateralized?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_not?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_gt?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_lt?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_gte?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_lte?: Maybe<Scalars["BigDecimal"]>;
  liquidityCollateralized_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityCollateralized_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premiumReceived?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_not?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_gt?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_lt?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_gte?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_lte?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premiumReceived_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum LpRecord_OrderBy {
  Id = "id",
  Lp = "lp",
  Otoken = "otoken",
  NumberOfOTokens = "numberOfOTokens",
  LiquidityCollateralized = "liquidityCollateralized",
  PremiumReceived = "premiumReceived",
  PoolRecords = "poolRecords",
}

/**
 * Tracks the oTokens created via the OtokenFactoryContract. This tracks all information
 * related to the oToken.
 *
 */
export type OToken = {
  __typename?: "OToken";
  id: Scalars["ID"];
  tokenAddress: Scalars["Bytes"];
  creator: Scalars["Bytes"];
  underlyingAsset: Token;
  strikeAsset: Token;
  collateralAsset: Token;
  strikePrice: Scalars["BigDecimal"];
  expiry: Scalars["BigInt"];
  isPut: Scalars["Boolean"];
  decimals: Scalars["BigInt"];
  settled: Scalars["Boolean"];
  premium: Scalars["BigDecimal"];
  collateralized: Scalars["BigDecimal"];
  liquiditySettled: Scalars["BigDecimal"];
  numberOfOTokens: Scalars["BigDecimal"];
  purchasesCount: Scalars["BigInt"];
  lpRecords: Array<Maybe<LpRecord>>;
  buyerRecords: Array<Maybe<BuyerRecord>>;
  orderBook: Array<Maybe<OrderBookEntry>>;
};

/**
 * Tracks the oTokens created via the OtokenFactoryContract. This tracks all information
 * related to the oToken.
 *
 */
export type OTokenLpRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<LpRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<LpRecord_Filter>;
};

/**
 * Tracks the oTokens created via the OtokenFactoryContract. This tracks all information
 * related to the oToken.
 *
 */
export type OTokenBuyerRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<BuyerRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<BuyerRecord_Filter>;
};

/**
 * Tracks the oTokens created via the OtokenFactoryContract. This tracks all information
 * related to the oToken.
 *
 */
export type OTokenOrderBookArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<OrderBookEntry_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<OrderBookEntry_Filter>;
};

export type OToken_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  tokenAddress?: Maybe<Scalars["Bytes"]>;
  tokenAddress_not?: Maybe<Scalars["Bytes"]>;
  tokenAddress_in?: Maybe<Array<Scalars["Bytes"]>>;
  tokenAddress_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  tokenAddress_contains?: Maybe<Scalars["Bytes"]>;
  tokenAddress_not_contains?: Maybe<Scalars["Bytes"]>;
  creator?: Maybe<Scalars["Bytes"]>;
  creator_not?: Maybe<Scalars["Bytes"]>;
  creator_in?: Maybe<Array<Scalars["Bytes"]>>;
  creator_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  creator_contains?: Maybe<Scalars["Bytes"]>;
  creator_not_contains?: Maybe<Scalars["Bytes"]>;
  underlyingAsset?: Maybe<Scalars["String"]>;
  underlyingAsset_not?: Maybe<Scalars["String"]>;
  underlyingAsset_gt?: Maybe<Scalars["String"]>;
  underlyingAsset_lt?: Maybe<Scalars["String"]>;
  underlyingAsset_gte?: Maybe<Scalars["String"]>;
  underlyingAsset_lte?: Maybe<Scalars["String"]>;
  underlyingAsset_in?: Maybe<Array<Scalars["String"]>>;
  underlyingAsset_not_in?: Maybe<Array<Scalars["String"]>>;
  underlyingAsset_contains?: Maybe<Scalars["String"]>;
  underlyingAsset_not_contains?: Maybe<Scalars["String"]>;
  underlyingAsset_starts_with?: Maybe<Scalars["String"]>;
  underlyingAsset_not_starts_with?: Maybe<Scalars["String"]>;
  underlyingAsset_ends_with?: Maybe<Scalars["String"]>;
  underlyingAsset_not_ends_with?: Maybe<Scalars["String"]>;
  strikeAsset?: Maybe<Scalars["String"]>;
  strikeAsset_not?: Maybe<Scalars["String"]>;
  strikeAsset_gt?: Maybe<Scalars["String"]>;
  strikeAsset_lt?: Maybe<Scalars["String"]>;
  strikeAsset_gte?: Maybe<Scalars["String"]>;
  strikeAsset_lte?: Maybe<Scalars["String"]>;
  strikeAsset_in?: Maybe<Array<Scalars["String"]>>;
  strikeAsset_not_in?: Maybe<Array<Scalars["String"]>>;
  strikeAsset_contains?: Maybe<Scalars["String"]>;
  strikeAsset_not_contains?: Maybe<Scalars["String"]>;
  strikeAsset_starts_with?: Maybe<Scalars["String"]>;
  strikeAsset_not_starts_with?: Maybe<Scalars["String"]>;
  strikeAsset_ends_with?: Maybe<Scalars["String"]>;
  strikeAsset_not_ends_with?: Maybe<Scalars["String"]>;
  collateralAsset?: Maybe<Scalars["String"]>;
  collateralAsset_not?: Maybe<Scalars["String"]>;
  collateralAsset_gt?: Maybe<Scalars["String"]>;
  collateralAsset_lt?: Maybe<Scalars["String"]>;
  collateralAsset_gte?: Maybe<Scalars["String"]>;
  collateralAsset_lte?: Maybe<Scalars["String"]>;
  collateralAsset_in?: Maybe<Array<Scalars["String"]>>;
  collateralAsset_not_in?: Maybe<Array<Scalars["String"]>>;
  collateralAsset_contains?: Maybe<Scalars["String"]>;
  collateralAsset_not_contains?: Maybe<Scalars["String"]>;
  collateralAsset_starts_with?: Maybe<Scalars["String"]>;
  collateralAsset_not_starts_with?: Maybe<Scalars["String"]>;
  collateralAsset_ends_with?: Maybe<Scalars["String"]>;
  collateralAsset_not_ends_with?: Maybe<Scalars["String"]>;
  strikePrice?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_not?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_gt?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_lt?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_gte?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_lte?: Maybe<Scalars["BigDecimal"]>;
  strikePrice_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  strikePrice_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  expiry?: Maybe<Scalars["BigInt"]>;
  expiry_not?: Maybe<Scalars["BigInt"]>;
  expiry_gt?: Maybe<Scalars["BigInt"]>;
  expiry_lt?: Maybe<Scalars["BigInt"]>;
  expiry_gte?: Maybe<Scalars["BigInt"]>;
  expiry_lte?: Maybe<Scalars["BigInt"]>;
  expiry_in?: Maybe<Array<Scalars["BigInt"]>>;
  expiry_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  isPut?: Maybe<Scalars["Boolean"]>;
  isPut_not?: Maybe<Scalars["Boolean"]>;
  isPut_in?: Maybe<Array<Scalars["Boolean"]>>;
  isPut_not_in?: Maybe<Array<Scalars["Boolean"]>>;
  decimals?: Maybe<Scalars["BigInt"]>;
  decimals_not?: Maybe<Scalars["BigInt"]>;
  decimals_gt?: Maybe<Scalars["BigInt"]>;
  decimals_lt?: Maybe<Scalars["BigInt"]>;
  decimals_gte?: Maybe<Scalars["BigInt"]>;
  decimals_lte?: Maybe<Scalars["BigInt"]>;
  decimals_in?: Maybe<Array<Scalars["BigInt"]>>;
  decimals_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  settled?: Maybe<Scalars["Boolean"]>;
  settled_not?: Maybe<Scalars["Boolean"]>;
  settled_in?: Maybe<Array<Scalars["Boolean"]>>;
  settled_not_in?: Maybe<Array<Scalars["Boolean"]>>;
  premium?: Maybe<Scalars["BigDecimal"]>;
  premium_not?: Maybe<Scalars["BigDecimal"]>;
  premium_gt?: Maybe<Scalars["BigDecimal"]>;
  premium_lt?: Maybe<Scalars["BigDecimal"]>;
  premium_gte?: Maybe<Scalars["BigDecimal"]>;
  premium_lte?: Maybe<Scalars["BigDecimal"]>;
  premium_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premium_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  collateralized?: Maybe<Scalars["BigDecimal"]>;
  collateralized_not?: Maybe<Scalars["BigDecimal"]>;
  collateralized_gt?: Maybe<Scalars["BigDecimal"]>;
  collateralized_lt?: Maybe<Scalars["BigDecimal"]>;
  collateralized_gte?: Maybe<Scalars["BigDecimal"]>;
  collateralized_lte?: Maybe<Scalars["BigDecimal"]>;
  collateralized_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  collateralized_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquiditySettled?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_not?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_gt?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_lt?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_gte?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_lte?: Maybe<Scalars["BigDecimal"]>;
  liquiditySettled_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquiditySettled_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_not?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  purchasesCount?: Maybe<Scalars["BigInt"]>;
  purchasesCount_not?: Maybe<Scalars["BigInt"]>;
  purchasesCount_gt?: Maybe<Scalars["BigInt"]>;
  purchasesCount_lt?: Maybe<Scalars["BigInt"]>;
  purchasesCount_gte?: Maybe<Scalars["BigInt"]>;
  purchasesCount_lte?: Maybe<Scalars["BigInt"]>;
  purchasesCount_in?: Maybe<Array<Scalars["BigInt"]>>;
  purchasesCount_not_in?: Maybe<Array<Scalars["BigInt"]>>;
};

export enum OToken_OrderBy {
  Id = "id",
  TokenAddress = "tokenAddress",
  Creator = "creator",
  UnderlyingAsset = "underlyingAsset",
  StrikeAsset = "strikeAsset",
  CollateralAsset = "collateralAsset",
  StrikePrice = "strikePrice",
  Expiry = "expiry",
  IsPut = "isPut",
  Decimals = "decimals",
  Settled = "settled",
  Premium = "premium",
  Collateralized = "collateralized",
  LiquiditySettled = "liquiditySettled",
  NumberOfOTokens = "numberOfOTokens",
  PurchasesCount = "purchasesCount",
  LpRecords = "lpRecords",
  BuyerRecords = "buyerRecords",
  OrderBook = "orderBook",
}

export type OrderBookEntry = {
  __typename?: "OrderBookEntry";
  id: Scalars["ID"];
  otoken: OToken;
  timestamp: Scalars["BigInt"];
  buyer: Scalars["Bytes"];
  numberOfOTokens: Scalars["BigDecimal"];
  premium: Scalars["BigDecimal"];
};

export type OrderBookEntry_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  otoken?: Maybe<Scalars["String"]>;
  otoken_not?: Maybe<Scalars["String"]>;
  otoken_gt?: Maybe<Scalars["String"]>;
  otoken_lt?: Maybe<Scalars["String"]>;
  otoken_gte?: Maybe<Scalars["String"]>;
  otoken_lte?: Maybe<Scalars["String"]>;
  otoken_in?: Maybe<Array<Scalars["String"]>>;
  otoken_not_in?: Maybe<Array<Scalars["String"]>>;
  otoken_contains?: Maybe<Scalars["String"]>;
  otoken_not_contains?: Maybe<Scalars["String"]>;
  otoken_starts_with?: Maybe<Scalars["String"]>;
  otoken_not_starts_with?: Maybe<Scalars["String"]>;
  otoken_ends_with?: Maybe<Scalars["String"]>;
  otoken_not_ends_with?: Maybe<Scalars["String"]>;
  timestamp?: Maybe<Scalars["BigInt"]>;
  timestamp_not?: Maybe<Scalars["BigInt"]>;
  timestamp_gt?: Maybe<Scalars["BigInt"]>;
  timestamp_lt?: Maybe<Scalars["BigInt"]>;
  timestamp_gte?: Maybe<Scalars["BigInt"]>;
  timestamp_lte?: Maybe<Scalars["BigInt"]>;
  timestamp_in?: Maybe<Array<Scalars["BigInt"]>>;
  timestamp_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  buyer?: Maybe<Scalars["Bytes"]>;
  buyer_not?: Maybe<Scalars["Bytes"]>;
  buyer_in?: Maybe<Array<Scalars["Bytes"]>>;
  buyer_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  buyer_contains?: Maybe<Scalars["Bytes"]>;
  buyer_not_contains?: Maybe<Scalars["Bytes"]>;
  numberOfOTokens?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_not?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premium?: Maybe<Scalars["BigDecimal"]>;
  premium_not?: Maybe<Scalars["BigDecimal"]>;
  premium_gt?: Maybe<Scalars["BigDecimal"]>;
  premium_lt?: Maybe<Scalars["BigDecimal"]>;
  premium_gte?: Maybe<Scalars["BigDecimal"]>;
  premium_lte?: Maybe<Scalars["BigDecimal"]>;
  premium_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premium_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum OrderBookEntry_OrderBy {
  Id = "id",
  Otoken = "otoken",
  Timestamp = "timestamp",
  Buyer = "buyer",
  NumberOfOTokens = "numberOfOTokens",
  Premium = "premium",
}

export enum OrderDirection {
  Asc = "asc",
  Desc = "desc",
}

/**
 * Describes a LP's pool.
 *
 */
export type Pool = {
  __typename?: "Pool";
  id: Scalars["ID"];
  poolId: Scalars["BigInt"];
  lp: Scalars["Bytes"];
  size: Scalars["BigDecimal"];
  locked: Scalars["BigDecimal"];
  unlocked: Scalars["BigDecimal"];
  utilization: Scalars["BigDecimal"];
  averageCost?: Maybe<Scalars["BigDecimal"]>;
  template?: Maybe<Template>;
  pnlTotal: Scalars["BigDecimal"];
  pnlPercentage: Scalars["BigDecimal"];
  liquidityAtTrades: Scalars["BigDecimal"];
  initialBalance?: Maybe<Scalars["BigDecimal"]>;
  snapshots: Array<Maybe<PoolSnapshot>>;
  poolRecords: Array<Maybe<PoolRecord>>;
};

/**
 * Describes a LP's pool.
 *
 */
export type PoolSnapshotsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolSnapshot_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolSnapshot_Filter>;
};

/**
 * Describes a LP's pool.
 *
 */
export type PoolPoolRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolRecord_Filter>;
};

/**
 * For every pool that has contributed to a oToken, there exists a PoolRecord
 * entity. It tracks the lp it belongs to, the oToken, the amount of money collateralized,
 * and the amount returned to the pool after settlement.
 *
 * The lpRecord field is used to join with LPRecord.
 *
 */
export type PoolRecord = {
  __typename?: "PoolRecord";
  id: Scalars["ID"];
  pool: Pool;
  lpRecord: LpRecord;
  otoken: OToken;
  collateral: Scalars["BigDecimal"];
  premiumReceived: Scalars["BigDecimal"];
  numberOfOTokens: Scalars["BigDecimal"];
  returned?: Maybe<Scalars["BigDecimal"]>;
};

export type PoolRecord_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  pool?: Maybe<Scalars["String"]>;
  pool_not?: Maybe<Scalars["String"]>;
  pool_gt?: Maybe<Scalars["String"]>;
  pool_lt?: Maybe<Scalars["String"]>;
  pool_gte?: Maybe<Scalars["String"]>;
  pool_lte?: Maybe<Scalars["String"]>;
  pool_in?: Maybe<Array<Scalars["String"]>>;
  pool_not_in?: Maybe<Array<Scalars["String"]>>;
  pool_contains?: Maybe<Scalars["String"]>;
  pool_not_contains?: Maybe<Scalars["String"]>;
  pool_starts_with?: Maybe<Scalars["String"]>;
  pool_not_starts_with?: Maybe<Scalars["String"]>;
  pool_ends_with?: Maybe<Scalars["String"]>;
  pool_not_ends_with?: Maybe<Scalars["String"]>;
  lpRecord?: Maybe<Scalars["String"]>;
  lpRecord_not?: Maybe<Scalars["String"]>;
  lpRecord_gt?: Maybe<Scalars["String"]>;
  lpRecord_lt?: Maybe<Scalars["String"]>;
  lpRecord_gte?: Maybe<Scalars["String"]>;
  lpRecord_lte?: Maybe<Scalars["String"]>;
  lpRecord_in?: Maybe<Array<Scalars["String"]>>;
  lpRecord_not_in?: Maybe<Array<Scalars["String"]>>;
  lpRecord_contains?: Maybe<Scalars["String"]>;
  lpRecord_not_contains?: Maybe<Scalars["String"]>;
  lpRecord_starts_with?: Maybe<Scalars["String"]>;
  lpRecord_not_starts_with?: Maybe<Scalars["String"]>;
  lpRecord_ends_with?: Maybe<Scalars["String"]>;
  lpRecord_not_ends_with?: Maybe<Scalars["String"]>;
  otoken?: Maybe<Scalars["String"]>;
  otoken_not?: Maybe<Scalars["String"]>;
  otoken_gt?: Maybe<Scalars["String"]>;
  otoken_lt?: Maybe<Scalars["String"]>;
  otoken_gte?: Maybe<Scalars["String"]>;
  otoken_lte?: Maybe<Scalars["String"]>;
  otoken_in?: Maybe<Array<Scalars["String"]>>;
  otoken_not_in?: Maybe<Array<Scalars["String"]>>;
  otoken_contains?: Maybe<Scalars["String"]>;
  otoken_not_contains?: Maybe<Scalars["String"]>;
  otoken_starts_with?: Maybe<Scalars["String"]>;
  otoken_not_starts_with?: Maybe<Scalars["String"]>;
  otoken_ends_with?: Maybe<Scalars["String"]>;
  otoken_not_ends_with?: Maybe<Scalars["String"]>;
  collateral?: Maybe<Scalars["BigDecimal"]>;
  collateral_not?: Maybe<Scalars["BigDecimal"]>;
  collateral_gt?: Maybe<Scalars["BigDecimal"]>;
  collateral_lt?: Maybe<Scalars["BigDecimal"]>;
  collateral_gte?: Maybe<Scalars["BigDecimal"]>;
  collateral_lte?: Maybe<Scalars["BigDecimal"]>;
  collateral_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  collateral_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premiumReceived?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_not?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_gt?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_lt?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_gte?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_lte?: Maybe<Scalars["BigDecimal"]>;
  premiumReceived_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  premiumReceived_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_not?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lt?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_gte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_lte?: Maybe<Scalars["BigDecimal"]>;
  numberOfOTokens_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numberOfOTokens_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  returned?: Maybe<Scalars["BigDecimal"]>;
  returned_not?: Maybe<Scalars["BigDecimal"]>;
  returned_gt?: Maybe<Scalars["BigDecimal"]>;
  returned_lt?: Maybe<Scalars["BigDecimal"]>;
  returned_gte?: Maybe<Scalars["BigDecimal"]>;
  returned_lte?: Maybe<Scalars["BigDecimal"]>;
  returned_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  returned_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum PoolRecord_OrderBy {
  Id = "id",
  Pool = "pool",
  LpRecord = "lpRecord",
  Otoken = "otoken",
  Collateral = "collateral",
  PremiumReceived = "premiumReceived",
  NumberOfOTokens = "numberOfOTokens",
  Returned = "returned",
}

/**
 * This entity is produced anytime a field in a pool is updated.
 * The type of change is denoted by actionType, which comes from the
 * ActionType enum.
 *
 */
export type PoolSnapshot = {
  __typename?: "PoolSnapshot";
  id: Scalars["ID"];
  poolId: Scalars["BigInt"];
  lp?: Maybe<Scalars["Bytes"]>;
  size: Scalars["BigDecimal"];
  locked: Scalars["BigDecimal"];
  unlocked: Scalars["BigDecimal"];
  utilization: Scalars["BigDecimal"];
  template: Template;
  templatePnlPercentage?: Maybe<Scalars["BigDecimal"]>;
  templateSize?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades?: Maybe<Scalars["BigDecimal"]>;
  actionAmount: Scalars["BigDecimal"];
  actionType: Scalars["BigInt"];
  timestamp: Scalars["BigInt"];
  currentPool: Pool;
  pnlTotal: Scalars["BigDecimal"];
  pnlPercentage: Scalars["BigDecimal"];
  liquidityAtTrades: Scalars["BigDecimal"];
  initialBalance?: Maybe<Scalars["BigDecimal"]>;
};

export type PoolSnapshot_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  poolId?: Maybe<Scalars["BigInt"]>;
  poolId_not?: Maybe<Scalars["BigInt"]>;
  poolId_gt?: Maybe<Scalars["BigInt"]>;
  poolId_lt?: Maybe<Scalars["BigInt"]>;
  poolId_gte?: Maybe<Scalars["BigInt"]>;
  poolId_lte?: Maybe<Scalars["BigInt"]>;
  poolId_in?: Maybe<Array<Scalars["BigInt"]>>;
  poolId_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  lp?: Maybe<Scalars["Bytes"]>;
  lp_not?: Maybe<Scalars["Bytes"]>;
  lp_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_contains?: Maybe<Scalars["Bytes"]>;
  lp_not_contains?: Maybe<Scalars["Bytes"]>;
  size?: Maybe<Scalars["BigDecimal"]>;
  size_not?: Maybe<Scalars["BigDecimal"]>;
  size_gt?: Maybe<Scalars["BigDecimal"]>;
  size_lt?: Maybe<Scalars["BigDecimal"]>;
  size_gte?: Maybe<Scalars["BigDecimal"]>;
  size_lte?: Maybe<Scalars["BigDecimal"]>;
  size_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  size_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked?: Maybe<Scalars["BigDecimal"]>;
  locked_not?: Maybe<Scalars["BigDecimal"]>;
  locked_gt?: Maybe<Scalars["BigDecimal"]>;
  locked_lt?: Maybe<Scalars["BigDecimal"]>;
  locked_gte?: Maybe<Scalars["BigDecimal"]>;
  locked_lte?: Maybe<Scalars["BigDecimal"]>;
  locked_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  unlocked?: Maybe<Scalars["BigDecimal"]>;
  unlocked_not?: Maybe<Scalars["BigDecimal"]>;
  unlocked_gt?: Maybe<Scalars["BigDecimal"]>;
  unlocked_lt?: Maybe<Scalars["BigDecimal"]>;
  unlocked_gte?: Maybe<Scalars["BigDecimal"]>;
  unlocked_lte?: Maybe<Scalars["BigDecimal"]>;
  unlocked_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  unlocked_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization?: Maybe<Scalars["BigDecimal"]>;
  utilization_not?: Maybe<Scalars["BigDecimal"]>;
  utilization_gt?: Maybe<Scalars["BigDecimal"]>;
  utilization_lt?: Maybe<Scalars["BigDecimal"]>;
  utilization_gte?: Maybe<Scalars["BigDecimal"]>;
  utilization_lte?: Maybe<Scalars["BigDecimal"]>;
  utilization_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  template?: Maybe<Scalars["String"]>;
  template_not?: Maybe<Scalars["String"]>;
  template_gt?: Maybe<Scalars["String"]>;
  template_lt?: Maybe<Scalars["String"]>;
  template_gte?: Maybe<Scalars["String"]>;
  template_lte?: Maybe<Scalars["String"]>;
  template_in?: Maybe<Array<Scalars["String"]>>;
  template_not_in?: Maybe<Array<Scalars["String"]>>;
  template_contains?: Maybe<Scalars["String"]>;
  template_not_contains?: Maybe<Scalars["String"]>;
  template_starts_with?: Maybe<Scalars["String"]>;
  template_not_starts_with?: Maybe<Scalars["String"]>;
  template_ends_with?: Maybe<Scalars["String"]>;
  template_not_ends_with?: Maybe<Scalars["String"]>;
  templatePnlPercentage?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_not?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_gt?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_lt?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_gte?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_lte?: Maybe<Scalars["BigDecimal"]>;
  templatePnlPercentage_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templatePnlPercentage_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateSize?: Maybe<Scalars["BigDecimal"]>;
  templateSize_not?: Maybe<Scalars["BigDecimal"]>;
  templateSize_gt?: Maybe<Scalars["BigDecimal"]>;
  templateSize_lt?: Maybe<Scalars["BigDecimal"]>;
  templateSize_gte?: Maybe<Scalars["BigDecimal"]>;
  templateSize_lte?: Maybe<Scalars["BigDecimal"]>;
  templateSize_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateSize_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateUtilization?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_not?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_gt?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_lt?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_gte?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_lte?: Maybe<Scalars["BigDecimal"]>;
  templateUtilization_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateUtilization_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templatePnlTotal?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_not?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_gt?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_lt?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_gte?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_lte?: Maybe<Scalars["BigDecimal"]>;
  templatePnlTotal_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templatePnlTotal_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateLiquidityAtTrades?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_not?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_gt?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_lt?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_gte?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_lte?: Maybe<Scalars["BigDecimal"]>;
  templateLiquidityAtTrades_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  templateLiquidityAtTrades_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  actionAmount?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_not?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_gt?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_lt?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_gte?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_lte?: Maybe<Scalars["BigDecimal"]>;
  actionAmount_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  actionAmount_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  actionType?: Maybe<Scalars["BigInt"]>;
  actionType_not?: Maybe<Scalars["BigInt"]>;
  actionType_gt?: Maybe<Scalars["BigInt"]>;
  actionType_lt?: Maybe<Scalars["BigInt"]>;
  actionType_gte?: Maybe<Scalars["BigInt"]>;
  actionType_lte?: Maybe<Scalars["BigInt"]>;
  actionType_in?: Maybe<Array<Scalars["BigInt"]>>;
  actionType_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  timestamp?: Maybe<Scalars["BigInt"]>;
  timestamp_not?: Maybe<Scalars["BigInt"]>;
  timestamp_gt?: Maybe<Scalars["BigInt"]>;
  timestamp_lt?: Maybe<Scalars["BigInt"]>;
  timestamp_gte?: Maybe<Scalars["BigInt"]>;
  timestamp_lte?: Maybe<Scalars["BigInt"]>;
  timestamp_in?: Maybe<Array<Scalars["BigInt"]>>;
  timestamp_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  currentPool?: Maybe<Scalars["String"]>;
  currentPool_not?: Maybe<Scalars["String"]>;
  currentPool_gt?: Maybe<Scalars["String"]>;
  currentPool_lt?: Maybe<Scalars["String"]>;
  currentPool_gte?: Maybe<Scalars["String"]>;
  currentPool_lte?: Maybe<Scalars["String"]>;
  currentPool_in?: Maybe<Array<Scalars["String"]>>;
  currentPool_not_in?: Maybe<Array<Scalars["String"]>>;
  currentPool_contains?: Maybe<Scalars["String"]>;
  currentPool_not_contains?: Maybe<Scalars["String"]>;
  currentPool_starts_with?: Maybe<Scalars["String"]>;
  currentPool_not_starts_with?: Maybe<Scalars["String"]>;
  currentPool_ends_with?: Maybe<Scalars["String"]>;
  currentPool_not_ends_with?: Maybe<Scalars["String"]>;
  pnlTotal?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_not?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlTotal_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_not?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_not?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  initialBalance?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_not?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_gt?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_lt?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_gte?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_lte?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  initialBalance_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum PoolSnapshot_OrderBy {
  Id = "id",
  PoolId = "poolId",
  Lp = "lp",
  Size = "size",
  Locked = "locked",
  Unlocked = "unlocked",
  Utilization = "utilization",
  Template = "template",
  TemplatePnlPercentage = "templatePnlPercentage",
  TemplateSize = "templateSize",
  TemplateUtilization = "templateUtilization",
  TemplatePnlTotal = "templatePnlTotal",
  TemplateLiquidityAtTrades = "templateLiquidityAtTrades",
  ActionAmount = "actionAmount",
  ActionType = "actionType",
  Timestamp = "timestamp",
  CurrentPool = "currentPool",
  PnlTotal = "pnlTotal",
  PnlPercentage = "pnlPercentage",
  LiquidityAtTrades = "liquidityAtTrades",
  InitialBalance = "initialBalance",
}

export type Pool_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  poolId?: Maybe<Scalars["BigInt"]>;
  poolId_not?: Maybe<Scalars["BigInt"]>;
  poolId_gt?: Maybe<Scalars["BigInt"]>;
  poolId_lt?: Maybe<Scalars["BigInt"]>;
  poolId_gte?: Maybe<Scalars["BigInt"]>;
  poolId_lte?: Maybe<Scalars["BigInt"]>;
  poolId_in?: Maybe<Array<Scalars["BigInt"]>>;
  poolId_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  lp?: Maybe<Scalars["Bytes"]>;
  lp_not?: Maybe<Scalars["Bytes"]>;
  lp_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  lp_contains?: Maybe<Scalars["Bytes"]>;
  lp_not_contains?: Maybe<Scalars["Bytes"]>;
  size?: Maybe<Scalars["BigDecimal"]>;
  size_not?: Maybe<Scalars["BigDecimal"]>;
  size_gt?: Maybe<Scalars["BigDecimal"]>;
  size_lt?: Maybe<Scalars["BigDecimal"]>;
  size_gte?: Maybe<Scalars["BigDecimal"]>;
  size_lte?: Maybe<Scalars["BigDecimal"]>;
  size_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  size_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked?: Maybe<Scalars["BigDecimal"]>;
  locked_not?: Maybe<Scalars["BigDecimal"]>;
  locked_gt?: Maybe<Scalars["BigDecimal"]>;
  locked_lt?: Maybe<Scalars["BigDecimal"]>;
  locked_gte?: Maybe<Scalars["BigDecimal"]>;
  locked_lte?: Maybe<Scalars["BigDecimal"]>;
  locked_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  unlocked?: Maybe<Scalars["BigDecimal"]>;
  unlocked_not?: Maybe<Scalars["BigDecimal"]>;
  unlocked_gt?: Maybe<Scalars["BigDecimal"]>;
  unlocked_lt?: Maybe<Scalars["BigDecimal"]>;
  unlocked_gte?: Maybe<Scalars["BigDecimal"]>;
  unlocked_lte?: Maybe<Scalars["BigDecimal"]>;
  unlocked_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  unlocked_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization?: Maybe<Scalars["BigDecimal"]>;
  utilization_not?: Maybe<Scalars["BigDecimal"]>;
  utilization_gt?: Maybe<Scalars["BigDecimal"]>;
  utilization_lt?: Maybe<Scalars["BigDecimal"]>;
  utilization_gte?: Maybe<Scalars["BigDecimal"]>;
  utilization_lte?: Maybe<Scalars["BigDecimal"]>;
  utilization_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  averageCost?: Maybe<Scalars["BigDecimal"]>;
  averageCost_not?: Maybe<Scalars["BigDecimal"]>;
  averageCost_gt?: Maybe<Scalars["BigDecimal"]>;
  averageCost_lt?: Maybe<Scalars["BigDecimal"]>;
  averageCost_gte?: Maybe<Scalars["BigDecimal"]>;
  averageCost_lte?: Maybe<Scalars["BigDecimal"]>;
  averageCost_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  averageCost_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  template?: Maybe<Scalars["String"]>;
  template_not?: Maybe<Scalars["String"]>;
  template_gt?: Maybe<Scalars["String"]>;
  template_lt?: Maybe<Scalars["String"]>;
  template_gte?: Maybe<Scalars["String"]>;
  template_lte?: Maybe<Scalars["String"]>;
  template_in?: Maybe<Array<Scalars["String"]>>;
  template_not_in?: Maybe<Array<Scalars["String"]>>;
  template_contains?: Maybe<Scalars["String"]>;
  template_not_contains?: Maybe<Scalars["String"]>;
  template_starts_with?: Maybe<Scalars["String"]>;
  template_not_starts_with?: Maybe<Scalars["String"]>;
  template_ends_with?: Maybe<Scalars["String"]>;
  template_not_ends_with?: Maybe<Scalars["String"]>;
  pnlTotal?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_not?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlTotal_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_not?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_not?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  initialBalance?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_not?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_gt?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_lt?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_gte?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_lte?: Maybe<Scalars["BigDecimal"]>;
  initialBalance_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  initialBalance_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum Pool_OrderBy {
  Id = "id",
  PoolId = "poolId",
  Lp = "lp",
  Size = "size",
  Locked = "locked",
  Unlocked = "unlocked",
  Utilization = "utilization",
  AverageCost = "averageCost",
  Template = "template",
  PnlTotal = "pnlTotal",
  PnlPercentage = "pnlPercentage",
  LiquidityAtTrades = "liquidityAtTrades",
  InitialBalance = "initialBalance",
  Snapshots = "snapshots",
  PoolRecords = "poolRecords",
}

export type Product = {
  __typename?: "Product";
  id: Scalars["ID"];
  underlying: Token;
  strike: Token;
  collateral: Token;
  isPut: Scalars["Boolean"];
  isWhitelisted: Scalars["Boolean"];
};

export type Product_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  underlying?: Maybe<Scalars["String"]>;
  underlying_not?: Maybe<Scalars["String"]>;
  underlying_gt?: Maybe<Scalars["String"]>;
  underlying_lt?: Maybe<Scalars["String"]>;
  underlying_gte?: Maybe<Scalars["String"]>;
  underlying_lte?: Maybe<Scalars["String"]>;
  underlying_in?: Maybe<Array<Scalars["String"]>>;
  underlying_not_in?: Maybe<Array<Scalars["String"]>>;
  underlying_contains?: Maybe<Scalars["String"]>;
  underlying_not_contains?: Maybe<Scalars["String"]>;
  underlying_starts_with?: Maybe<Scalars["String"]>;
  underlying_not_starts_with?: Maybe<Scalars["String"]>;
  underlying_ends_with?: Maybe<Scalars["String"]>;
  underlying_not_ends_with?: Maybe<Scalars["String"]>;
  strike?: Maybe<Scalars["String"]>;
  strike_not?: Maybe<Scalars["String"]>;
  strike_gt?: Maybe<Scalars["String"]>;
  strike_lt?: Maybe<Scalars["String"]>;
  strike_gte?: Maybe<Scalars["String"]>;
  strike_lte?: Maybe<Scalars["String"]>;
  strike_in?: Maybe<Array<Scalars["String"]>>;
  strike_not_in?: Maybe<Array<Scalars["String"]>>;
  strike_contains?: Maybe<Scalars["String"]>;
  strike_not_contains?: Maybe<Scalars["String"]>;
  strike_starts_with?: Maybe<Scalars["String"]>;
  strike_not_starts_with?: Maybe<Scalars["String"]>;
  strike_ends_with?: Maybe<Scalars["String"]>;
  strike_not_ends_with?: Maybe<Scalars["String"]>;
  collateral?: Maybe<Scalars["String"]>;
  collateral_not?: Maybe<Scalars["String"]>;
  collateral_gt?: Maybe<Scalars["String"]>;
  collateral_lt?: Maybe<Scalars["String"]>;
  collateral_gte?: Maybe<Scalars["String"]>;
  collateral_lte?: Maybe<Scalars["String"]>;
  collateral_in?: Maybe<Array<Scalars["String"]>>;
  collateral_not_in?: Maybe<Array<Scalars["String"]>>;
  collateral_contains?: Maybe<Scalars["String"]>;
  collateral_not_contains?: Maybe<Scalars["String"]>;
  collateral_starts_with?: Maybe<Scalars["String"]>;
  collateral_not_starts_with?: Maybe<Scalars["String"]>;
  collateral_ends_with?: Maybe<Scalars["String"]>;
  collateral_not_ends_with?: Maybe<Scalars["String"]>;
  isPut?: Maybe<Scalars["Boolean"]>;
  isPut_not?: Maybe<Scalars["Boolean"]>;
  isPut_in?: Maybe<Array<Scalars["Boolean"]>>;
  isPut_not_in?: Maybe<Array<Scalars["Boolean"]>>;
  isWhitelisted?: Maybe<Scalars["Boolean"]>;
  isWhitelisted_not?: Maybe<Scalars["Boolean"]>;
  isWhitelisted_in?: Maybe<Array<Scalars["Boolean"]>>;
  isWhitelisted_not_in?: Maybe<Array<Scalars["Boolean"]>>;
};

export enum Product_OrderBy {
  Id = "id",
  Underlying = "underlying",
  Strike = "strike",
  Collateral = "collateral",
  IsPut = "isPut",
  IsWhitelisted = "isWhitelisted",
}

export type Query = {
  __typename?: "Query";
  curve?: Maybe<Curve>;
  curves: Array<Curve>;
  criteria?: Maybe<Criteria>;
  criterias: Array<Criteria>;
  template?: Maybe<Template>;
  templates: Array<Template>;
  criteriaSet?: Maybe<CriteriaSet>;
  criteriaSets: Array<CriteriaSet>;
  criteriaJoinedCriteriaSet?: Maybe<CriteriaJoinedCriteriaSet>;
  criteriaJoinedCriteriaSets: Array<CriteriaJoinedCriteriaSet>;
  pool?: Maybe<Pool>;
  pools: Array<Pool>;
  poolSnapshot?: Maybe<PoolSnapshot>;
  poolSnapshots: Array<PoolSnapshot>;
  buyerRecord?: Maybe<BuyerRecord>;
  buyerRecords: Array<BuyerRecord>;
  lprecord?: Maybe<LpRecord>;
  lprecords: Array<LpRecord>;
  poolRecord?: Maybe<PoolRecord>;
  poolRecords: Array<PoolRecord>;
  otoken?: Maybe<OToken>;
  otokens: Array<OToken>;
  orderBookEntry?: Maybe<OrderBookEntry>;
  orderBookEntries: Array<OrderBookEntry>;
  token?: Maybe<Token>;
  tokens: Array<Token>;
  underlying?: Maybe<Underlying>;
  underlyings: Array<Underlying>;
  collateral?: Maybe<Collateral>;
  collaterals: Array<Collateral>;
  product?: Maybe<Product>;
  products: Array<Product>;
  /** Access to subgraph metadata */
  _meta?: Maybe<_Meta_>;
};

export type QueryCurveArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryCurvesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Curve_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Curve_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryCriteriaArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryCriteriasArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Criteria_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Criteria_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryTemplateArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryTemplatesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Template_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Template_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryCriteriaSetArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryCriteriaSetsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaSet_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryCriteriaJoinedCriteriaSetArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryCriteriaJoinedCriteriaSetsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaJoinedCriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaJoinedCriteriaSet_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryPoolArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryPoolsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Pool_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Pool_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryPoolSnapshotArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryPoolSnapshotsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolSnapshot_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolSnapshot_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryBuyerRecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryBuyerRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<BuyerRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<BuyerRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryLprecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryLprecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<LpRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<LpRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryPoolRecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryPoolRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryOtokenArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryOtokensArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<OToken_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<OToken_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryOrderBookEntryArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryOrderBookEntriesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<OrderBookEntry_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<OrderBookEntry_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryTokenArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryTokensArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Token_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Token_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryUnderlyingArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryUnderlyingsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Underlying_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Underlying_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryCollateralArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryCollateralsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Collateral_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Collateral_Filter>;
  block?: Maybe<Block_Height>;
};

export type QueryProductArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type QueryProductsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Product_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Product_Filter>;
  block?: Maybe<Block_Height>;
};

export type Query_MetaArgs = {
  block?: Maybe<Block_Height>;
};

export type Subscription = {
  __typename?: "Subscription";
  curve?: Maybe<Curve>;
  curves: Array<Curve>;
  criteria?: Maybe<Criteria>;
  criterias: Array<Criteria>;
  template?: Maybe<Template>;
  templates: Array<Template>;
  criteriaSet?: Maybe<CriteriaSet>;
  criteriaSets: Array<CriteriaSet>;
  criteriaJoinedCriteriaSet?: Maybe<CriteriaJoinedCriteriaSet>;
  criteriaJoinedCriteriaSets: Array<CriteriaJoinedCriteriaSet>;
  pool?: Maybe<Pool>;
  pools: Array<Pool>;
  poolSnapshot?: Maybe<PoolSnapshot>;
  poolSnapshots: Array<PoolSnapshot>;
  buyerRecord?: Maybe<BuyerRecord>;
  buyerRecords: Array<BuyerRecord>;
  lprecord?: Maybe<LpRecord>;
  lprecords: Array<LpRecord>;
  poolRecord?: Maybe<PoolRecord>;
  poolRecords: Array<PoolRecord>;
  otoken?: Maybe<OToken>;
  otokens: Array<OToken>;
  orderBookEntry?: Maybe<OrderBookEntry>;
  orderBookEntries: Array<OrderBookEntry>;
  token?: Maybe<Token>;
  tokens: Array<Token>;
  underlying?: Maybe<Underlying>;
  underlyings: Array<Underlying>;
  collateral?: Maybe<Collateral>;
  collaterals: Array<Collateral>;
  product?: Maybe<Product>;
  products: Array<Product>;
  /** Access to subgraph metadata */
  _meta?: Maybe<_Meta_>;
};

export type SubscriptionCurveArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionCurvesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Curve_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Curve_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriaArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriasArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Criteria_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Criteria_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionTemplateArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionTemplatesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Template_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Template_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriaSetArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriaSetsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaSet_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriaJoinedCriteriaSetArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionCriteriaJoinedCriteriaSetsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<CriteriaJoinedCriteriaSet_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<CriteriaJoinedCriteriaSet_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Pool_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Pool_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolSnapshotArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolSnapshotsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolSnapshot_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolSnapshot_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionBuyerRecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionBuyerRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<BuyerRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<BuyerRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionLprecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionLprecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<LpRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<LpRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolRecordArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionPoolRecordsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<PoolRecord_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<PoolRecord_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionOtokenArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionOtokensArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<OToken_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<OToken_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionOrderBookEntryArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionOrderBookEntriesArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<OrderBookEntry_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<OrderBookEntry_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionTokenArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionTokensArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Token_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Token_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionUnderlyingArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionUnderlyingsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Underlying_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Underlying_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionCollateralArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionCollateralsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Collateral_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Collateral_Filter>;
  block?: Maybe<Block_Height>;
};

export type SubscriptionProductArgs = {
  id: Scalars["ID"];
  block?: Maybe<Block_Height>;
};

export type SubscriptionProductsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Product_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Product_Filter>;
  block?: Maybe<Block_Height>;
};

export type Subscription_MetaArgs = {
  block?: Maybe<Block_Height>;
};

/**
 * Describes a unique combination of a Curve and CriteriaSet. For every unique combination
 * of curveHash and criteriaSetHash, there is a Template that describbes the number of pools
 * that have these settings, the aggregated size of all pools, and absolute Profit and Loss.
 *
 */
export type Template = {
  __typename?: "Template";
  id: Scalars["ID"];
  size: Scalars["BigDecimal"];
  locked: Scalars["BigDecimal"];
  utilization: Scalars["BigDecimal"];
  numPools: Scalars["BigInt"];
  curve?: Maybe<Curve>;
  criteriaSet?: Maybe<CriteriaSet>;
  pnl: Scalars["BigDecimal"];
  pnlTotal: Scalars["BigDecimal"];
  pnlPercentage: Scalars["BigDecimal"];
  liquidityAtTrades: Scalars["BigDecimal"];
  pools: Array<Pool>;
};

/**
 * Describes a unique combination of a Curve and CriteriaSet. For every unique combination
 * of curveHash and criteriaSetHash, there is a Template that describbes the number of pools
 * that have these settings, the aggregated size of all pools, and absolute Profit and Loss.
 *
 */
export type TemplatePoolsArgs = {
  skip?: Maybe<Scalars["Int"]>;
  first?: Maybe<Scalars["Int"]>;
  orderBy?: Maybe<Pool_OrderBy>;
  orderDirection?: Maybe<OrderDirection>;
  where?: Maybe<Pool_Filter>;
};

export type Template_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  size?: Maybe<Scalars["BigDecimal"]>;
  size_not?: Maybe<Scalars["BigDecimal"]>;
  size_gt?: Maybe<Scalars["BigDecimal"]>;
  size_lt?: Maybe<Scalars["BigDecimal"]>;
  size_gte?: Maybe<Scalars["BigDecimal"]>;
  size_lte?: Maybe<Scalars["BigDecimal"]>;
  size_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  size_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked?: Maybe<Scalars["BigDecimal"]>;
  locked_not?: Maybe<Scalars["BigDecimal"]>;
  locked_gt?: Maybe<Scalars["BigDecimal"]>;
  locked_lt?: Maybe<Scalars["BigDecimal"]>;
  locked_gte?: Maybe<Scalars["BigDecimal"]>;
  locked_lte?: Maybe<Scalars["BigDecimal"]>;
  locked_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  locked_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization?: Maybe<Scalars["BigDecimal"]>;
  utilization_not?: Maybe<Scalars["BigDecimal"]>;
  utilization_gt?: Maybe<Scalars["BigDecimal"]>;
  utilization_lt?: Maybe<Scalars["BigDecimal"]>;
  utilization_gte?: Maybe<Scalars["BigDecimal"]>;
  utilization_lte?: Maybe<Scalars["BigDecimal"]>;
  utilization_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  utilization_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  numPools?: Maybe<Scalars["BigInt"]>;
  numPools_not?: Maybe<Scalars["BigInt"]>;
  numPools_gt?: Maybe<Scalars["BigInt"]>;
  numPools_lt?: Maybe<Scalars["BigInt"]>;
  numPools_gte?: Maybe<Scalars["BigInt"]>;
  numPools_lte?: Maybe<Scalars["BigInt"]>;
  numPools_in?: Maybe<Array<Scalars["BigInt"]>>;
  numPools_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  curve?: Maybe<Scalars["String"]>;
  curve_not?: Maybe<Scalars["String"]>;
  curve_gt?: Maybe<Scalars["String"]>;
  curve_lt?: Maybe<Scalars["String"]>;
  curve_gte?: Maybe<Scalars["String"]>;
  curve_lte?: Maybe<Scalars["String"]>;
  curve_in?: Maybe<Array<Scalars["String"]>>;
  curve_not_in?: Maybe<Array<Scalars["String"]>>;
  curve_contains?: Maybe<Scalars["String"]>;
  curve_not_contains?: Maybe<Scalars["String"]>;
  curve_starts_with?: Maybe<Scalars["String"]>;
  curve_not_starts_with?: Maybe<Scalars["String"]>;
  curve_ends_with?: Maybe<Scalars["String"]>;
  curve_not_ends_with?: Maybe<Scalars["String"]>;
  criteriaSet?: Maybe<Scalars["String"]>;
  criteriaSet_not?: Maybe<Scalars["String"]>;
  criteriaSet_gt?: Maybe<Scalars["String"]>;
  criteriaSet_lt?: Maybe<Scalars["String"]>;
  criteriaSet_gte?: Maybe<Scalars["String"]>;
  criteriaSet_lte?: Maybe<Scalars["String"]>;
  criteriaSet_in?: Maybe<Array<Scalars["String"]>>;
  criteriaSet_not_in?: Maybe<Array<Scalars["String"]>>;
  criteriaSet_contains?: Maybe<Scalars["String"]>;
  criteriaSet_not_contains?: Maybe<Scalars["String"]>;
  criteriaSet_starts_with?: Maybe<Scalars["String"]>;
  criteriaSet_not_starts_with?: Maybe<Scalars["String"]>;
  criteriaSet_ends_with?: Maybe<Scalars["String"]>;
  criteriaSet_not_ends_with?: Maybe<Scalars["String"]>;
  pnl?: Maybe<Scalars["BigDecimal"]>;
  pnl_not?: Maybe<Scalars["BigDecimal"]>;
  pnl_gt?: Maybe<Scalars["BigDecimal"]>;
  pnl_lt?: Maybe<Scalars["BigDecimal"]>;
  pnl_gte?: Maybe<Scalars["BigDecimal"]>;
  pnl_lte?: Maybe<Scalars["BigDecimal"]>;
  pnl_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnl_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlTotal?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_not?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlTotal_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlTotal_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_not?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lt?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_gte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_lte?: Maybe<Scalars["BigDecimal"]>;
  pnlPercentage_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  pnlPercentage_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_not?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lt?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_gte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_lte?: Maybe<Scalars["BigDecimal"]>;
  liquidityAtTrades_in?: Maybe<Array<Scalars["BigDecimal"]>>;
  liquidityAtTrades_not_in?: Maybe<Array<Scalars["BigDecimal"]>>;
};

export enum Template_OrderBy {
  Id = "id",
  Size = "size",
  Locked = "locked",
  Utilization = "utilization",
  NumPools = "numPools",
  Curve = "curve",
  CriteriaSet = "criteriaSet",
  Pnl = "pnl",
  PnlTotal = "pnlTotal",
  PnlPercentage = "pnlPercentage",
  LiquidityAtTrades = "liquidityAtTrades",
  Pools = "pools",
}

export type Token = {
  __typename?: "Token";
  id: Scalars["ID"];
  address: Scalars["Bytes"];
  decimals: Scalars["BigInt"];
  symbol: Scalars["String"];
  name: Scalars["String"];
};

export type Token_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  address?: Maybe<Scalars["Bytes"]>;
  address_not?: Maybe<Scalars["Bytes"]>;
  address_in?: Maybe<Array<Scalars["Bytes"]>>;
  address_not_in?: Maybe<Array<Scalars["Bytes"]>>;
  address_contains?: Maybe<Scalars["Bytes"]>;
  address_not_contains?: Maybe<Scalars["Bytes"]>;
  decimals?: Maybe<Scalars["BigInt"]>;
  decimals_not?: Maybe<Scalars["BigInt"]>;
  decimals_gt?: Maybe<Scalars["BigInt"]>;
  decimals_lt?: Maybe<Scalars["BigInt"]>;
  decimals_gte?: Maybe<Scalars["BigInt"]>;
  decimals_lte?: Maybe<Scalars["BigInt"]>;
  decimals_in?: Maybe<Array<Scalars["BigInt"]>>;
  decimals_not_in?: Maybe<Array<Scalars["BigInt"]>>;
  symbol?: Maybe<Scalars["String"]>;
  symbol_not?: Maybe<Scalars["String"]>;
  symbol_gt?: Maybe<Scalars["String"]>;
  symbol_lt?: Maybe<Scalars["String"]>;
  symbol_gte?: Maybe<Scalars["String"]>;
  symbol_lte?: Maybe<Scalars["String"]>;
  symbol_in?: Maybe<Array<Scalars["String"]>>;
  symbol_not_in?: Maybe<Array<Scalars["String"]>>;
  symbol_contains?: Maybe<Scalars["String"]>;
  symbol_not_contains?: Maybe<Scalars["String"]>;
  symbol_starts_with?: Maybe<Scalars["String"]>;
  symbol_not_starts_with?: Maybe<Scalars["String"]>;
  symbol_ends_with?: Maybe<Scalars["String"]>;
  symbol_not_ends_with?: Maybe<Scalars["String"]>;
  name?: Maybe<Scalars["String"]>;
  name_not?: Maybe<Scalars["String"]>;
  name_gt?: Maybe<Scalars["String"]>;
  name_lt?: Maybe<Scalars["String"]>;
  name_gte?: Maybe<Scalars["String"]>;
  name_lte?: Maybe<Scalars["String"]>;
  name_in?: Maybe<Array<Scalars["String"]>>;
  name_not_in?: Maybe<Array<Scalars["String"]>>;
  name_contains?: Maybe<Scalars["String"]>;
  name_not_contains?: Maybe<Scalars["String"]>;
  name_starts_with?: Maybe<Scalars["String"]>;
  name_not_starts_with?: Maybe<Scalars["String"]>;
  name_ends_with?: Maybe<Scalars["String"]>;
  name_not_ends_with?: Maybe<Scalars["String"]>;
};

export enum Token_OrderBy {
  Id = "id",
  Address = "address",
  Decimals = "decimals",
  Symbol = "symbol",
  Name = "name",
}

export type Underlying = {
  __typename?: "Underlying";
  id: Scalars["ID"];
  token: Token;
};

export type Underlying_Filter = {
  id?: Maybe<Scalars["ID"]>;
  id_not?: Maybe<Scalars["ID"]>;
  id_gt?: Maybe<Scalars["ID"]>;
  id_lt?: Maybe<Scalars["ID"]>;
  id_gte?: Maybe<Scalars["ID"]>;
  id_lte?: Maybe<Scalars["ID"]>;
  id_in?: Maybe<Array<Scalars["ID"]>>;
  id_not_in?: Maybe<Array<Scalars["ID"]>>;
  token?: Maybe<Scalars["String"]>;
  token_not?: Maybe<Scalars["String"]>;
  token_gt?: Maybe<Scalars["String"]>;
  token_lt?: Maybe<Scalars["String"]>;
  token_gte?: Maybe<Scalars["String"]>;
  token_lte?: Maybe<Scalars["String"]>;
  token_in?: Maybe<Array<Scalars["String"]>>;
  token_not_in?: Maybe<Array<Scalars["String"]>>;
  token_contains?: Maybe<Scalars["String"]>;
  token_not_contains?: Maybe<Scalars["String"]>;
  token_starts_with?: Maybe<Scalars["String"]>;
  token_not_starts_with?: Maybe<Scalars["String"]>;
  token_ends_with?: Maybe<Scalars["String"]>;
  token_not_ends_with?: Maybe<Scalars["String"]>;
};

export enum Underlying_OrderBy {
  Id = "id",
  Token = "token",
}

export type _Block_ = {
  __typename?: "_Block_";
  /** The hash of the block */
  hash?: Maybe<Scalars["Bytes"]>;
  /** The block number */
  number: Scalars["Int"];
};

/** The type for the top-level _meta field */
export type _Meta_ = {
  __typename?: "_Meta_";
  /**
   * Information about a specific subgraph block. The hash of the block
   * will be null if the _meta field has a block constraint that asks for
   * a block number. It will be filled if the _meta field has no block constraint
   * and therefore asks for the latest  block
   *
   */
  block: _Block_;
  /** The deployment ID */
  deployment: Scalars["String"];
  /** If `true`, the subgraph encountered indexing errors at some past block */
  hasIndexingErrors: Scalars["Boolean"];
};

export enum _SubgraphErrorPolicy_ {
  /** Data will be returned even if the subgraph has indexing errors */
  Allow = "allow",
  /** If the subgraph has indexing errors, data will be omitted. The default. */
  Deny = "deny",
}

export type CurveFragmentFragment = {
  __typename?: "Curve";
  a: any;
  b: any;
  c: any;
  d: any;
  maxUtil: any;
};

export type TokenFragmentFragment = {
  __typename?: "Token";
  address: any;
  decimals: any;
  symbol: string;
  name: string;
};

export type CriteriaFragmentFragment = {
  __typename?: "Criteria";
  maxStrikePercent: any;
  maxDurationInDays: any;
  isPut: boolean;
  id: string;
  strikeAsset: {
    __typename?: "Token";
    address: any;
    decimals: any;
    symbol: string;
    name: string;
  };
  underlyingAsset: {
    __typename?: "Token";
    address: any;
    decimals: any;
    symbol: string;
    name: string;
  };
};

export type TemplateFragmentFragment = {
  __typename?: "Template";
  id: string;
  liquidityAtTrades: any;
  locked: any;
  numPools: any;
  pnlPercentage: any;
  pnlTotal: any;
  size: any;
  utilization: any;
};

export type PoolFragmentFragment = {
  __typename?: "Pool";
  averageCost?: Maybe<any>;
  id: string;
  initialBalance?: Maybe<any>;
  liquidityAtTrades: any;
  locked: any;
  lp: any;
  pnlPercentage: any;
  pnlTotal: any;
  poolId: any;
  size: any;
  unlocked: any;
  utilization: any;
};

export type PoolRecordFragmentFragment = {
  __typename?: "PoolRecord";
  collateral: any;
  id: string;
  numberOfOTokens: any;
  premiumReceived: any;
  returned?: Maybe<any>;
};

export type LpRecordFragmentFragment = {
  __typename?: "LPRecord";
  id: string;
  liquidityCollateralized: any;
  lp: any;
  numberOfOTokens: any;
  premiumReceived: any;
};

export type OTokenFragmentFragment = {
  __typename?: "OToken";
  collateralized: any;
  creator: any;
  decimals: any;
  expiry: any;
  id: string;
  isPut: boolean;
  liquiditySettled: any;
  numberOfOTokens: any;
  premium: any;
  purchasesCount: any;
  settled: boolean;
  strikePrice: any;
  tokenAddress: any;
  collateralAsset: {
    __typename?: "Token";
    address: any;
    decimals: any;
    symbol: string;
    name: string;
  };
  strikeAsset: {
    __typename?: "Token";
    address: any;
    decimals: any;
    symbol: string;
    name: string;
  };
  underlyingAsset: {
    __typename?: "Token";
    address: any;
    decimals: any;
    symbol: string;
    name: string;
  };
};

export type PoolSnapshotFragmentFragment = {
  __typename?: "PoolSnapshot";
  actionAmount: any;
  actionType: any;
  id: string;
  initialBalance?: Maybe<any>;
  liquidityAtTrades: any;
  locked: any;
  lp?: Maybe<any>;
  pnlPercentage: any;
  pnlTotal: any;
  poolId: any;
  size: any;
  templateLiquidityAtTrades?: Maybe<any>;
  templatePnlPercentage?: Maybe<any>;
  templatePnlTotal?: Maybe<any>;
  templateSize?: Maybe<any>;
  templateUtilization?: Maybe<any>;
  timestamp: any;
  unlocked: any;
  utilization: any;
};

export type TemplateQueryVariables = Exact<{
  id: Scalars["ID"];
}>;

export type TemplateQuery = {
  __typename?: "Query";
  template?: Maybe<{
    __typename?: "Template";
    id: string;
    liquidityAtTrades: any;
    locked: any;
    numPools: any;
    pnlPercentage: any;
    pnlTotal: any;
    size: any;
    utilization: any;
    curve?: Maybe<{
      __typename?: "Curve";
      a: any;
      b: any;
      c: any;
      d: any;
      maxUtil: any;
    }>;
    criteriaSet?: Maybe<{
      __typename?: "CriteriaSet";
      criterias: Array<{
        __typename?: "CriteriaJoinedCriteriaSet";
        criteria: {
          __typename?: "Criteria";
          maxStrikePercent: any;
          maxDurationInDays: any;
          isPut: boolean;
          id: string;
          strikeAsset: {
            __typename?: "Token";
            address: any;
            decimals: any;
            symbol: string;
            name: string;
          };
          underlyingAsset: {
            __typename?: "Token";
            address: any;
            decimals: any;
            symbol: string;
            name: string;
          };
        };
      }>;
    }>;
  }>;
};

export type PoolQueryVariables = Exact<{
  id: Scalars["ID"];
}>;

export type PoolQuery = {
  __typename?: "Query";
  pool?: Maybe<{
    __typename?: "Pool";
    averageCost?: Maybe<any>;
    id: string;
    initialBalance?: Maybe<any>;
    liquidityAtTrades: any;
    locked: any;
    lp: any;
    pnlPercentage: any;
    pnlTotal: any;
    poolId: any;
    size: any;
    unlocked: any;
    utilization: any;
    template?: Maybe<{
      __typename?: "Template";
      id: string;
      liquidityAtTrades: any;
      locked: any;
      numPools: any;
      pnlPercentage: any;
      pnlTotal: any;
      size: any;
      utilization: any;
      curve?: Maybe<{
        __typename?: "Curve";
        a: any;
        b: any;
        c: any;
        d: any;
        maxUtil: any;
      }>;
      criteriaSet?: Maybe<{
        __typename?: "CriteriaSet";
        criterias: Array<{
          __typename?: "CriteriaJoinedCriteriaSet";
          criteria: {
            __typename?: "Criteria";
            maxStrikePercent: any;
            maxDurationInDays: any;
            isPut: boolean;
            id: string;
            strikeAsset: {
              __typename?: "Token";
              address: any;
              decimals: any;
              symbol: string;
              name: string;
            };
            underlyingAsset: {
              __typename?: "Token";
              address: any;
              decimals: any;
              symbol: string;
              name: string;
            };
          };
        }>;
      }>;
    }>;
  }>;
};

export type PoolsQueryVariables = Exact<{ [key: string]: never }>;

export type PoolsQuery = {
  __typename?: "Query";
  pools: Array<{
    __typename?: "Pool";
    averageCost?: Maybe<any>;
    id: string;
    initialBalance?: Maybe<any>;
    liquidityAtTrades: any;
    locked: any;
    lp: any;
    pnlPercentage: any;
    pnlTotal: any;
    poolId: any;
    size: any;
    unlocked: any;
    utilization: any;
    template?: Maybe<{
      __typename?: "Template";
      id: string;
      liquidityAtTrades: any;
      locked: any;
      numPools: any;
      pnlPercentage: any;
      pnlTotal: any;
      size: any;
      utilization: any;
      curve?: Maybe<{
        __typename?: "Curve";
        a: any;
        b: any;
        c: any;
        d: any;
        maxUtil: any;
      }>;
      criteriaSet?: Maybe<{
        __typename?: "CriteriaSet";
        criterias: Array<{
          __typename?: "CriteriaJoinedCriteriaSet";
          criteria: {
            __typename?: "Criteria";
            maxStrikePercent: any;
            maxDurationInDays: any;
            isPut: boolean;
            id: string;
            strikeAsset: {
              __typename?: "Token";
              address: any;
              decimals: any;
              symbol: string;
              name: string;
            };
            underlyingAsset: {
              __typename?: "Token";
              address: any;
              decimals: any;
              symbol: string;
              name: string;
            };
          };
        }>;
      }>;
    }>;
  }>;
};
