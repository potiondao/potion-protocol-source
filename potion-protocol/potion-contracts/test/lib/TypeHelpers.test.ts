import { expect } from 'chai'
import { CurveCriteria, OrderedCriteria } from '../../scripts/lib/typeHelpers'

describe('OrderedCriteria tests', () => {
  it('gets an ordered criteria', () => {
    const mockUnderlyingTokenAddress = '0x1122334455667788990011223344556677889900'
    const mockStrikeTokenAddress = '0x0000111122223333444455556666777788889999'

    const criteria_30days_100pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 100, 30)
    const criteria_10days_110pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 110, 10)
    const criteria_60days_80pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 80, 60)

    const criterias = [criteria_10days_110pct, criteria_30days_100pct, criteria_60days_80pct]

    const orderedCriteria = OrderedCriteria.from(criterias)

    // calculate values to assert
    const hashes = [
      criteria_30days_100pct.toKeccak256(),
      criteria_60days_80pct.toKeccak256(),
      criteria_10days_110pct.toKeccak256(),
    ]
    const sortedHashes = [...hashes].sort()

    expect(orderedCriteria[0].toKeccak256()).to.equal(sortedHashes[0])
    expect(orderedCriteria[1].toKeccak256()).to.equal(sortedHashes[1])
    expect(orderedCriteria[2].toKeccak256()).to.equal(sortedHashes[2])
  })
})
