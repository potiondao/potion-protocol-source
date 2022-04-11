/*
 * Functions used to create blockchain events that will be mocked by matchstick
 */

import {
  Deposited,
  CriteriaSetSelected,
  CurveSelected,
  OptionSettled,
  OptionsSold,
  OptionSettlementDistributed,
  OptionsBought,
  Withdrawn,
} from "../generated/PotionLiquidityPool/PotionLiquidityPool";
import { CurveAdded } from "../generated/CurveManager/CurveManager";
import {
  CriteriaAdded,
  CriteriaSetAdded,
} from "../generated/CriteriaManager/CriteriaManager";
import { OtokenCreated } from "../generated/OtokenFactoryContract/OtokenFactoryContract";
import { ethereum, BigInt, Address, Bytes } from "@graphprotocol/graph-ts";
import { newMockEvent } from "matchstick-as/assembly/index";

export function createDeposited(
  lp: Address,
  poolId: BigInt,
  amount: BigInt
): Deposited {
  const mockEvent = newMockEvent();
  const event = new Deposited(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam(
      "poolId",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam(
      "amount",
      ethereum.Value.fromUnsignedBigInt(amount)
    ),
  ];

  return event;
}

export function createCriteriaSetSelected(
  lp: Address,
  poolId: BigInt,
  criteriaSetHash: Bytes
): CriteriaSetSelected {
  const mockEvent = newMockEvent();
  const event = new CriteriaSetSelected(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam(
      "poolId",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam(
      "criteriaSetHash",
      ethereum.Value.fromBytes(criteriaSetHash)
    ),
  ];

  return event;
}

export function createCurveAdded(
  curveHash: Bytes,
  a: BigInt,
  b: BigInt,
  c: BigInt,
  d: BigInt,
  maxUtil: BigInt
): CurveAdded {
  const mockEvent = newMockEvent();
  const event = new CurveAdded(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  const aParam = ethereum.Value.fromUnsignedBigInt(a);
  const bParam = ethereum.Value.fromUnsignedBigInt(b);
  const cParam = ethereum.Value.fromUnsignedBigInt(c);
  const dParam = ethereum.Value.fromUnsignedBigInt(d);
  const maxUtilParam = ethereum.Value.fromUnsignedBigInt(maxUtil);

  const curveParams = new ethereum.Tuple();
  curveParams.push(aParam);
  curveParams.push(bParam);
  curveParams.push(cParam);
  curveParams.push(dParam);
  curveParams.push(maxUtilParam);

  event.parameters = [
    new ethereum.EventParam("curveHash", ethereum.Value.fromBytes(curveHash)),
    new ethereum.EventParam(
      "curveParams",
      ethereum.Value.fromTuple(curveParams)
    ),
  ];

  return event;
}

export function createCurveSelected(
  lp: Address,
  poolId: BigInt,
  curveHash: Bytes
): CurveSelected {
  const mockEvent = newMockEvent();
  const event = new CurveSelected(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam(
      "poolId",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam("curveHash", ethereum.Value.fromBytes(curveHash)),
  ];

  return event;
}

export function createOptionSettled(
  otoken: Address,
  collateralReturned: BigInt
): OptionSettled {
  const mockEvent = newMockEvent();
  const event = new OptionSettled(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("otoken", ethereum.Value.fromAddress(otoken)),
    new ethereum.EventParam(
      "collateralReturned",
      ethereum.Value.fromUnsignedBigInt(collateralReturned)
    ),
  ];

  return event;
}

export function createOptionsSold(
  lp: Address,
  poolId: BigInt,
  otoken: Address,
  curveHash: Bytes,
  numberOfOtokens: BigInt,
  liquidityCollateralized: BigInt,
  premiumReceived: BigInt
): OptionsSold {
  const mockEvent = newMockEvent();
  const event = new OptionsSold(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam(
      "poolId",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam("otoken", ethereum.Value.fromAddress(otoken)),
    new ethereum.EventParam("curveHash", ethereum.Value.fromBytes(curveHash)),
    new ethereum.EventParam(
      "numberOfOtokens",
      ethereum.Value.fromUnsignedBigInt(numberOfOtokens)
    ),
    new ethereum.EventParam(
      "liquidityCollateralized",
      ethereum.Value.fromUnsignedBigInt(liquidityCollateralized)
    ),
    new ethereum.EventParam(
      "premiumReceived",
      ethereum.Value.fromUnsignedBigInt(premiumReceived)
    ),
  ];

  return event;
}

export function createOptionSettlementDistributed(
  otoken: Address,
  lp: Address,
  poolId: BigInt,
  collateralReturned: BigInt
): OptionSettlementDistributed {
  const mockEvent = newMockEvent();
  const event = new OptionSettlementDistributed(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam("otoken", ethereum.Value.fromAddress(otoken)),
    new ethereum.EventParam(
      "poolid",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam(
      "collateralReturned",
      ethereum.Value.fromUnsignedBigInt(collateralReturned)
    ),
  ];

  return event;
}

export function createOptionsBought(
  buyer: Address,
  otoken: Address,
  numberOfOtokens: BigInt,
  totalPremiumPaid: BigInt
): OptionsBought {
  const mockEvent = newMockEvent();
  const event = new OptionsBought(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("buyer", ethereum.Value.fromAddress(buyer)),
    new ethereum.EventParam("otoken", ethereum.Value.fromAddress(otoken)),
    new ethereum.EventParam(
      "numberOfOtokens",
      ethereum.Value.fromUnsignedBigInt(numberOfOtokens)
    ),
    new ethereum.EventParam(
      "totalPremiumPaid",
      ethereum.Value.fromUnsignedBigInt(totalPremiumPaid)
    ),
  ];

  return event;
}

export function createWithdrawn(
  lp: Address,
  poolId: BigInt,
  amount: BigInt
): Withdrawn {
  const mockEvent = newMockEvent();
  const event = new Withdrawn(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  event.parameters = [
    new ethereum.EventParam("lp", ethereum.Value.fromAddress(lp)),
    new ethereum.EventParam(
      "poolId",
      ethereum.Value.fromUnsignedBigInt(poolId)
    ),
    new ethereum.EventParam(
      "amount",
      ethereum.Value.fromUnsignedBigInt(amount)
    ),
  ];

  return event;
}

export function createCriteriaAdded(
  criteriaHash: Bytes,
  underlyingAsset: Address,
  strikeAsset: Address,
  isPut: boolean,
  maxStrikePercent: BigInt,
  maxDurationInDays: BigInt
): CriteriaAdded {
  const mockEvent = newMockEvent();
  const event = new CriteriaAdded(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  const underlyingAssetParam = ethereum.Value.fromAddress(underlyingAsset);
  const strikeAssetParam = ethereum.Value.fromAddress(strikeAsset);
  const isPutParam = ethereum.Value.fromBoolean(isPut);
  const maxStrikePercentParam =
    ethereum.Value.fromUnsignedBigInt(maxStrikePercent);
  const maxDurationInDaysParam =
    ethereum.Value.fromUnsignedBigInt(maxDurationInDays);

  const criteriaTuple = new ethereum.Tuple();
  criteriaTuple.push(underlyingAssetParam);
  criteriaTuple.push(strikeAssetParam);
  criteriaTuple.push(isPutParam);
  criteriaTuple.push(maxStrikePercentParam);
  criteriaTuple.push(maxDurationInDaysParam);

  event.parameters = [
    new ethereum.EventParam(
      "criteriaHash",
      ethereum.Value.fromBytes(criteriaHash)
    ),
    new ethereum.EventParam(
      "criteriaParams",
      ethereum.Value.fromTuple(criteriaTuple)
    ),
  ];

  return event;
}

export function createCriteriaSetAdded(
  criteriaSetHash: Bytes,
  criteriaSet: Array<Bytes>
): CriteriaSetAdded {
  const mockEvent = newMockEvent();
  const event = new CriteriaSetAdded(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );

  const criteriaSetValues: ethereum.Value[] = [];
  for (let i = 0; i < criteriaSet.length; i += 1) {
    const value = ethereum.Value.fromBytes(criteriaSet[i]);
    criteriaSetValues.push(value);
  }

  event.parameters = [
    new ethereum.EventParam(
      "criteriaSetHash",
      ethereum.Value.fromBytes(criteriaSetHash)
    ),
    new ethereum.EventParam(
      "criteriaSet",
      ethereum.Value.fromArray(criteriaSetValues)
    ),
  ];

  return event;
}

export function createOtokenCreated(
  tokenAddress: Address,
  creator: Address,
  underlying: Address,
  strike: Address,
  collateral: Address,
  strikePrice: BigInt,
  expiry: BigInt,
  isPut: boolean
): OtokenCreated {
  const mockEvent = newMockEvent();
  const event = new OtokenCreated(
    mockEvent.address,
    mockEvent.logIndex,
    mockEvent.transactionLogIndex,
    mockEvent.logType,
    mockEvent.block,
    mockEvent.transaction,
    mockEvent.parameters
  );
  event.parameters = [
    new ethereum.EventParam(
      "tokenAddress",
      ethereum.Value.fromAddress(tokenAddress)
    ),
    new ethereum.EventParam("creator", ethereum.Value.fromAddress(creator)),
    new ethereum.EventParam(
      "underlying",
      ethereum.Value.fromAddress(underlying)
    ),
    new ethereum.EventParam("strike", ethereum.Value.fromAddress(strike)),
    new ethereum.EventParam(
      "collateral",
      ethereum.Value.fromAddress(collateral)
    ),
    new ethereum.EventParam(
      "strikePrice",
      ethereum.Value.fromUnsignedBigInt(strikePrice)
    ),
    new ethereum.EventParam(
      "expiry",
      ethereum.Value.fromUnsignedBigInt(expiry)
    ),
    new ethereum.EventParam("isPut", ethereum.Value.fromBoolean(isPut)),
  ];

  return event;
}
