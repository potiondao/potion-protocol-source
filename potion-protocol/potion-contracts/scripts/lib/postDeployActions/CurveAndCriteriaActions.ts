import { Deployment } from '../../../deploy/deploymentConfig'
import { CriteriaManager, CurveManager } from '../../../typechain'
import { CriteriaSet, CurveCriteria, HyperbolicCurve } from '../typeHelpers'
import {
  PostDeployAction,
  PostDeployActionResult,
  CurveGenerator,
  CriteriaGenerator,
  PostDeployActionsResults,
  CriteriaAndCriteriaSets,
} from '../postDeploy'

export const generateOneCurve: CurveGenerator = () => {
  return [new HyperbolicCurve(0.004681221242539369, 1.5952508937241, 7.056354222158904, 0.015587766897271952)]
}

export const generateTwoCurves: CurveGenerator = () => {
  return [new HyperbolicCurve(8.03456817, 1.29961294, 4.71657739, 16.62165255), new HyperbolicCurve(5, 1.5, 4, 12)]
}

export const generateOneCriteriaAndOneCriteriaSet: CriteriaGenerator = (wethAddress, usdcAddress) => {
  const criteria = [new CurveCriteria(wethAddress, usdcAddress, true, 90, 5)]
  const criteriaSets = [
    new CriteriaSet([criteria[0].toKeccak256()]), // Only first criteria above
  ]
  return {
    criteria: criteria,
    criteriaSets: criteriaSets,
  }
}

export const generateTwoCriteriaAndTwoCriteriaSets: CriteriaGenerator = (wethAddress, usdcAddress) => {
  const criteria = [
    new CurveCriteria(wethAddress, usdcAddress, true, 120, 365), // WETH PUT, max 120% strike & max 1 year duration
    new CurveCriteria(wethAddress, usdcAddress, true, 100, 30),
  ]
  const criteriaSets = [
    new CriteriaSet([criteria[0].toKeccak256()]), // Only first criteria above
    new CriteriaSet([criteria[0].toKeccak256(), criteria[1].toKeccak256()]), // Both criteria above
  ]
  return {
    criteria: criteria,
    criteriaSets: criteriaSets,
  }
}

const deployCurves = async (cm: CurveManager, curves: HyperbolicCurve[]) => {
  for (const c of curves) {
    const trx = await cm.addCurve(c.asSolidityStruct())
    await trx.wait() // Wait for mining to avoid duplicate nonces
  }
}

const deployCriteriaAndSets = async (crm: CriteriaManager, data: CriteriaAndCriteriaSets) => {
  for (const c of data.criteria) {
    const trx = await crm.addCriteria(c)
    await trx.wait() // Wait for mining to avoid duplicate nonces
  }
  for (const c of data.criteriaSets) {
    const trx = await crm.addCriteriaSet(c.toArray())
    await trx.wait() // Wait for mining to avoid duplicate nonces
  }
}

export const deployDefaultCurves = async (cm: CurveManager): Promise<HyperbolicCurve[]> => {
  const curves = generateTwoCurves()
  await deployCurves(cm, curves)
  return curves
}

export const deployDefaultCriteria = async (
  crm: CriteriaManager,
  wethAddress: string,
  usdcAddress: string,
): Promise<CriteriaAndCriteriaSets> => {
  const data = generateTwoCriteriaAndTwoCriteriaSets(wethAddress, usdcAddress)
  await deployCriteriaAndSets(crm, data)
  return data
}

export class DeployCurves implements PostDeployAction {
  public constructor(public curveGenerator: CurveGenerator = generateTwoCurves) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult> {
    if (!depl.sampleUnderlyingTokenAddress) {
      throw new Error('Cannot deploy sample curves without sample underlying token address')
    }
    const cm = await depl.curveManager()
    const curves = this.curveGenerator()

    printProgress && process.stdout.write(`Deploying ${curves.length} curves... `)
    await deployCurves(cm, curves)
    printProgress && console.log(`Done.`)
    return curves
  }
}

export class DeployCriteriaAndCriteriaSets implements PostDeployAction {
  public constructor(public criteriaGenerator: CriteriaGenerator = generateTwoCriteriaAndTwoCriteriaSets) {}

  async executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult> {
    const addedObjects: PostDeployActionResult = []
    if (!depl.sampleUnderlyingTokenAddress) {
      throw new Error('Cannot deploy sample curves without sample underlying token address')
    }
    const crm = await depl.criteriaManager()
    const criteriaAndSets = this.criteriaGenerator(depl.sampleUnderlyingTokenAddress, depl.collateralTokenAddress)

    printProgress &&
      process.stdout.write(
        `Deploying ${criteriaAndSets.criteria.length} criteria, and ${criteriaAndSets.criteriaSets.length} criteria sets... `,
      )
    await deployCriteriaAndSets(crm, criteriaAndSets)
    printProgress && console.log(`Done.`)
    return addedObjects.concat(criteriaAndSets.criteria).concat(criteriaAndSets.criteriaSets)
  }
}
