import { BigInt, Address } from "@graphprotocol/graph-ts";
import { IERC20MetadataUpgradeable as ERC20 } from "../generated/Whitelist/IERC20MetadataUpgradeable";

export function getTokenDecimals(tokenAddress: Address): BigInt {
  const contract = ERC20.bind(tokenAddress);
  let decimals = 0;

  const result = contract.try_decimals();
  if (!result.reverted) {
    decimals = result.value;
  }

  return BigInt.fromI32(decimals as i32);
}

export function getTokenName(tokenAddress: Address): string {
  const contract = ERC20.bind(tokenAddress);
  let name = "";

  const result = contract.try_name();
  if (!result.reverted) {
    name = result.value;
  }

  return name;
}

export function getTokenSymbol(tokenAddress: Address): string {
  const contract = ERC20.bind(tokenAddress);
  let symbol = "";

  const result = contract.try_symbol();
  if (!result.reverted) {
    symbol = result.value;
  }

  return symbol;
}
