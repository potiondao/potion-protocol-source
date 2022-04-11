import { utils } from 'ethers'
import { diffArrays } from 'diff'

import fs from 'fs'
const fsPromises = fs.promises

// Represents a tumple of contracts:
// - The first contract is one deployed by Opyn and accessible to us on mainnet and kovan
// - The second is some interface purporting to represent (some subset of) the first contract
class ComparableContracts {
  static async loadAndFilterAbi(contractName: string): Promise<string[]> {
    try {
      const abiLocation = `${__dirname}/../abis/${contractName}.json`
      const abiString = await fsPromises.readFile(abiLocation)
      const parsedAbi = new utils.Interface(abiString.toString())
      const abiEntries = parsedAbi.format(utils.FormatTypes.minimal)
      return abiEntries as string[]
    } catch (err) {
      throw new Error(`No valid ABI found for contract '${contractName}'`)
    }
  }

  async loadAndFilterAbis() {
    this.opynAbi = await ComparableContracts.loadAndFilterAbi(this.opynContractName)
    this.ourInterfaceAbi = await ComparableContracts.loadAndFilterAbi(this.ourInterfaceName)
    this.loaded = true
  }

  // Compares the ABIs of the two contracts
  async getDiff() {
    if (!this.loaded) {
      await this.loadAndFilterAbis()
    }

    const diff = diffArrays(this.opynAbi as string[], this.ourInterfaceAbi as string[])
    return diff
  }

  public opynAbi: string[]
  public ourInterfaceAbi: string[]
  public loaded: boolean
  constructor(public opynContractName: string, public ourInterfaceName: string) {
    this.loaded = false
    this.opynAbi = []
    this.ourInterfaceAbi = []
  }
}

const validSubsetOfAbi: ComparableContracts[] = [
  new ComparableContracts('Whitelist', 'WhitelistInterface'),
  new ComparableContracts('Controller', 'ControllerInterface'),
  new ComparableContracts('AddressBook', 'AddressBookInterface'),
  new ComparableContracts('MarginCalculator', 'MarginCalculatorInterface'),
  new ComparableContracts('Oracle', 'OracleInterface'),
  new ComparableContracts('Otoken', 'OtokenInterface'),
  new ComparableContracts('OtokenFactory', 'OtokenFactoryInterface'),
]

// Interates through the contract relationships defined above, checking that the interface is a subset of the contract
// If it is not, info is printed about the disparity and a non-zero value (the number of disparities) is returned
async function main() {
  let errorCount = 0
  for (const pair of validSubsetOfAbi) {
    // console.log(`Comparing ${pair.opynContractName} with ${pair.ourInterfaceName}`)
    const diff = await pair.getDiff()
    let missingFunctions: string[] = []
    let extraFunctions: string[] = []

    diff.forEach((part) => {
      // green for additions, red for deletions
      // grey for common parts
      if (part.added) {
        // console.log('\x1b[32m%s\x1b[0m', part.value.join('\n')) // Green
        missingFunctions = missingFunctions.concat(part.value)
      } else if (part.removed) {
        // console.log('\x1b[31m%s\x1b[0m', part.value.join('\n')) // Red
        extraFunctions = extraFunctions.concat(part.value)
      } else {
        // console.log(part.value.join('\n'))
      }
    })

    if (missingFunctions.length > 0) {
      errorCount += missingFunctions.length
      console.log(`Contained in ${pair.ourInterfaceName} but missing from ${pair.opynContractName}:`)
      console.log('\x1b[31m%s\x1b[0m', ` - ${missingFunctions.sort().join(`\n - `)}`)
      console.log(`(Vice versa:\n - ${extraFunctions.join(`\n - `)}`)
    } else {
      console.log(
        '\x1b[32m%s\x1b[0m', // Red
        `Everything in ${pair.ourInterfaceName} is present in ${pair.opynContractName} (vice versa not checked)`,
      )
    }
  }

  return errorCount
}

// Return code is the number of problems found (0 => success)
main()
  .then((errorCount) => process.exit(errorCount))
  .catch((error) => {
    console.error(error)
    process.exit(1)
  })
