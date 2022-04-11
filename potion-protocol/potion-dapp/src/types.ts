import {
  CurveCriteria,
  CurveParamsAsBigNumbers,
  HyperbolicCurve,
} from "potion-contracts/scripts/lib/typeHelpers";

import { BigNumberish } from "@ethersproject/bignumber";

interface Criteria {
  address: string;
  decimals: string;
  duration: string;
  id: string;
  name: string;
  selected: boolean;
  strike: string;
  symbol: string;
}

interface CurveParams {
  a: string;
  b: string;
  c: string;
  d: string;
  maxUtil: string;
}

interface PoolIdentifier {
  lp: string;
  poolId: number;
}

interface ICriteria {
  underlyingAsset: {
    id: string;
    symbol: string;
  };
  strikeAsset: {
    id: string;
  };
  isPut: string;
  maxStrikePercent: string;
  maxDurationInDays: string;
  stylizedStrike: string;
  endDate: string;
}

interface IOToken {
  tokenAddress: string;
  underlying: {
    id: string;
    symbol: string;
  };
  expiry: string;
  strikePrice: string;
}

interface IPotions {
  buyer: string;
  numberOfOTokens: string;
  otoken: {
    id: string;
    decimals: string;
    strikePrice: string;
    expiry: string;
    underlyingAsset: {
      id: string;
      name: string;
      symbol: string;
      address: string;
    };
  };
  premium: string;
}

interface PopularOTokens {
  mostPurchased: IOToken[];
  mostCollateralized: IOToken[];
}

interface IPoolUntyped {
  id: string;
  poolId: string;
  lp: string;
  size: string;
  locked: string;
  unlocked: string;
  poolOrderSize: string;
  utilization: string;
  underlyingAddress: string;
  strikeAddress: string;
  maxStrikePercent: string;
  maxDurationInDays: string;
  isPut: boolean;
  template: {
    curve: {
      id: string;
      a: string;
      b: string;
      c: string;
      d: string;
      maxUtil: string;
    };
  };
}

interface IPool {
  id: string;
  poolId: number;
  lp: string;
  size: number;
  locked: number;
  unlocked: number;
  curve: HyperbolicCurve;
  curveCriteria: CurveCriteria;
  poolOrderSize: number;
  poolPremium: number;
  marginalCostForDeltaX: number;
  initialMarginalCost: number;
  util: number;
  maxUtil: number;
}

interface IRouterReturn {
  premium: number;
  counterparties: CounterpartyDetails[];
}

interface IRecord {
  LP: string;
  Order_Size: number;
  Order_portion: number;
  Premium: number;
}

interface PoolRecord {
  id: string;
  lpRecord: {
    lp: string;
    otoken: {
      id: string;
      poolId: number;
    };
  };
  pool: {
    poolId: number;
  };
}

interface PoolRecordIdentifier {
  lp: string;
  poolId: number;
  otokenAddress: string;
}

export class CounterpartyDetails {
  curve: CurveParamsAsBigNumbers;

  constructor(
    public lp: string,
    public poolId: number,
    public curveAs64x64: HyperbolicCurve,
    public criteria: CurveCriteria,
    public orderSizeInOtokens: BigNumberish
  ) {
    this.curve = curveAs64x64.asSolidityStruct();
  }
}

interface UserPotions {
  activePotions: IPotions[];
  expiredPotions: IPotions[];
}

export type {
  Criteria,
  CurveParams,
  PoolIdentifier,
  ICriteria,
  IOToken,
  PopularOTokens,
  IPotions,
  IPoolUntyped,
  IPool,
  IRecord,
  IRouterReturn,
  PoolRecord,
  PoolRecordIdentifier,
  UserPotions,
};
