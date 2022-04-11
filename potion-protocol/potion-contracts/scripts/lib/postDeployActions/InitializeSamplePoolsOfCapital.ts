import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'
import { commify, formatUnits } from 'ethers/lib/utils'
import { ethers } from 'hardhat'
import { Deployment } from '../../../deploy/deploymentConfig'
import { DepositParams } from '../lpHelpers'
import { CriteriaSet, HyperbolicCurve } from '../typeHelpers'
import { PostDeployAction, parseUsdcAmount, PostDeployActionsResults, PostDeployActionResult } from '../postDeploy'

type DepositGenerator = {
  (dataSoFar: PostDeployActionsResults): Promise<DepositParams[]>
}

// We select LPs from from the front of the list, so for a small number of LPs and buyers they will not overlap
export async function getLps(count?: number): Promise<SignerWithAddress[]> {
  const signers = await ethers.getSigners()
  count = count || signers.length
  if (count > signers.length) {
    throw Error(`${count} LPs requested but only ${signers.length} signers available`)
  }
  return signers.slice(0, count)
}

const generateDefaultDeposits: DepositGenerator = async (dataAlreadyDeployed) => {
  // TODO: refactor? consider using curve and criteria registries instead of params
  const lps = await getLps()
  const deposits: DepositParams[] = []
  const curves = dataAlreadyDeployed.allDataOfType(HyperbolicCurve)
  const criteriaSets = dataAlreadyDeployed.allDataOfType(CriteriaSet)
  for (let i = 0; i < lps.length; i++) {
    deposits.push(
      new DepositParams(
        lps[i],
        parseUsdcAmount((i + 1) * 20000),
        0,
        curves[i % curves.length].toKeccak256(),
        criteriaSets[i % criteriaSets.length].toKeccak256(),
      ),
    )
  }
  return deposits
}

// Iterates over  all curves & criteria from the stack, creating pools of capital corresponding to each one
export class InitializeSamplePoolsOfCapital implements PostDeployAction {
  public constructor(public despositGenerator: DepositGenerator = generateDefaultDeposits) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult> {
    const poolsOfCapital = await this.despositGenerator(dataAlreadyDeployed)
    printProgress && console.log(`Initializing ${poolsOfCapital.length} pools of LP capital:`)

    const token = await depl.faucetToken()
    const symbol = await token.symbol()
    const decimals = await token.decimals()
    const lpContract = await depl.potionLiquidityPool()

    for (const p of poolsOfCapital) {
      const trx = await lpContract
        .connect(p.lp)
        .depositAndConfigurePool(p.poolId, p.amount, p.curveHash, p.criteriaSetHash)
      await trx.wait() // Wait for mining to avoid duplicate nonces
      printProgress &&
        console.log(` - deposited ${commify(formatUnits(p.amount, decimals))} ${symbol} from LP ${p.lp.address}`)
    }
    printProgress && console.log(`LP deposits complete`)
    return poolsOfCapital
  }
}
