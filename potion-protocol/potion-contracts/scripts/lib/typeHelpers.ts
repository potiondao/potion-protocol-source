import { BigNumber, BigNumberish, utils } from 'ethers'
import { Int59x18 } from './math59x18'
import { MockOtoken } from '../../typechain/'

function assert(input: boolean, message?: string): asserts input {
  if (!input) throw new Error(message ? message : 'assertion failed')
}

export interface CurveParamsAsBigNumbers {
  a_59x18: BigNumber
  b_59x18: BigNumber
  c_59x18: BigNumber
  d_59x18: BigNumber
  max_util_59x18: BigNumber
}

export class OtokenPropertiesForValidation {
  constructor(
    public percentStrikeValue: number,
    public wholeDaysRemaining: number,
    public underlyingAsset: string,
    public strikeAsset: string,
    public isPut = true,
  ) {}

  public static async fromOtokenAssets(
    otoken: MockOtoken,
    percentStrikeValue: number,
    wholeDaysRemaining: number,
  ): Promise<OtokenPropertiesForValidation> {
    return new OtokenPropertiesForValidation(
      percentStrikeValue,
      wholeDaysRemaining,
      await otoken.underlyingAsset(),
      await otoken.strikeAsset(),
      await otoken.isPut(),
    )
  }
}

export class HyperbolicCurve {
  public a_59x18: Int59x18
  public b_59x18: Int59x18
  public c_59x18: Int59x18
  public d_59x18: Int59x18
  public max_util_59x18: Int59x18

  public static registry = new Map<string, HyperbolicCurve>()

  constructor(
    public a_number: number,
    public b_number: number,
    public c_number: number,
    public d_number: number,
    public max_util: number = 1,
  ) {
    this.a_59x18 = Int59x18.fromDecimal(a_number)
    this.b_59x18 = Int59x18.fromDecimal(b_number)
    this.c_59x18 = Int59x18.fromDecimal(c_number)
    this.d_59x18 = Int59x18.fromDecimal(d_number)
    this.max_util_59x18 = Int59x18.fromDecimal(max_util) // by default assign to max util = 1 -> 100%
    // All curves are mapped by their hash for easy retrieval later
    HyperbolicCurve.registry.set(this.toKeccak256(), this)
  }

  // As specified in the CurveManager.sol
  static MAX_A = 10
  static MAX_B = 20
  static MAX_C = 1000
  static MAX_D = 20

  asSolidityStruct(): CurveParamsAsBigNumbers {
    return {
      a_59x18: this.a_59x18.value,
      b_59x18: this.b_59x18.value,
      c_59x18: this.c_59x18.value,
      d_59x18: this.d_59x18.value,
      max_util_59x18: this.max_util_59x18.value,
    }
  }

  // Returned values and order must match the struct declaration in CriteriaManager.hashCriteria()
  toArray(): (string | boolean | BigNumberish)[] {
    const values = [
      this.a_59x18.value,
      this.b_59x18.value,
      this.c_59x18.value,
      this.d_59x18.value,
      this.max_util_59x18.value,
    ]

    // Check for an out of date solidityTypes()
    assert(values.length === HyperbolicCurve.solidityTypes().length, 'curve: # of solidity types != # of members')
    return values
  }

  static solidityTypes(): string[] {
    const types = ['int256', 'int256', 'int256', 'int256', 'int256']
    return types
  }

  toKeccak256(): string {
    return utils.solidityKeccak256(HyperbolicCurve.solidityTypes(), this.toArray())
  }

  evalAt(x: number): number {
    const coshPart = Math.cosh(this.b_number * Math.pow(x, this.c_number))
    return coshPart * this.a_number * x + this.d_number
  }
}

export class CurveCriteria {
  public static registry = new Map<string, CurveCriteria>()

  constructor(
    public underlyingAsset: string,
    public strikeAsset: string,
    public isPut: boolean,
    public maxStrikePercent: BigNumberish,
    public maxDurationInDays: BigNumberish,
  ) {
    CurveCriteria.registry.set(this.toKeccak256(), this)
  }

  // Returned values and order must match the struct declaration in CriteriaManager.hashCriteria()
  toArray(): (string | boolean | BigNumberish)[] {
    const values = [this.underlyingAsset, this.strikeAsset, this.isPut, this.maxStrikePercent, this.maxDurationInDays]

    // Check for an out of date solidityTypes()
    assert(values.length === CurveCriteria.solidityTypes().length, 'criteria: # of solidity types != # of members')
    return values
  }

  static solidityTypes(): string[] {
    const types = ['address', 'address', 'bool', 'uint256', 'uint256']
    return types
  }

  toKeccak256(): string {
    return utils.solidityKeccak256(CurveCriteria.solidityTypes(), this.toArray())
  }
}

export class CriteriaSet {
  public hashes: string[]
  public static registry = new Map<string, Set<CurveCriteria>>()

  constructor(unsortedHashes: string[]) {
    this.hashes = [...unsortedHashes].sort() // Taking care not to sort the input array, for easier testing
    const mySet = new Set<CurveCriteria>()

    for (const h of this.hashes) {
      mySet.add(CurveCriteria.registry.get(h) as CurveCriteria)
    }
    CriteriaSet.registry.set(this.toKeccak256(), mySet)
  }

  toArray(): string[] {
    return this.hashes
  }

  static solidityTypes(): string[] {
    return ['bytes32[]']
  }

  toKeccak256(): string {
    return utils.solidityKeccak256(CriteriaSet.solidityTypes(), [this.toArray()])
  }
}

export class OrderedCriteria {
  static from(criterias: CurveCriteria[]): CurveCriteria[] {
    const orderedCriterias: CurveCriteria[] = []
    const criteriaHashesMap = new Map<string, CurveCriteria>()
    criterias.forEach((item) => {
      criteriaHashesMap.set(item.toKeccak256(), item)
    })

    const allHashes = Array.from(criteriaHashesMap.keys())
    const sortedHashes = [...allHashes].sort()

    for (const hash of sortedHashes) {
      const criteriaItem = criteriaHashesMap.get(hash)
      if (!criteriaItem) {
        throw new Error('Invalid criteria hash')
      }
      orderedCriterias.push(criteriaItem)
    }
    return orderedCriterias
  }
}
