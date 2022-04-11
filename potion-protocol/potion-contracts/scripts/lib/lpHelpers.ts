import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import type { Wallet } from 'ethers'
import { BigNumberish } from 'ethers'

export class DepositParams {
  constructor(
    public lp: Wallet | SignerWithAddress,
    public amount: BigNumberish,
    public poolId: BigNumberish,
    public curveHash: string,
    public criteriaSetHash: string,
  ) {}
}
