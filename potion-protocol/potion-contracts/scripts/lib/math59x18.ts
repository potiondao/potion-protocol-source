import { BigNumber, parseFixed } from '@ethersproject/bignumber'
import fromExponential from 'from-exponential'

import BigDecimal from 'bignumber.js'

BigDecimal.config({ EXPONENTIAL_AT: 60 })

type BigDecimalish = string | BigDecimal | number
const DENOMINATOR = BigNumber.from(2).pow(64)

/**
 * Return two parts array of exponential number
 */
function getExponentialParts(num: number | string): string[] {
  return String(num).split(/[eE]/)
}

function isExponential(num: number | string): boolean {
  const eParts = getExponentialParts(num)
  return !Number.isNaN(Number(eParts[1]))
}

// TypeScript equivalent of PRB Math, for working with 59x18 bit fixed-point decimals.
export class Int59x18 {
  private static asBigNumberFromString(x: string): BigNumber {
    const precision = 18

    if (isExponential(x)) {
      return parseFixed(fromExponential(x), precision)
    } else {
      // Check if x is either a whole number with up to 60 digits or a fixed-point number with up to 60 digits and up to 18 decimals.
      if (!/^[-+]?(\d{1,60}|(?=\d+\.\d+)\d{1,60}\.\d{1,18})$/.test(x)) {
        throw new Error(`Unknown format for fixed-point number: ${x}`)
      }
      return parseFixed(x, precision)
    }
  }

  constructor(public value: BigNumber) {}

  static fromDecimal(decimal: BigDecimalish): Int59x18 {
    const inputAsString = decimal.toString()
    return new this(Int59x18.asBigNumberFromString(inputAsString))
  }

  // A string including the object type
  toString(): string {
    return `Int59x18:<${this.value} (~${new BigDecimal(this.value.toString())
      .div(new BigDecimal(DENOMINATOR.toString()))
      .toString()}>`
  }

  // A string that's parseable as a BigDecimal
  toNumberString(): string {
    return `${new BigDecimal(this.value.toString()).div(new BigDecimal(DENOMINATOR.toString())).toString()}`
  }

  approximateAsString(): string {
    const decimal = new BigDecimal(this.value.toString())
    return `Int59x18:<${decimal.toExponential(13)}>`
  }
}
