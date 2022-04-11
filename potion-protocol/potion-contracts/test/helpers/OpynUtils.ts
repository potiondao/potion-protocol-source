import { BigNumber, BigNumberish } from 'ethers'

export type vault = {
  shortAmounts: BigNumber[]
  longAmounts: BigNumber[]
  collateralAmounts: BigNumber[]
  shortOtokens: string[]
  longOtokens: string[]
  collateralAssets: string[]
}

const SECONDS_PER_DAY = 86400
const SECONDS_TO_8AM = 28800

/**
 * Return a valid expiry timestamp that's today + # days, 0800 UTC.
 * @param now
 * @param days
 */
export const createValidExpiry = (now: number, days: number, roundForward = false): number => {
  const multiplier = (now - SECONDS_TO_8AM) / SECONDS_PER_DAY
  const last8amUTC = Math.floor(multiplier) * SECONDS_PER_DAY + SECONDS_TO_8AM
  const next8amUTC = last8amUTC + SECONDS_PER_DAY
  // console.log(`multiplier:${multiplier};last8amUTC:${last8amUTC};next8amUTC:${next8amUTC}`)
  return (roundForward ? next8amUTC : last8amUTC) + days * SECONDS_PER_DAY
}

/**
 * Create a vault for testing
 * @param shortOtoken
 * @param longOtoken
 * @param collateralAsset
 * @param shortAmount
 * @param longAmount
 * @param collateralAmount
 */
export const createVault = (
  shortOtoken: string | undefined,
  longOtoken: string | undefined,
  collateralAsset: string | undefined,
  shortAmount: BigNumberish | undefined,
  longAmount: BigNumberish | undefined,
  collateralAmount: BigNumberish | undefined,
): vault => {
  return {
    shortOtokens: shortOtoken ? [shortOtoken] : [],
    longOtokens: longOtoken ? [longOtoken] : [],
    collateralAssets: collateralAsset ? [collateralAsset] : [],
    shortAmounts: shortAmount !== undefined ? [BigNumber.from(shortAmount)] : [],
    longAmounts: longAmount !== undefined ? [BigNumber.from(longAmount)] : [],
    collateralAmounts: collateralAmount !== undefined ? [BigNumber.from(collateralAmount)] : [],
  }
}

export const createTokenAmount = (num: BigNumberish, decimals = 8): BigNumber => {
  return BigNumber.from(num).mul(BigNumber.from(10).pow(decimals))
}

const MAX_SAFE_INTEGER_BEFORE_SCALING = Math.floor(Number.MAX_SAFE_INTEGER / 1e8)

/**
 * Create a number string that scales numbers to 1e8
 * @param num
 */
export const createScaledNumber = (num: number): BigNumber => {
  if (num < MAX_SAFE_INTEGER_BEFORE_SCALING) {
    // To cope with decimals, we multiply before converting to BigNumber
    return BigNumber.from(Math.floor(num * 1e8))
  } else {
    // This is a large number; not safe to multiply as a `number` so convert to BigNumber first
    return BigNumber.from(Math.floor(num)).mul(1e8)
  }
}
