import { CounterpartyDetails, IPool, IRouterReturn } from "@/types";

import { DepthRouterReturn } from "@/services/router";
import { sortBy as _sortBy } from "lodash-es";
import { calculateMarginalCostForDeltaX } from "@/services/router/helpers";
import { marginalCostRouter } from "@/services/router/marginalCostRouter";

/**
 *
 * @param pools pools compatible with the otoken that is going to be bought from
 * @param initialOrderSize order size
 * @param deltaX selected deltaX
 * @param strikePriceUSDC selected strike price
 * @param gas gas cost in wei
 * @param ethPrice eth price in dollars
 * @returns an object with the lowest premium, the lowest premium including gas cost and an array of counterparties
 */
const depthRouter = (
  pools: IPool[],
  initialOrderSize: number,
  deltaX: number,
  strikePriceUSDC: number,
  gas: number,
  ethPrice: number
): DepthRouterReturn => {
  /**
   * this is the average cost in gas units of adding a counterparty to the array of counterparties
   */
  const gasUnitsPerCounterparty = 100000;
  const gasCostArray: number[] = [];
  for (let i = 1; i <= pools.length; i++) {
    gasCostArray.push(((gasUnitsPerCounterparty * i * gas) / 1e18) * ethPrice);
  }
  const sortedPools = _sortBy(pools, (o) => o.initialMarginalCost);

  let startIndex = 0;
  let csum = 0;
  for (let i = 0; i < sortedPools.length; i++) {
    csum += sortedPools[i].unlocked;
    if (csum >= initialOrderSize) {
      startIndex = i;
      break;
    }
  }

  let i = startIndex;
  let lowestPremiumGas = Infinity;
  let lowestCounterparties: CounterpartyDetails[] = [];

  while (i < sortedPools.length) {
    const { premium, counterparties } = marginalCostRouter(
      sortedPools.slice(0, i + 1),
      initialOrderSize,
      deltaX,
      strikePriceUSDC
    );

    const premiumGas = premium + gasCostArray[counterparties.length - 1];

    if (premiumGas < lowestPremiumGas) {
      lowestPremiumGas = premiumGas;
      lowestCounterparties = counterparties;
    }

    i++;

    sortedPools.slice(0, i + 1).forEach((pool) => {
      pool.poolOrderSize = 0;
      pool.marginalCostForDeltaX = calculateMarginalCostForDeltaX(pool, deltaX);
    });
  }

  return {
    premium: lowestPremiumGas - gasCostArray[lowestCounterparties.length - 1],
    premiumGas: lowestPremiumGas,
    counterparties: lowestCounterparties,
  };
};

export { depthRouter };
