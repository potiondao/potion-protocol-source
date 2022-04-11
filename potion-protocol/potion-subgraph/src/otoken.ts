import { BigInt, BigDecimal, Bytes } from "@graphprotocol/graph-ts";

import { OtokenCreated } from "../generated/OtokenFactoryContract/OtokenFactoryContract";
import { OToken } from "../generated/schema";
import { Otoken } from "../generated/OtokenFactoryContract/Otoken";
import { createTokenId, collateralFixedtoDecimals } from "./token";
import { bigIntToDecimal } from "./helpers";

export function getOTokenIdFromEvent(event: OtokenCreated): string {
  return event.params.tokenAddress.toHexString();
}

export function getOTokenIdFromAddress(tokenHexAdress: Bytes): string {
  return tokenHexAdress.toHexString();
}

export function getOtokenDecimals(address: Bytes): BigInt {
  const id = getOTokenIdFromAddress(address);
  const oTokenEntity = OToken.load(id)!;
  return oTokenEntity.decimals;
}

/**
 * Function converts an Integer oToken amount to the number of decimals
   that the oToken has.
 * @param {Bytes} address Descriptor of the event emitted.
 * @param {BigInt} value Integer to convert to Fixed Precision
 */
export function oTokenFixedtoDecimals(
  address: Bytes,
  value: BigInt
): BigDecimal {
  const decimals = getOtokenDecimals(address);
  const decimalsInt = parseInt(decimals.toString());
  return bigIntToDecimal(value, decimalsInt as i32);
}

/**
 * Called when a OtokenCreated event is emitted. Creates an oToken
   entity.
 * @param {OtokenCreated} event Descriptor of the event emitted.
 */
export function handleOtokenCreate(event: OtokenCreated): void {
  const oTokenID = getOTokenIdFromEvent(event);
  let otoken = OToken.load(oTokenID);
  if (otoken == null) {
    otoken = new OToken(oTokenID);
  }
  otoken.tokenAddress = event.params.tokenAddress;
  otoken.creator = event.params.creator;
  otoken.underlyingAsset = createTokenId(event.params.underlying);
  otoken.strikeAsset = createTokenId(event.params.strike);
  otoken.collateralAsset = createTokenId(event.params.collateral);
  otoken.strikePrice = bigIntToDecimal(event.params.strikePrice, 8 as i32);
  otoken.expiry = event.params.expiry;
  otoken.isPut = event.params.isPut;
  otoken.settled = false;
  otoken.premium = BigDecimal.fromString("0");
  otoken.collateralized = BigDecimal.fromString("0");
  otoken.liquiditySettled = BigDecimal.fromString("0");
  otoken.numberOfOTokens = BigDecimal.fromString("0");
  otoken.purchasesCount = BigInt.fromI32(0 as i32);

  const oTokenContract = Otoken.bind(event.params.tokenAddress);
  const oTokenDecimalResult = oTokenContract.try_decimals();
  if (!oTokenDecimalResult.reverted) {
    otoken.decimals = BigInt.fromI32(oTokenDecimalResult.value as i32);
  }
  otoken.save();
}

/**
 * Settles an oToken and sets its liquiditySettled field.
 * @param {Bytes} oToken Address of the oToken.
 * @param {BigInt} collateralReturned Amount of collateral returned to Pools.
 */
export function oTokenSettled(oToken: Bytes, collateralReturned: BigInt): void {
  const oTokenID = getOTokenIdFromAddress(oToken);
  const otoken = OToken.load(oTokenID);

  if (otoken) {
    otoken.settled = true;
    otoken.liquiditySettled = collateralFixedtoDecimals(collateralReturned);
    otoken.save();
  }
}

/**
 * Increments the number of oTokens and liquidity that is collateralized by a
   specific oToken.
 * @param {Bytes} oTokenAddress Address of the oToken.
 * @param {BigInt} numberOfOtokens Number of oTokens created.
 * @param {BigInt} liquidityCollateralized Amount of liquidity locked.
 * @param {BigInt} premiumReceived Amount of premium paid for numberOfOtokens.
 */
export function oTokenIncrementLiquidity(
  oTokenAddress: Bytes,
  numberOfOtokens: BigInt,
  liquidityCollateralized: BigInt,
  premiumReceived: BigInt
): void {
  const oTokenID = getOTokenIdFromAddress(oTokenAddress);
  const otoken = OToken.load(oTokenID);
  if (otoken) {
    const tokensDecimals = oTokenFixedtoDecimals(
      oTokenAddress,
      numberOfOtokens
    );
    const liquidityCollateralizedDecimals = collateralFixedtoDecimals(
      liquidityCollateralized
    );
    const premiumReceivedDecimals = collateralFixedtoDecimals(premiumReceived);

    otoken.numberOfOTokens = otoken.numberOfOTokens.plus(tokensDecimals);
    otoken.collateralized = otoken.collateralized.plus(
      liquidityCollateralizedDecimals
    );
    otoken.premium = otoken.premium.plus(premiumReceivedDecimals);
    otoken.save();
  }
}

/**
 * Called when a unique buyer purchases a oToken, increments purchasesCount.
 * @param {Bytes} oTokenAddress Address of the oToken.
 */
export function oTokenIncrementPurchasesCount(oTokenAddress: Bytes): void {
  const oTokenID = getOTokenIdFromAddress(oTokenAddress);
  const otoken = OToken.load(oTokenID);

  if (otoken) {
    otoken.purchasesCount = otoken.purchasesCount.plus(
      BigInt.fromI32(1 as i32)
    );
    otoken.save();
  }
}
