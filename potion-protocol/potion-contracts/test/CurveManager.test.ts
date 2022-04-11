import { ethers } from 'hardhat'
import { expect } from 'chai'

import { HyperbolicCurve } from '../scripts/lib/typeHelpers'
import { CurveManager } from '../typechain/'

import { EMPTY_HASH } from './helpers/testSetup'

const offset1 = 16.62165255
const curve1 = new HyperbolicCurve(8.03456817, 1.29961294, 4.71657739, offset1)
const hash1 = curve1.toKeccak256()
const offset2 = 5.123
const curve2 = new HyperbolicCurve(6.03456817, 2, 0, offset2)
const hash2 = curve2.toKeccak256()
const offset3 = 5.123
const curve3 = new HyperbolicCurve(0, 2.35568, 6.00689, offset3)
const hash3 = curve3.toKeccak256()

describe('CurveManager', function () {
  let curveManager: CurveManager

  beforeEach('Deploy new CurveManager contract', async () => {
    const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
    curveManager = (await CurveManagerFactory.deploy()) as CurveManager
  })

  it('add curve', async () => {
    let known = await curveManager.isKnownCurveHash(hash1)
    expect(known, 'known before add').to.equal(false)
    const hash = await curveManager.hashCurve(curve1.asSolidityStruct())
    expect(hash, 'hash').to.equal(hash1)
    await expect(curveManager.addCurve(curve1.asSolidityStruct()), 'addCurve')
      .to.emit(curveManager, 'CurveAdded')
      .withArgs(hash1, curve1.toArray())
    known = await curveManager.isKnownCurveHash(hash1)
    expect(known, 'known after add').to.equal(true)
  })

  it('add second curve', async () => {
    await curveManager.addCurve(curve1.asSolidityStruct())

    let known = await curveManager.isKnownCurveHash(hash2)
    expect(known, 'known before add').to.equal(false)
    const hash = await curveManager.hashCurve(curve2.asSolidityStruct())
    expect(hash, 'hash').to.equal(hash2)
    await expect(curveManager.addCurve(curve2.asSolidityStruct()), 'addCurve')
      .to.emit(curveManager, 'CurveAdded')
      .withArgs(hash2, curve2.toArray())
    known = await curveManager.isKnownCurveHash(hash2)
    expect(known, 'known after add').to.equal(true)
  })

  it('add duplicate curve', async () => {
    await curveManager.addCurve(curve1.asSolidityStruct())

    const trx = await curveManager.addCurve(curve1.asSolidityStruct())
    const rcpt = await trx.wait()
    expect(rcpt.logs.length, 'no longs').to.equal(0)
    const known = await curveManager.isKnownCurveHash(hash1)
    expect(known, 'known after second add').to.equal(true)
  })

  describe('with 3 curves', function () {
    beforeEach('deploy 3 curves', async () => {
      await curveManager.addCurve(curve1.asSolidityStruct())
      await curveManager.addCurve(curve2.asSolidityStruct())
      await curveManager.addCurve(curve3.asSolidityStruct())
    })

    it('3 curves exist', async () => {
      expect(await curveManager.isKnownCurveHash(EMPTY_HASH), 'A').to.equal(false)
      expect(
        await curveManager.isKnownCurveHash('0x0df4419f707b143fe5e182b14e3885a3fa93121cfc4b18a5bade62455a0ff75b'),
        'B',
      ).to.equal(false)
      expect(await curveManager.isKnownCurveHash(hash1), '1').to.equal(true)
      expect(await curveManager.isKnownCurveHash(hash2), '2').to.equal(true)
      expect(await curveManager.isKnownCurveHash(hash3), '3').to.equal(true)
    })
  })

  const test = it

  describe('Invalid curves', () => {
    beforeEach('Deploy new CurveManager contract', async () => {
      const CurveManagerFactory = await ethers.getContractFactory('CurveManager')
      curveManager = (await CurveManagerFactory.deploy()) as CurveManager
    })

    test('[A] out of UPPER bound limit', async () => {
      const invalidValue = 10.001
      const curveToAdd = new HyperbolicCurve(invalidValue, 1, 1, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid A value')
    })

    test('[A] out of LOWER bound limit', async () => {
      const invalidValue = -0.001
      const curveToAdd = new HyperbolicCurve(invalidValue, 1, 1, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid A value')
    })

    test('[B] out of UPPER bound limit', async () => {
      const invalidValue = 20.0001
      const curveToAdd = new HyperbolicCurve(1, invalidValue, 1, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid B value')
    })

    test('[B] out of LOWER bound limit', async () => {
      const invalidValue = -0.001
      const curveToAdd = new HyperbolicCurve(1, invalidValue, 1, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid B value')
    })

    test('[C] out of UPPER bound limit', async () => {
      const invalidValue = 1000.0001
      const curveToAdd = new HyperbolicCurve(1, 1, invalidValue, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid C value')
    })

    test('[C] out of LOWER bound limit', async () => {
      const invalidValue = -0.001
      const curveToAdd = new HyperbolicCurve(1, 1, invalidValue, 1)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid C value')
    })

    test('[D] out of UPPER bound limit', async () => {
      const invalidValue = 20.00001
      const curveToAdd = new HyperbolicCurve(1, 1, 1, invalidValue)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid D value')
    })

    test('[D] out of LOWER bound limit', async () => {
      const invalidValue = -0.001
      const curveToAdd = new HyperbolicCurve(1, 1, 1, invalidValue)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid D value')
    })

    test('[MAX_UTIL] out of LOWER bound limit', async () => {
      const invalidValue = -0.1
      const curveToAdd = new HyperbolicCurve(1, 1, 1, 1, invalidValue)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid Max util value')
    })

    test('[MAX_UTIL] out of LOWER bound limit (0)', async () => {
      const invalidValue = 0
      const curveToAdd = new HyperbolicCurve(1, 1, 1, 1, invalidValue)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid Max util value')
    })

    test('[MAX_UTIL] out of UPPER bound limit', async () => {
      const invalidValue = 10
      const curveToAdd = new HyperbolicCurve(1, 1, 1, 1, invalidValue)

      await expect(curveManager.addCurve(curveToAdd.asSolidityStruct())).to.be.revertedWith('Invalid Max util value')
    })
  })
})
