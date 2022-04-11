import { ethers } from 'hardhat'
import { Deployment } from '../../../deploy/deploymentConfig'
import { PostDeployAction, PostDeployActionsResults } from '../postDeploy'

export class FastForwardDays implements PostDeployAction {
  public fastForwardSeconds: number

  public constructor(fastForwardDays: number) {
    this.fastForwardSeconds = fastForwardDays * 60 * 60 * 24
  }

  public setNumberOfSeconds(s: number): void {
    this.fastForwardSeconds = s
  }

  // Advance a local blockchain 1 block and `fastForwardSeconds` seconds of time
  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    printProgress &&
      console.log(`Fast forwarding ${this.fastForwardSeconds / 86400} days (${this.fastForwardSeconds} seconds)`)
    await ethers.provider.send('evm_increaseTime', [this.fastForwardSeconds])
    await ethers.provider.send('evm_mine', []) // mine the next block
  }
}

export class FastForwardPastNextActiveOtokenExpiry implements PostDeployAction {
  // Advance a local blockchain 1 block and `fastForwardSeconds` seconds of time
  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<void> {
    const now = (await ethers.provider.getBlock('latest')).timestamp
    const otokens = await dataAlreadyDeployed.unsettledOtokensExpiringBefore()
    const activeOtokenExpiryTimestamps = otokens.filter((o) => o.contributors.length > 0).map((o) => o.expiry)
    const nextTimestamp = Math.min(...activeOtokenExpiryTimestamps)
    const delta = nextTimestamp - now
    if (delta > 0) {
      printProgress && console.log(`Fast forwarding to next otoken expiry: ${delta / 86400} days (${delta} seconds)`)
      await ethers.provider.send('evm_increaseTime', [delta + 1]) // We go past it by at least 1 second
      await ethers.provider.send('evm_mine', []) // mine the next block
    }
  }
}
