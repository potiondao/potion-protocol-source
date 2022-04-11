import { IPool, IRouterReturn } from "@/types";
import {
  calculateMarginalCostForDeltaX,
  createCounterpartyDetail,
} from "@/services/router/helpers";
import { Heap } from "heap-js";

import { min as _min } from "lodash-es";

const deltaXComparator = (a: IPool, b: IPool): number =>
  a.marginalCostForDeltaX - b.marginalCostForDeltaX;

/**
 * Function that runs the Marginal Cost Router without gas heuristics.
 * @param pools an array of possible counterparties
 * @param initialOrderSize the order size of the buy
 * @param deltaX chunk size
 * @param strikePriceUSDC the strike price in USDC
 * @returns the premium and an array of counterparties
 */
const marginalCostRouter = (
  pools: IPool[],
  initialOrderSize: number,
  deltaX: number,
  strikePriceUSDC: number
): IRouterReturn => {
  let currentOrderSize = initialOrderSize;
  const minMarginalCostForDeltaXHeap = new Heap(deltaXComparator);
  minMarginalCostForDeltaXHeap.init(pools);

  while (currentOrderSize > 0) {
    const minCostPool = minMarginalCostForDeltaXHeap.pop();
    if (!minCostPool) break;
    const fillAmount = _min([
      deltaX,
      minCostPool.maxUtil * minCostPool.size -
        minCostPool.poolOrderSize -
        minCostPool.locked,
      currentOrderSize,
    ]);
    currentOrderSize -= fillAmount;
    /* update the pool ordersize */
    minCostPool.poolOrderSize += fillAmount;
    if (currentOrderSize === 0) break;

    if (
      minCostPool.poolOrderSize + minCostPool.locked <
      minCostPool.maxUtil * minCostPool.size
    ) {
      /**
       * In this case there is still enough free capital for the pool to be
       * selected again, if this condition is not true, do not re-add the pool
       */
      minCostPool.marginalCostForDeltaX = calculateMarginalCostForDeltaX(
        minCostPool,
        fillAmount
      );

      minMarginalCostForDeltaXHeap.push(minCostPool);
    }
  }

  const counterparties = [];
  const premium = pools
    .filter((pool) => pool.poolOrderSize > 0)
    .reduce((sum, pool) => {
      counterparties.push(
        createCounterpartyDetail(
          pool.lp,
          pool.poolId,
          pool.curve,
          pool.curveCriteria,
          pool.poolOrderSize,
          strikePriceUSDC
        )
      );
      return (
        sum +
        ((pool.poolOrderSize + pool.locked) *
          pool.curve.evalAt((pool.poolOrderSize + pool.locked) / pool.size) -
          pool.locked * pool.curve.evalAt(pool.locked / pool.size))
      );
    }, 0);
  return {
    premium,
    counterparties,
  };
};

export { marginalCostRouter };
