import {
  CollateralWhitelisted,
  ProductWhitelisted,
} from "../generated/Whitelist/Whitelist";
import { BigInt, Address, BigDecimal, log } from "@graphprotocol/graph-ts";
import { Token, Underlying, Collateral, Product } from "../generated/schema";
import { getTokenDecimals, getTokenName, getTokenSymbol } from "./tokenHelpers";
import { bigIntToDecimal } from "./helpers";

export const COLLATERAL_ID = "0";

export function getCollateralDecimals(): BigInt {
  const collateral = Collateral.load(COLLATERAL_ID)!;
  const token = Token.load(collateral.token)!;
  return token.decimals;
}

export function collateralFixedtoDecimals(value: BigInt): BigDecimal {
  // TEMPORARY WORKAROUND: We only use stable coins as collateral that always have 6 decimals
  // For a proper solution we probably need more data (eg, the address of the token that we are using as collateral and not only the amount)
  // const decimals = getCollateralDecimals();
  const decimals = 6;
  const decimalsInt = parseInt(decimals.toString());
  return bigIntToDecimal(value, decimalsInt as i32);
}

export function createTokenId(address: Address): string {
  return address.toHexString();
}

function createToken(address: Address): void {
  const tokenId = createTokenId(address);
  let token = Token.load(tokenId);

  if (token == null) {
    token = new Token(tokenId);
    token.address = address;
    token.decimals = getTokenDecimals(address);
    token.name = getTokenName(address);
    token.symbol = getTokenSymbol(address);
    token.save();
  }
}

// Create an entity for the underlying of the product (if it does not exist already).
export function handleProductWhitelist(event: ProductWhitelisted): void {
  const underlyingAddress = event.params.underlying;
  createToken(underlyingAddress as Address);
  const tokenId = createTokenId(underlyingAddress as Address);
  let underlying = Underlying.load(tokenId);

  if (underlying == null) {
    underlying = new Underlying(tokenId);
    underlying.token = tokenId;
    underlying.save();
  }

  const productID =
    event.params.underlying.toHexString() +
    event.params.strike.toHexString() +
    event.params.collateral.toHexString();
  const product = new Product(productID);
  product.underlying = event.params.underlying.toHexString();
  product.strike = event.params.strike.toHexString();
  product.collateral = event.params.collateral.toHexString();
  product.isPut = event.params.isPut;
  product.isWhitelisted = true;
  product.save();
}

export function createCollateral(collateralAddress: Address): void {
  log.info("Creating collateral {}", [collateralAddress.toHexString()]);
  createToken(collateralAddress);
  const tokenId = createTokenId(collateralAddress);
  // Since we can only have one collateral token in the current
  // smart contracts architecture, fix the id to 0.
  let collateral = Collateral.load(COLLATERAL_ID);

  if (collateral == null) {
    collateral = new Collateral(COLLATERAL_ID);
    collateral.token = tokenId;
    collateral.save();
  }
}

// Create an entity for a collateral that is whitelisted.
export function handleCollateralWhitelist(event: CollateralWhitelisted): void {
  const collateralAddress = event.params.collateral;
  createCollateral(collateralAddress as Address);
}
