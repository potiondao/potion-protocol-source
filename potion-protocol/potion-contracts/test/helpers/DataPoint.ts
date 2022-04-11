import { utils } from 'ethers'
import type { BytesLike, BigNumberish } from 'ethers'

function assert(input: boolean, message?: string): asserts input {
  if (!input) throw new Error(message ? message : 'assertion failed')
}

// This is a typescript representation of the struct in the MerkleProofDataPoints contract
// The member variables, and the ordering of toArray() and solidityTypes(), MUST MATCH each other and the MerkleProofDataPoints contract
export class DataPoint {
  constructor(
    public assetIdentifier: BytesLike,
    public durationInDays: BigNumberish,
    public strikePriceInDai: BigNumberish,
    public priorUtilisationNumerator: BigNumberish,
    public orderSize: BigNumberish,
    public premium: BigNumberish,
  ) {}

  toString(): string {
    const buffer: string[] = []
    const values = this.toArray()
    const types = DataPoint.solidityTypes()
    for (let i = 0; i < types.length; i++) {
      buffer.push(`${values[i]}[${types[i]}]`)
    }
    return `DataPoint:<${buffer.join()}>`
  }

  // Returned values and order must match the struct declaration in MerkleProofDataPoints.sol
  private toArray(): (BytesLike | BigNumberish)[] {
    const values = [
      this.assetIdentifier,
      this.durationInDays,
      this.strikePriceInDai,
      this.priorUtilisationNumerator,
      this.orderSize,
      this.premium,
    ]

    // Check for an out of date solidityTypes()
    assert(values.length === DataPoint.solidityTypes().length, '# of solidity types != # of members')
    return values
  }

  toKeccak256(): string {
    return utils.solidityKeccak256(DataPoint.solidityTypes(), this.toArray())
  }

  toKeccak256Buffer(): Buffer {
    const hashAsUint8s = utils.arrayify(this.toKeccak256())
    return Buffer.from(hashAsUint8s)
  }

  // Returned types and order must match those in the struct declaration in MerkleProofDataPoints.sol
  static solidityTypes(): string[] {
    const types = ['bytes32', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256']
    return types
  }
}
