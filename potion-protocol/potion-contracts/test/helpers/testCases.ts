import { Int59x18 } from '../../scripts/lib/math59x18'
import { HyperbolicCurve } from '../../scripts/lib/typeHelpers'

export class PowerDecimalTestCase {
  public in_base_59x18: Int59x18
  public in_exponent_59x18: Int59x18
  public out_59x18: Int59x18

  constructor(
    public in_base_number: number, // base
    public in_exponent_number: number, // exponent
  ) {
    this.in_base_59x18 = Int59x18.fromDecimal(in_base_number)
    this.in_exponent_59x18 = Int59x18.fromDecimal(in_exponent_number)

    this.out_59x18 = Int59x18.fromDecimal(Math.pow(in_base_number, in_exponent_number))
  }
}

// For use in testing solidity's evaluation of cosh(x)
export class CoshTestCase {
  public in_59x18: Int59x18 // x
  public out_59x18: Int59x18 // expected cosh(x)

  constructor(public in_number: number) {
    this.in_59x18 = Int59x18.fromDecimal(in_number)
    this.out_59x18 = Int59x18.fromDecimal(Math.cosh(in_number))
  }
}

export class HyperbolicCurveTestCase {
  public x_59x18: Int59x18

  constructor(public curve: HyperbolicCurve, public x_number: number) {
    this.x_59x18 = Int59x18.fromDecimal(x_number)
  }

  answer(): Int59x18 {
    return Int59x18.fromDecimal(this.curve.evalAt(this.x_number).toFixed(14))
  }
}
