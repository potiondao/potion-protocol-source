/*
 * Functions used to assert the equality of fields in an entity with some parameters
 * used to make the unit tests easier to read
 */

import { assert } from "matchstick-as/assembly/index";
import { ethereum, BigInt, BigDecimal } from "@graphprotocol/graph-ts";
import { Pool, OToken, Template, Curve, Criteria } from "../generated/schema";

export function assertPoolLiquidity(
  pool: Pool,
  size: string,
  unlocked: string,
  locked: string,
  initialBalance: string
): void {
  assert.equals(
    ethereum.Value.fromString(size),
    ethereum.Value.fromString(pool.size.toString())
  );
  assert.equals(
    ethereum.Value.fromString(unlocked),
    ethereum.Value.fromString(pool.unlocked.toString())
  );
  assert.equals(
    ethereum.Value.fromString(locked),
    ethereum.Value.fromString(pool.locked.toString())
  );
  if (pool.initialBalance) {
    assert.equals(
      ethereum.Value.fromString(initialBalance),
      ethereum.Value.fromString((pool.initialBalance as BigDecimal).toString())
    );
  } else {
    // raise error
  }
}

export function assertPoolMarketData(
  pool: Pool,
  pnlTotal: string,
  pnlPercentage: string,
  liquidityAtTrades: string
): void {
  assert.equals(
    ethereum.Value.fromString(pnlTotal),
    ethereum.Value.fromString(pool.pnlTotal.toString())
  );
  assert.equals(
    ethereum.Value.fromString(pnlPercentage),
    ethereum.Value.fromString(pool.pnlPercentage.toString())
  );
  assert.equals(
    ethereum.Value.fromString(liquidityAtTrades),
    ethereum.Value.fromString(pool.liquidityAtTrades.toString())
  );
}

export function assertTemplateLiquidity(
  template: Template,
  size: string,
  locked: string
): void {
  assert.equals(
    ethereum.Value.fromString(size),
    ethereum.Value.fromString(template.size.toString())
  );
  assert.equals(
    ethereum.Value.fromString(locked),
    ethereum.Value.fromString(template.locked.toString())
  );
}

export function assertCurveEquality(
  curve: Curve,
  a: string,
  b: string,
  c: string,
  d: string,
  maxUtil: string
): void {
  assert.equals(
    ethereum.Value.fromString(a),
    ethereum.Value.fromString(curve.a.toString())
  );
  assert.equals(
    ethereum.Value.fromString(b),
    ethereum.Value.fromString(curve.b.toString())
  );
  assert.equals(
    ethereum.Value.fromString(c),
    ethereum.Value.fromString(curve.c.toString())
  );
  assert.equals(
    ethereum.Value.fromString(d),
    ethereum.Value.fromString(curve.d.toString())
  );
  assert.equals(
    ethereum.Value.fromString(maxUtil),
    ethereum.Value.fromString(curve.maxUtil.toString())
  );
}

export function assertCriteriaEquality(
  criteria: Criteria,
  isPut: boolean,
  maxStrikePercent: string,
  maxDurationInDays: string
): void {
  assert.equals(
    ethereum.Value.fromBoolean(isPut),
    ethereum.Value.fromBoolean(criteria.isPut)
  );
  assert.equals(
    ethereum.Value.fromString(maxStrikePercent),
    ethereum.Value.fromString(criteria.maxStrikePercent.toString())
  );
  assert.equals(
    ethereum.Value.fromString(maxDurationInDays),
    ethereum.Value.fromString(criteria.maxDurationInDays.toString())
  );
}

export function assertOtokenEquality(
  otoken: OToken,
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
): void {
  assert.equals(
    ethereum.Value.fromString(tokenAddress),
    ethereum.Value.fromString(otoken.tokenAddress.toHexString())
  );
  assert.equals(
    ethereum.Value.fromString(creator),
    ethereum.Value.fromString(otoken.creator.toHexString())
  );
  assert.equals(
    ethereum.Value.fromString(underlyingAsset),
    ethereum.Value.fromString(otoken.underlyingAsset)
  );
  assert.equals(
    ethereum.Value.fromString(strikeAsset),
    ethereum.Value.fromString(otoken.strikeAsset)
  );
  assert.equals(
    ethereum.Value.fromString(collateralAsset),
    ethereum.Value.fromString(otoken.collateralAsset)
  );
  assert.equals(
    ethereum.Value.fromString(strikePrice.toString()),
    ethereum.Value.fromString(otoken.strikePrice.toString())
  );
  assert.equals(
    ethereum.Value.fromUnsignedBigInt(expiry),
    ethereum.Value.fromUnsignedBigInt(otoken.expiry)
  );
  assert.equals(
    ethereum.Value.fromBoolean(isPut),
    ethereum.Value.fromBoolean(otoken.isPut)
  );
  assert.equals(
    ethereum.Value.fromUnsignedBigInt(decimals),
    ethereum.Value.fromUnsignedBigInt(otoken.decimals)
  );
  assert.equals(
    ethereum.Value.fromBoolean(settled),
    ethereum.Value.fromBoolean(otoken.settled)
  );
  assert.equals(
    ethereum.Value.fromString(premium.toString()),
    ethereum.Value.fromString(otoken.premium.toString())
  );
  assert.equals(
    ethereum.Value.fromString(collateralized.toString()),
    ethereum.Value.fromString(otoken.collateralized.toString())
  );
  assert.equals(
    ethereum.Value.fromString(liquiditySettled.toString()),
    ethereum.Value.fromString(otoken.liquiditySettled.toString())
  );
  assert.equals(
    ethereum.Value.fromString(numberOfOTokens.toString()),
    ethereum.Value.fromString(otoken.numberOfOTokens.toString())
  );
  assert.equals(
    ethereum.Value.fromUnsignedBigInt(purchasesCount),
    ethereum.Value.fromUnsignedBigInt(otoken.purchasesCount)
  );
}
