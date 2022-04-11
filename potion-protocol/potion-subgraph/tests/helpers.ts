import {
  Pool,
  Template,
  Curve,
  Criteria,
  CriteriaSet,
  OToken,
  CriteriaJoinedCriteriaSet,
} from "../generated/schema";
import {
  createPool,
  createPoolId,
  createTemplate,
  createTemplateId,
} from "../src/pools";

import { BigInt, Address, BigDecimal, Bytes } from "@graphprotocol/graph-ts";
import {
  COLLATERAL_PRECISION_BIG_INT,
  CURVE_PRECISION_BIG_INT,
  STRIKE_PRECISION_BIG_INT,
} from "./constants";
import { createCriteriaJoinedCriteriaSetId } from "../src/criterias";

export function createNewPool(
  lp: Address,
  poolId: BigInt,
  size: string,
  templateId: string
): Pool {
  const poolSize = BigDecimal.fromString(size);
  const id = createPoolId(lp, poolId);
  const pool = createPool(id, lp, poolId);
  pool.template = templateId;
  pool.size = poolSize;
  pool.unlocked = poolSize;
  pool.initialBalance = poolSize;
  return pool;
}

export function createNewTemplate(
  curveHash: string,
  criteriaSetHash: string,
  size: string,
  locked: string,
  lp: Bytes
): Template {
  const id = createTemplateId(
    Bytes.fromHexString(curveHash) as Bytes,
    Bytes.fromHexString(criteriaSetHash) as Bytes
  );
  const template = createTemplate(id, curveHash, criteriaSetHash, lp);
  template.size = BigDecimal.fromString(size);
  template.locked = BigDecimal.fromString(locked);
  return template;
}

export function createNewCurve(
  id: string,
  a: BigDecimal,
  b: BigDecimal,
  c: BigDecimal,
  d: BigDecimal,
  maxUtil: BigDecimal
): Curve {
  const curve = new Curve(id);
  curve.a = a;
  curve.b = b;
  curve.c = c;
  curve.d = d;
  curve.maxUtil = maxUtil;
  return curve;
}

export function toCurveParam(value: string): BigInt {
  return BigInt.fromString(value).times(CURVE_PRECISION_BIG_INT);
}

export function formatCollateral(value: string): BigInt {
  return BigInt.fromString(value).times(COLLATERAL_PRECISION_BIG_INT);
}

export function formatStrike(value: string): BigInt {
  return BigInt.fromString(value).times(STRIKE_PRECISION_BIG_INT);
}

export function createNewCriteria(
  id: string,
  underlyingAsset: string,
  strikeAsset: string,
  isPut: boolean,
  maxStrikePercent: BigDecimal,
  maxDurationInDays: BigInt
): Criteria {
  const criteria = new Criteria(id);
  criteria.underlyingAsset = underlyingAsset;
  criteria.strikeAsset = strikeAsset;
  criteria.isPut = isPut;
  criteria.maxStrikePercent = maxStrikePercent;
  criteria.maxDurationInDays = maxDurationInDays;
  return criteria;
}

export function createNewCriteriaSet(id: string): CriteriaSet {
  const criteriaSet = new CriteriaSet(id);
  return criteriaSet;
}

export function createNewCriteriaJoinedCriteriaSet(
  criteriaId: string,
  criteriaSetId: string
): CriteriaJoinedCriteriaSet {
  const id = createCriteriaJoinedCriteriaSetId(
    Bytes.fromHexString(criteriaId) as Bytes,
    Bytes.fromHexString(criteriaSetId) as Bytes
  );
  const criteriaJoinedCriteriaSet = new CriteriaJoinedCriteriaSet(id);

  criteriaJoinedCriteriaSet.criteria = criteriaId;
  criteriaJoinedCriteriaSet.criteriaSet = criteriaSetId;
  return criteriaJoinedCriteriaSet;
}

export function createNewOtoken(
  id: string,
  tokenAddress: string,
  creator: string,
  underlyingAsset: string,
  strikeAsset: string,
  collateralAsset: string,
  strikePrice: BigDecimal,
  expiry: BigInt,
  isPut: boolean,
  decimals: BigInt,
  settled: boolean,
  premium: BigDecimal,
  collateralized: BigDecimal,
  liquiditySettled: BigDecimal,
  numberOfOTokens: BigDecimal,
  purchasesCount: BigInt
): OToken {
  const otoken = new OToken(id);
  otoken.tokenAddress = Bytes.fromHexString(tokenAddress) as Bytes;
  otoken.creator = Bytes.fromHexString(creator) as Bytes;
  otoken.underlyingAsset = underlyingAsset;
  otoken.strikeAsset = strikeAsset;
  otoken.collateralAsset = collateralAsset;
  otoken.strikePrice = strikePrice;
  otoken.expiry = expiry;
  otoken.isPut = isPut;
  otoken.decimals = decimals;
  otoken.settled = settled;
  otoken.premium = premium;
  otoken.collateralized = collateralized;
  otoken.liquiditySettled = liquiditySettled;
  otoken.numberOfOTokens = numberOfOTokens;
  otoken.purchasesCount = purchasesCount;

  return otoken;
}
