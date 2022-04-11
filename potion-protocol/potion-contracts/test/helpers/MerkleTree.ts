import { bufferToHex, keccakFromString, keccak256 } from 'ethereumjs-util'

export default class MerkleTree {
  private readonly elements: Buffer[]
  private readonly layers: Buffer[][]

  // Assume all buffers have already been hashed, but hashes strings for use as leaves
  constructor(elements: Buffer[] | string[]) {
    if (Buffer.isBuffer(elements[0])) {
      this.elements = elements as Buffer[]
    } else {
      // Assume all
      this.elements = (elements as string[]).map((el) => keccakFromString(el))
    }

    // console.log("this.elements:", JSON.stringify(this.elements))

    // Sort elements
    this.elements.sort(Buffer.compare)
    // Deduplicate elements
    this.elements = MerkleTree.bufDedup(this.elements)

    // Create layers
    this.layers = this.getLayers(this.elements)
  }

  bufIndexOf(el: Buffer, arr: Buffer[]): number {
    let hash

    // Convert element to 32 byte hash if it is not one already
    if (el.length !== 32 || !Buffer.isBuffer(el)) {
      hash = keccak256(el)
    } else {
      hash = el
    }

    for (let i = 0; i < arr.length; i++) {
      if (hash.equals(arr[i])) {
        return i
      }
    }

    return -1
  }

  getLayers(elements: Buffer[]): Buffer[][] {
    if (elements.length === 0) {
      throw new Error('empty tree')
    }

    const layers = []
    layers.push(elements)

    // Get next layer until we reach the root
    while (layers[layers.length - 1].length > 1) {
      layers.push(this.getNextLayer(layers[layers.length - 1]))
    }

    return layers
  }

  getNextLayer(elements: Buffer[]): Buffer[] {
    return elements.reduce<Buffer[]>((layer, el, idx, arr) => {
      if (idx % 2 === 0) {
        // Hash the current element with its pair element
        layer.push(MerkleTree.combinedHash(el, arr[idx + 1]))
      }

      return layer
    }, [])
  }

  static combinedHash(first: Buffer, second: Buffer): Buffer {
    if (!first) {
      return second
    }
    if (!second) {
      return first
    }

    return keccak256(MerkleTree.sortAndConcat(first, second))
  }

  getRoot(): Buffer {
    // console.log("this.layers:", JSON.stringify(this.layers))
    return this.layers[this.layers.length - 1][0]
  }

  getHexRoot(): string {
    return bufferToHex(this.getRoot())
  }

  getProof(el: Buffer): Buffer[] {
    let idx = this.bufIndexOf(el, this.elements)

    if (typeof idx !== 'number') {
      throw new Error('Element does not exist in Merkle tree')
    }

    return this.layers.reduce((proof, layer) => {
      const pairElement = MerkleTree.getPairElement(idx, layer)

      if (pairElement) {
        proof.push(pairElement)
      }

      idx = Math.floor(idx / 2)

      return proof
    }, [])
  }

  // If Buffer, assume already hashed
  getHexProof(el: Buffer | string): string[] {
    if (typeof el === 'string') {
      el = keccakFromString(el)
    }
    const proof = this.getProof(el)

    return MerkleTree.bufArrToHexArr(proof)
  }

  private static getPairElement(idx: number, layer: Buffer[]): Buffer | null {
    const pairIdx = idx % 2 === 0 ? idx + 1 : idx - 1

    if (pairIdx < layer.length) {
      return layer[pairIdx]
    } else {
      return null
    }
  }

  private static bufDedup(elements: Buffer[]): Buffer[] {
    return elements.filter((el, idx) => {
      return idx === 0 || !elements[idx - 1].equals(el)
    })
  }

  private static bufArrToHexArr(arr: Buffer[]): string[] {
    if (arr.some((el) => !Buffer.isBuffer(el))) {
      throw new Error('Array is not an array of buffers')
    }

    return arr.map((el) => '0x' + el.toString('hex'))
  }

  private static sortAndConcat(...args: Buffer[]): Buffer {
    return Buffer.concat([...args].sort(Buffer.compare))
  }
}
