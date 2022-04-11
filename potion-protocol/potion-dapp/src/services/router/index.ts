import { minBy as _minBy } from "lodash-es";

import { depthRouter } from "@/services/router/depthRouter";
import {
  calculateDepthMarginalCost,
  calculateMarginalCostForDeltaX,
  checkTotalUnlockedCollateral,
  poolUntypedToTyped
} from "@/services/router/helpers";
import { marginalCostRouter } from "@/services/router/marginalCostRouter";
import { CounterpartyDetails, IPoolUntyped, IRouterReturn } from "@/types";

const runMarginalCostRouter = (
  pools: IPoolUntyped[],
  initialOrderSize: number,
  deltaX: number,
  strikePriceUSDC: number
): IRouterReturn => {
  if (checkTotalUnlockedCollateral(pools, initialOrderSize)) {
    const typedPools = pools.map((pool) => poolUntypedToTyped(pool));
    typedPools.forEach((pool) => {
      pool.marginalCostForDeltaX = calculateMarginalCostForDeltaX(pool, deltaX);
    });
    return marginalCostRouter(
      typedPools,
      initialOrderSize,
      deltaX,
      strikePriceUSDC
    );
  }
  return {
    premium: 0,
    counterparties: [],
  };
};

export interface DepthRouterReturn {
  premium: number;
  premiumGas: number;
  counterparties: CounterpartyDetails[];
}

/**
 *
 * @param pools an array of pools
 * @param initialOrderSize the order size
 * @param strikePriceUSDC the strike price
 * @param gas the gas price in WEI
 * @param ethPrice eth price in dollars
 * @returns an object with the premium, the premium + gas and an array of counterparties
 *
 */
const runDepthRouter = (
  pools: IPoolUntyped[],
  initialOrderSize: number,
  strikePriceUSDC: number,
  gas: number,
  ethPrice: number
): DepthRouterReturn => {
  const depthValues = [0, 0.5, 1];
  if (checkTotalUnlockedCollateral(pools, initialOrderSize)) {
    let newDeltaX = 0;
    if (initialOrderSize >= 100000) {
      newDeltaX = initialOrderSize / 100000;
    } else {
      newDeltaX = 1;
    }
    if (pools.length >= 50) {
      newDeltaX = (newDeltaX * pools.length) / 50;
    }
    const typedPools = pools.map((pool) => poolUntypedToTyped(pool));

    typedPools.forEach((pool) => {
      pool.marginalCostForDeltaX = calculateMarginalCostForDeltaX(
        pool,
        newDeltaX
      );
    });

    const routerResults: DepthRouterReturn[] = [];

    /* We run it 3 times each time with a different depth value */
    for (let i = 0; i < depthValues.length; i++) {
      typedPools.forEach((pool) => {
        pool.initialMarginalCost = calculateDepthMarginalCost(
          pool,
          initialOrderSize,
          newDeltaX,
          depthValues[i],
          gas
        );
      });
      routerResults.push(
        depthRouter(
          typedPools,
          initialOrderSize,
          newDeltaX,
          strikePriceUSDC,
          gas,
          ethPrice
        )
      );
    }

    return { ..._minBy(routerResults, "premiumGas") };
  }
  return {
    premium: 0,
    premiumGas: 0,
    counterparties: [],
  };
};

export { runMarginalCostRouter, runDepthRouter };
