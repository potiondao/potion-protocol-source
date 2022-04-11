import { ethers } from 'hardhat'
import { expect } from 'chai'
import { CurveCriteria, CriteriaSet, OtokenPropertiesForValidation } from '../scripts/lib/typeHelpers'
import { utils } from 'ethers'

import { MockOtoken, CriteriaManager, MockAddressBook } from '../typechain/'
const unusedAddress = '0x0000000000000000000000000000000000000000'
const mockUnderlyingTokenAddress = '0x1122334455667788990011223344556677889900'
const mockStrikeTokenAddress = '0x0000111122223333444455556666777788889999'
const criteria_30days_100pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 100, 30)
const hash_30days_100pct = criteria_30days_100pct.toKeccak256()
const criteria_10days_110pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 110, 10)
const hash_10days_110pct = criteria_10days_110pct.toKeccak256()
const criteria_60days_80pct = new CurveCriteria(mockUnderlyingTokenAddress, mockStrikeTokenAddress, true, 80, 60)
const hash_60days_80pct = criteria_60days_80pct.toKeccak256()

describe('CriteriaManager', function () {
  let criteriaManager: CriteriaManager

  beforeEach('Deploy new CriteriaManager contact', async () => {
    const CriteriaManagerFactory = await ethers.getContractFactory('CriteriaManager')
    criteriaManager = (await CriteriaManagerFactory.deploy()) as CriteriaManager
  })

  it('add criteria', async () => {
    let known = await criteriaManager.registeredCriteria(hash_30days_100pct)
    expect(known, 'known before add').to.equal(false)
    const hash = await criteriaManager.hashCriteria(criteria_30days_100pct)
    expect(hash, 'hash').to.equal(hash_30days_100pct)
    await expect(criteriaManager.addCriteria(criteria_30days_100pct), 'addCriteria')
      .to.emit(criteriaManager, 'CriteriaAdded')
      .withArgs(hash_30days_100pct, criteria_30days_100pct.toArray())
    known = await criteriaManager.registeredCriteria(hash_30days_100pct)
    expect(known, 'known after add').to.equal(true)
  })

  it('add second criteria', async () => {
    await criteriaManager.addCriteria(criteria_30days_100pct)

    let known = await criteriaManager.registeredCriteria(hash_60days_80pct)
    expect(known, 'known before add').to.equal(false)
    const hash = await criteriaManager.hashCriteria(criteria_60days_80pct)
    expect(hash, 'hash').to.equal(hash_60days_80pct)
    await expect(criteriaManager.addCriteria(criteria_60days_80pct), 'addCriteria')
      .to.emit(criteriaManager, 'CriteriaAdded')
      .withArgs(hash_60days_80pct, criteria_60days_80pct.toArray())
    known = await criteriaManager.registeredCriteria(hash_60days_80pct)
    expect(known, 'known after add').to.equal(true)
  })

  it('add duplicate criteria', async () => {
    await criteriaManager.addCriteria(criteria_30days_100pct)

    const trx = await criteriaManager.addCriteria(criteria_30days_100pct)
    const rcpt = await trx.wait()
    expect(rcpt.logs.length, 'no logs because no change').to.equal(0)
    const known = await criteriaManager.registeredCriteria(hash_30days_100pct)
    expect(known, 'known after second add').to.equal(true)
  })

  it('hash hashes', async () => {
    const unsortedInput = [hash_10days_110pct, hash_60days_80pct, hash_30days_100pct]
    const setOfHashes = new CriteriaSet(unsortedInput)
    await expect(criteriaManager.hashOfSortedHashes(unsortedInput)).to.be.revertedWith('Input hashes not sorted')
    const hashOfHashes = await criteriaManager.hashOfSortedHashes(setOfHashes.toArray())

    expect(hashOfHashes).to.equal(setOfHashes.toKeccak256())
  })

  it('add criteria set', async () => {
    const set = new CriteriaSet([hash_30days_100pct, hash_60days_80pct])
    const hash = set.toKeccak256()

    await expect(criteriaManager.addCriteria(criteria_30days_100pct), 'addCriteria')
      .to.emit(criteriaManager, 'CriteriaAdded')
      .withArgs(hash_30days_100pct, criteria_30days_100pct.toArray())
    await expect(criteriaManager.addCriteria(criteria_60days_80pct), 'addCriteria')
      .to.emit(criteriaManager, 'CriteriaAdded')
      .withArgs(hash_60days_80pct, criteria_60days_80pct.toArray())
    let known = await criteriaManager.isCriteriaSetHash(hash)
    expect(known, 'known before add').to.equal(false)

    await expect(criteriaManager.addCriteriaSet(set.toArray()), 'addCriteriaSet')
      .to.emit(criteriaManager, 'CriteriaSetAdded')
      .withArgs(hash, set.toArray())
    known = await criteriaManager.isCriteriaSetHash(hash)
    expect(known, 'known after add').to.equal(true)
  })

  it('add second criteria set', async () => {
    // We do not currently check for duplicates, so this is allowed and results in a second criteria set
    await criteriaManager.addCriteria(criteria_30days_100pct)
    await criteriaManager.addCriteria(criteria_60days_80pct)
    await criteriaManager.addCriteria(criteria_10days_110pct)
    const set1 = new CriteriaSet([hash_30days_100pct, hash_60days_80pct])
    const hash1 = set1.toKeccak256()
    await expect(criteriaManager.addCriteriaSet(set1.toArray()), 'addCriteriaSet')
      .to.emit(criteriaManager, 'CriteriaSetAdded')
      .withArgs(hash1, set1.toArray())
    const set2 = new CriteriaSet([hash_10days_110pct, hash_30days_100pct])
    const hash2 = set2.toKeccak256()
    let known = await criteriaManager.isCriteriaSetHash(hash2)
    expect(known, 'known before add').to.equal(false)
    await expect(criteriaManager.addCriteriaSet(set2.toArray()), 'addCriteriaSet')
      .to.emit(criteriaManager, 'CriteriaSetAdded')
      .withArgs(hash2, set2.toArray())
    known = await criteriaManager.isCriteriaSetHash(hash2)
    expect(known, 'known after add').to.equal(true)
  })

  it('add duplicate (re-ordered) criteria set', async () => {
    // We do not currently check for duplicates, so this is allowed and results in a second criteria set
    await criteriaManager.addCriteria(criteria_30days_100pct)
    await criteriaManager.addCriteria(criteria_60days_80pct)
    const setUnordered = [hash_60days_80pct, hash_30days_100pct]
    const hashUnordered = utils.solidityKeccak256(['bytes32[]'], [setUnordered])
    const setOrdered = [hash_30days_100pct, hash_60days_80pct]
    const hashOrdered = new CriteriaSet(setOrdered).toKeccak256()
    await expect(criteriaManager.addCriteriaSet(setOrdered), 'addCriteriaSet')
      .to.emit(criteriaManager, 'CriteriaSetAdded')
      .withArgs(hashOrdered, setOrdered)
    const knownBadHash = await criteriaManager.isCriteriaSetHash(hashUnordered)
    expect(knownBadHash, 'known hash of wrongly ordered array').to.equal(false)
    const knownGoodHash = await criteriaManager.isCriteriaSetHash(hashOrdered)
    expect(knownGoodHash, 'known before re-add').to.equal(true)
    const trx = await criteriaManager.addCriteriaSet(setOrdered)
    const rcpt = await trx.wait()
    expect(rcpt.logs.length, 'no logs beause no change').to.equal(0)
    const knownBadHash2 = await criteriaManager.isCriteriaSetHash(hashUnordered)
    expect(knownBadHash2, 'known hash of wrongly ordered array (2)').to.equal(false)
    const knownGoodHash2 = await criteriaManager.isCriteriaSetHash(hashOrdered)
    expect(knownGoodHash2, 'known after re-add').to.equal(true)
  })

  describe('with 3 criteria sets', function () {
    let validOtoken: MockOtoken
    let badUnderlyingOtoken: MockOtoken
    let badStrikeOtoken: MockOtoken
    let callOtoken: MockOtoken
    const set1 = new CriteriaSet([hash_30days_100pct, hash_60days_80pct])
    const setHash1 = set1.toKeccak256()
    const set2 = new CriteriaSet([hash_10days_110pct, hash_30days_100pct])
    const setHash2 = set2.toKeccak256()
    const set3 = new CriteriaSet([hash_60days_80pct, hash_10days_110pct])
    const setHash3 = set3.toKeccak256()

    before('deploy 3 mock otokens', async () => {
      const MockAddressBookFactory = await ethers.getContractFactory('MockAddressBook')
      const mockAddressBook = (await MockAddressBookFactory.deploy()) as MockAddressBook
      const MockOtokenFactory = await ethers.getContractFactory('MockOtoken')
      validOtoken = (await MockOtokenFactory.deploy()) as MockOtoken
      validOtoken.init(
        mockAddressBook.address,
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        unusedAddress,
        0,
        0,
        true,
      )
      badUnderlyingOtoken = (await MockOtokenFactory.deploy()) as MockOtoken
      badUnderlyingOtoken.init(
        mockAddressBook.address,
        mockStrikeTokenAddress,
        mockStrikeTokenAddress,
        unusedAddress,
        0,
        0,
        true,
      )
      badStrikeOtoken = (await MockOtokenFactory.deploy()) as MockOtoken
      badStrikeOtoken.init(
        mockAddressBook.address,
        mockUnderlyingTokenAddress,
        mockUnderlyingTokenAddress,
        unusedAddress,
        0,
        0,
        true,
      )
      callOtoken = (await MockOtokenFactory.deploy()) as MockOtoken
      callOtoken.init(
        mockAddressBook.address,
        mockUnderlyingTokenAddress,
        mockStrikeTokenAddress,
        unusedAddress,
        0,
        0,
        false,
      )
    })
    beforeEach('deploy 3 criteria sets', async () => {
      await criteriaManager.addCriteria(criteria_30days_100pct)
      await criteriaManager.addCriteria(criteria_60days_80pct)
      await criteriaManager.addCriteria(criteria_10days_110pct)
      await criteriaManager.addCriteriaSet(set1.toArray()) //  Set 1
      await criteriaManager.addCriteriaSet(set2.toArray()) // Set 2
      await criteriaManager.addCriteriaSet(set3.toArray()) //  Set 3
    })

    it('3 criteria lists exist', async () => {
      expect(await criteriaManager.isCriteriaSetHash(setHash1), '1').to.equal(true)
      expect(await criteriaManager.isCriteriaSetHash(setHash2), '2').to.equal(true)
      expect(await criteriaManager.isCriteriaSetHash(setHash3), '3').to.equal(true)
    })

    it('isInCriteriaSet', async () => {
      expect(await criteriaManager.isInCriteriaSet(setHash1, hash_30days_100pct), '1-1').to.equal(true)
      expect(await criteriaManager.isInCriteriaSet(setHash2, hash_30days_100pct), '1-2').to.equal(true)
      expect(await criteriaManager.isInCriteriaSet(setHash3, hash_30days_100pct), '1-3').to.equal(false)

      expect(await criteriaManager.isInCriteriaSet(setHash1, hash_60days_80pct), '2-1').to.equal(true)
      expect(await criteriaManager.isInCriteriaSet(setHash2, hash_60days_80pct), '2-2').to.equal(false)
      expect(await criteriaManager.isInCriteriaSet(setHash3, hash_60days_80pct), '2-3').to.equal(true)

      expect(await criteriaManager.isInCriteriaSet(setHash1, hash_10days_110pct), '3-1').to.equal(false)
      expect(await criteriaManager.isInCriteriaSet(setHash2, hash_10days_110pct), '3-2').to.equal(true)
      expect(await criteriaManager.isInCriteriaSet(setHash3, hash_10days_110pct), '3-3').to.equal(true)
    })

    it('valid criteria', async () => {
      await criteriaManager.requireOtokenMeetsCriteria(
        criteria_30days_100pct,
        await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 100, 30),
      )
      await criteriaManager.requireOtokenMeetsCriteria(
        criteria_30days_100pct,
        await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 99, 30),
      )
      await criteriaManager.requireOtokenMeetsCriteria(
        criteria_30days_100pct,
        await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 100, 29),
      )
      await criteriaManager.requireOtokenMeetsCriteria(
        criteria_30days_100pct,
        await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 99, 29),
      )
      await criteriaManager.requireOtokenMeetsCriteria(
        criteria_30days_100pct,
        await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 1, 1),
      )
    })

    it('invalid criteria', async () => {
      await expect(
        criteriaManager.requireOtokenMeetsCriteria(
          criteria_30days_100pct,
          await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 101, 30),
        ),
      ).to.be.revertedWith('invalid strike%')
      await expect(
        criteriaManager.requireOtokenMeetsCriteria(
          criteria_30days_100pct,
          await OtokenPropertiesForValidation.fromOtokenAssets(validOtoken, 100, 31),
        ),
      ).to.be.revertedWith('invalid duration')
      await expect(
        criteriaManager.requireOtokenMeetsCriteria(
          criteria_30days_100pct,
          await OtokenPropertiesForValidation.fromOtokenAssets(badUnderlyingOtoken, 100, 30),
        ),
      ).to.be.revertedWith('wrong underlying token')
      await expect(
        criteriaManager.requireOtokenMeetsCriteria(
          criteria_30days_100pct,
          await OtokenPropertiesForValidation.fromOtokenAssets(badStrikeOtoken, 100, 30),
        ),
      ).to.be.revertedWith('wrong strike token')
      await expect(
        criteriaManager.requireOtokenMeetsCriteria(
          criteria_30days_100pct,
          await OtokenPropertiesForValidation.fromOtokenAssets(callOtoken, 100, 30),
        ),
      ).to.be.revertedWith('call options not supported')
    })
  })
})
