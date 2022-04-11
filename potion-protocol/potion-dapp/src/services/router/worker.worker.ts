import { ICriteria, IPoolUntyped } from "@/types";

import { getEmergingBondingCurvesFromCriterias as calculate } from "@/services/router/emergingBondingCurve";
import { runDepthRouter } from "@/services/router";

export async function getEmergingBondingCurvesFromCriterias(
  criterias: ICriteria[]
) {
  return calculate(criterias);
}
/**
 *
 * @param pools
 * @param initialOrderSize
 * @param strikePriceUSDC
 * @param gas the gas price in WEI
 * @param ethPrice
 * @returns
 */
export async function runWorkerRouter(
  pools: IPoolUntyped[],
  initialOrderSize: number,
  strikePriceUSDC: number,
  gas: number,
  ethPrice: number
) {
  const response = runDepthRouter(
    pools,
    initialOrderSize,
    strikePriceUSDC,
    gas,
    ethPrice
  );
  return response;
}
