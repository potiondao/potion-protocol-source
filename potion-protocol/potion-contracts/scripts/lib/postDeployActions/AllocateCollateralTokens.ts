import { ethers } from 'hardhat'
import { BigNumber, Wallet } from 'ethers'
import { Deployment } from '../../../deploy/deploymentConfig'
import { AccountValue, PostDeployActionsResults } from '../postDeploy'
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import { commify, formatUnits } from 'ethers/lib/utils'

// Allocates tokens to the specified accounts, without any allowance

export class AllocateCollateralTokensFromFaucet {
  public constructor(public allocations: AccountValue[]) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    await allocateCollateralTokensFromFaucet(depl, this.allocations, '', printProgress)
  }
}

// Allocates tokens to the accounts in our wallet, and grants our contract a full allowance
export class AllocateCollateralTokensToWalletsFromFaucet {
  public constructor(public tokenCountForEachUser: BigNumber, public grantAllowanceToPotion = true) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    const allocations = (await ethers.getSigners()).map((w) => new AccountValue(w, this.tokenCountForEachUser))
    await allocateCollateralTokensFromFaucet(
      depl,
      allocations,
      this.grantAllowanceToPotion ? depl.potionLiquidityPoolAddress : undefined,
      printProgress,
    )
  }
}

// Allocates funds to the provided addresses, and optionally approves a contract to spend these funds
async function allocateCollateralTokensFromFaucet(
  depl: Deployment,
  recipients: AccountValue[],
  approveFullAllowanceToAddress?: string,
  printProgress = false,
): Promise<void> {
  // Mint some team balances
  printProgress &&
    console.log(
      `Pre-mining ${recipients.length} collateral token balances ${
        approveFullAllowanceToAddress
          ? `(granting allowance to contract ${approveFullAllowanceToAddress})`
          : '(no allowance granted)'
      }:`,
    )
  const token = await depl.faucetToken()
  const symbol = await token.symbol()
  const decimals = await token.decimals()

  for (const r of recipients) {
    let address
    if (r.account instanceof Wallet || r.account instanceof SignerWithAddress) {
      address = r.account.address
    } else {
      address = r.account
    }
    try {
      const trx = await token.allocateTo(address, r.value)
      await trx.wait()
    } catch (err) {
      // If allocate fails, we might be using a mintable token with an unguarded mint function
      const mintableToken = await depl.faucetTokenAsMock()
      const trx = await mintableToken.mint(address, r.value)
      await trx.wait()
    }
    if (approveFullAllowanceToAddress) {
      const approveTrx = await token.connect(r.account).approve(approveFullAllowanceToAddress, r.value)
      await approveTrx.wait() // Wait for mining to avoid duplicate nonces
    }
    printProgress && console.log(` - ${address} gets ${commify(formatUnits(r.value, decimals))} ${symbol}`)
  }
}
