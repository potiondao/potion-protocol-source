import { BigInt, BigDecimal, Bytes } from "@graphprotocol/graph-ts";
import { Pool } from "../generated/schema";

const PRECISION = 18;

export function bigIntToDecimal(amount: BigInt, decimals: i32): BigDecimal {
  const scale = BigInt.fromI32(10)
    .pow(decimals as u8)
    .toBigDecimal();
  return amount.toBigDecimal().div(scale);
}

export function tokenToDecimal(amount: BigDecimal, decimals: i32): BigDecimal {
  const scale = BigInt.fromI32(10)
    .pow(decimals as u8)
    .toBigDecimal();
  return amount.div(scale);
}

export function int59x18ToDecimal(amount: BigInt): BigDecimal {
  return bigIntToDecimal(amount, PRECISION);
}

export function copyBigInt(num: BigInt): BigInt {
  return BigInt.fromI32(num.toI32());
}

export function copyBigDecimal(num: BigDecimal): BigDecimal {
  return BigDecimal.fromString(num.toString());
}

export function copyBytes(bytes: Bytes): Bytes {
  return Bytes.fromHexString(bytes.toHexString()) as Bytes;
}

export function copyPool(pool: Pool): Pool {
  const newPool = new Pool(pool.id);
  newPool.poolId = copyBigInt(pool.poolId);
  newPool.lp = copyBytes(pool.lp);
  newPool.size = copyBigDecimal(pool.size);
  newPool.locked = copyBigDecimal(pool.locked);
  newPool.template = pool.template;
  return newPool;
}

export function findIndex(array: BigInt[], value: BigInt): number {
  for (let i = 0; i < array.length; i++) {
    if (array[i].equals(value)) return i;
    i++;
  }
  return null;
}
