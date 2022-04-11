import { range as _range } from "lodash-es";

import { HYPERBOLIC_POINTS } from "@/helpers/pools";
import { Router } from "@/services/api/router";
import { runMarginalCostRouter } from "@/services/router";
import { ICriteria } from "@/types";

const stepArray = [0.01].concat(
  _range(1 / HYPERBOLIC_POINTS, 1, 1 / HYPERBOLIC_POINTS)
);

interface EmergingBondingCurves {
  data: number[];
  underlyingSymbol: string;
}
/**
 *
 * @param criterias
 * @returns the data needed to compute the chart for the emerging bonding curves of the selected criterias
 */
const getEmergingBondingCurvesFromCriterias = async (
  criterias: ICriteria[]
): Promise<EmergingBondingCurves[]> => {
  const bondingCurves: EmergingBondingCurves[] = [];
  for (const criteria of criterias) {
    const pools = await Router.getPoolsFromCriteria(
      criteria.underlyingAsset.id,
      criteria.maxStrikePercent,
      criteria.maxDurationInDays
    );
    if (pools.length > 0) {
      const totalUnlocked: number = pools.reduce((sum, pool) => {
        return sum + parseFloat(pool.unlocked);
      }, 0);
      const criteriaRelativePremiums = stepArray.map((step) => {
        const orderSize = totalUnlocked * step;
        const { premium } = runMarginalCostRouter(pools, orderSize, 1000, 1);
        return orderSize > 0 ? premium / orderSize : 0;
      });
      bondingCurves.push({
        data: criteriaRelativePremiums,
        underlyingSymbol: criteria.underlyingAsset.symbol,
      });
    } else {
      bondingCurves.push({
        data: [],
        underlyingSymbol: criteria.underlyingAsset.symbol,
      });
    }
  }
  return bondingCurves;
};

export { getEmergingBondingCurvesFromCriterias };
