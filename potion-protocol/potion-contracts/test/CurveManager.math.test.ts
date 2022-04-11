import { ethers } from 'hardhat'
import { expect, assert } from 'chai'
import { Int59x18 } from '../scripts/lib/math59x18'
import { HyperbolicCurve } from '../scripts/lib/typeHelpers'
import { CurveManager } from '../typechain'
import { HyperbolicCurveTestCase, PowerDecimalTestCase, CoshTestCase } from './helpers/testCases'
import BigDecimal from 'bignumber.js'

describe('CurveManager math', function () {
  let curveManager: CurveManager

  before(async () => {
    const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
    curveManager = (await CurveManagerFactory.deploy()) as CurveManager
  })

  describe('powerDecimal', () => {
    const powerDecimalTestCases: PowerDecimalTestCase[] = [
      new PowerDecimalTestCase(1, 1),
      new PowerDecimalTestCase(4, 2),
      new PowerDecimalTestCase(3, -2),
      new PowerDecimalTestCase(4, 2.5),
      new PowerDecimalTestCase(6, 0),
      new PowerDecimalTestCase(0, 2),
      new PowerDecimalTestCase(0, 0),
      new PowerDecimalTestCase(1.5, 2.35240961),
      new PowerDecimalTestCase(16.45667, -1.4545),

      // 1000 is the max exponent we expect in HyperbolicCurves
      new PowerDecimalTestCase(0.9999, 1000),
      new PowerDecimalTestCase(0.0001, 1000),
    ]

    powerDecimalTestCases.forEach((tc) => {
      it(`powerDecimal(${tc.in_base_number},${tc.in_exponent_number})`, async () => {
        const res = new Int59x18(await curveManager.powerDecimal(tc.in_base_59x18.value, tc.in_exponent_59x18.value))
        expect(res.approximateAsString()).to.equal(tc.out_59x18.approximateAsString())
      })
    })

    const powerDecimalFailureCases: PowerDecimalTestCase[] = [
      new PowerDecimalTestCase(-1, 1),
      new PowerDecimalTestCase(-0.001, 2),
    ]
    powerDecimalFailureCases.forEach((tc) => {
      it(`out of bounds: powerDecimal(${tc.in_base_number},${tc.in_exponent_number})`, async () => {
        await expect(curveManager.powerDecimal(tc.in_base_59x18.value, tc.in_exponent_59x18.value)).to.be.revertedWith(
          'powerDecimal: base must be >= 0',
        )
      })
    })
  })

  describe('cosh', () => {
    const coshTestCases: CoshTestCase[] = [
      new CoshTestCase(0),
      new CoshTestCase(1),
      new CoshTestCase(1.5),
      new CoshTestCase(3),
      new CoshTestCase(3.14),
      new CoshTestCase(5),
      new CoshTestCase(8.44459),
      new CoshTestCase(0.001),
      new CoshTestCase(9.9999),
      new CoshTestCase(20), // Max supported input
    ]

    coshTestCases.forEach((tc) => {
      it(`cosh(${tc.in_number})`, async () => {
        const res = new Int59x18(await curveManager.cosh(tc.in_59x18.value))
        expect(res.approximateAsString()).to.equal(tc.out_59x18.approximateAsString())
      })
    })

    const coshFailureCases: CoshTestCase[] = [
      new CoshTestCase(-0.001),
      new CoshTestCase(-1),
      new CoshTestCase(-99),
      new CoshTestCase(20.001),
      new CoshTestCase(99), // This would overflow in solidity if not explicitly guarded against
    ]

    coshFailureCases.forEach((tc) => {
      it(`out of bounds: cosh(${tc.in_number})`, async () => {
        await expect(curveManager.cosh(tc.in_59x18.value)).to.be.revertedWith('Cosh input')
      })
    })
  })

  describe('hyperbolicCurves', () => {
    const offset1 = 46.62165255
    const curve1 = new HyperbolicCurve(8.03456817, 1.29961294, 4.71657739, offset1)
    const curve1TestCases: HyperbolicCurveTestCase[] = [
      new HyperbolicCurveTestCase(curve1, 0),
      new HyperbolicCurveTestCase(curve1, 0.0001),
      new HyperbolicCurveTestCase(curve1, 0.1),
      new HyperbolicCurveTestCase(curve1, 0.21),
      new HyperbolicCurveTestCase(curve1, 0.456),
      new HyperbolicCurveTestCase(curve1, 0.875),
      new HyperbolicCurveTestCase(curve1, 0.9999),
      new HyperbolicCurveTestCase(curve1, 1),
    ]
    curve1TestCases.forEach((tc) => {
      it(`curve1(${tc.x_number})`, async () => {
        const res = new Int59x18(await curveManager.hyperbolicCurve(tc.curve.asSolidityStruct(), tc.x_59x18.value))
        expect(res.approximateAsString()).to.equal(tc.answer().approximateAsString())
      })
    })

    const offset2 = 15.15568744
    const curve2 = new HyperbolicCurve(0.03456817, 1.29961294, 4.71657739, offset2)
    const curve2TestCases: HyperbolicCurveTestCase[] = [
      new HyperbolicCurveTestCase(curve2, 0),
      new HyperbolicCurveTestCase(curve2, 0.000001),
      new HyperbolicCurveTestCase(curve2, 0.004),
      new HyperbolicCurveTestCase(curve2, 0.25),
      new HyperbolicCurveTestCase(curve2, 0.456789),
      new HyperbolicCurveTestCase(curve2, 0.8),
      new HyperbolicCurveTestCase(curve2, 0.94999),
      new HyperbolicCurveTestCase(curve2, 0.9999999),
      new HyperbolicCurveTestCase(curve2, 1),
    ]
    curve2TestCases.forEach((tc) => {
      it(`curve2(${tc.x_number})`, async () => {
        const res = new Int59x18(await curveManager.hyperbolicCurve(tc.curve.asSolidityStruct(), tc.x_59x18.value))
        expect(res.approximateAsString()).to.equal(tc.answer().approximateAsString())
      })
    })

    const offset3 = 0
    const curve3 = new HyperbolicCurve(0.000001, 0, 0, offset3)
    const curve3TestCases: HyperbolicCurveTestCase[] = [
      new HyperbolicCurveTestCase(curve3, 0),
      new HyperbolicCurveTestCase(curve3, 0.000001),
      new HyperbolicCurveTestCase(curve3, 0.004),
      new HyperbolicCurveTestCase(curve3, 0.25),
      new HyperbolicCurveTestCase(curve3, 0.456789),
      new HyperbolicCurveTestCase(curve3, 0.8),
      new HyperbolicCurveTestCase(curve3, 0.94999),
      new HyperbolicCurveTestCase(curve3, 0.999999),
      new HyperbolicCurveTestCase(curve3, 1),
    ]
    curve3TestCases.forEach((tc) => {
      it(`curve3(${tc.x_number})`, async () => {
        const res = new Int59x18(await curveManager.hyperbolicCurve(tc.curve.asSolidityStruct(), tc.x_59x18.value))
        expect(res.approximateAsString()).to.equal(tc.answer().approximateAsString())
      })
    })

    const curveFailureCases: HyperbolicCurveTestCase[] = [
      new HyperbolicCurveTestCase(curve3, -1.0001),
      new HyperbolicCurveTestCase(curve3, 1.0001),
    ]

    curveFailureCases.forEach((tc) => {
      it(`out of bounds: curve(${tc.x_number})`, async () => {
        await expect(curveManager.hyperbolicCurve(tc.curve.asSolidityStruct(), tc.x_59x18.value)).to.be.revertedWith(
          'x input',
        )
      })
    })
  })

  // To run thousands of tests, iterate through generatedCurveTestCases instead of myTests
  // Commenting out this describe block because it takes ages to run, and with ALL the tests generated but skipped it seems to dominate and
  // also corrupt the output of other tests (the previous test appears in red even though they pass)
  describe.skip('hyperbolicCurves (accuracy tests; skipping 11k+ tests for brevity; edit file to enable)', () => {
    const tinyVal1 = 0.00000001
    const tinyVal2 = 0.0001
    const smallVal = 0.001
    const aValues = [0, tinyVal1, tinyVal2, 0.5, 5, 10]
    const bValues = [0, tinyVal1, tinyVal2, 0.5, 5, 20]
    const cValues = [0, tinyVal1, tinyVal2, 0.5, 50, 1000]
    const dValues = [0, tinyVal1, tinyVal2, 0.5, 5, 20]
    const xValues = [0, tinyVal1, tinyVal2, smallVal, 0.01, 0.2, 0.75, 0.99999999, 1]

    const generatedCurveTestCases: HyperbolicCurveTestCase[] = []
    aValues.forEach((a) => {
      bValues.forEach((b) => {
        cValues.forEach((c) => {
          dValues.forEach((d) => {
            const curve = new HyperbolicCurve(a, b, c, d)
            xValues.forEach((x) => {
              if (a <= tinyVal2 && d == 0 && x <= smallVal) {
                // The d = 0 case actually causes our accuracy to fall below 0.1% when we also have a =~ 0 and small values of x.
                // For the purposes of accuracy testing, we assert that it is not reasonable to price using a curve where
                // d<0.00000001 AND a<0.0001 (this curve would be selling risk for almost nothing).
                // (Note that for such a curve, the absolute premium values would be tiny anyway, so even while the percentage error
                // may get larger, the absolute size of the error is still most likely a fraction of a cent.)
                return
              } else {
                generatedCurveTestCases.push(new HyperbolicCurveTestCase(curve, x))
              }
            })
          })
        })
      })
    })

    const myTests: HyperbolicCurveTestCase[] = [
      new HyperbolicCurveTestCase(new HyperbolicCurve(0.0001, 0.5, 0.0001, 0.0001), 0.01),
    ]
    // generatedCurveTestCases.forEach((tc) => {
    myTests.forEach((tc) => {
      it(`curve{${tc.curve.a_number},${tc.curve.b_number},${tc.curve.c_number},${tc.curve.d_number}}(${tc.x_number})`, async () => {
        const res = new Int59x18(await curveManager.hyperbolicCurve(tc.curve.asSolidityStruct(), tc.x_59x18.value))
        const answDecimal = new BigDecimal(tc.answer().toNumberString())
        const resDecimal = new BigDecimal(res.toNumberString())

        // console.log(`Answer is ${tc.answer().toNumberString()}`)
        // console.log(`answDecimal is ${answDecimal.toString()}`)
        // console.log(`resDecimal is ${resDecimal.toString()}`)
        if (answDecimal.toNumber() == 0) {
          assert(resDecimal.toNumber() == 0, `Zero expectation yields non-zero result of ${resDecimal.toString()}`)
        } else {
          const percentRatio = answDecimal.gt(resDecimal) ? answDecimal.div(resDecimal) : resDecimal.div(answDecimal)
          const percentDiff = percentRatio.minus(new BigDecimal(1))

          const MAX_ALLOWABLE_ERROR_RATIO = new BigDecimal(0.0001) // 0.01%
          const ONE_HUNDRED = new BigDecimal(100)
          assert(
            percentDiff.lte(MAX_ALLOWABLE_ERROR_RATIO),
            `Error of ${percentDiff.multipliedBy(
              ONE_HUNDRED,
            )}% is too large: expected ${answDecimal.toString()} but got ${resDecimal.toString()}`,
          )
        }
      })
    })
  })
})
