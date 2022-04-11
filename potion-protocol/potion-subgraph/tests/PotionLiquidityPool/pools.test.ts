import { test, assert, clearStore } from "matchstick-as/assembly/index";
import { log } from "matchstick-as/assembly/log";
import { Pool, Curve, CriteriaSet } from "../../generated/schema";
import {
  createPoolId,
  handleCurveSelected,
  handleCriteriaSetSelected,
  handleDeposited,
  handleWithdrawn,
} from "../../src/pools";
import { ethereum, Bytes, BigDecimal } from "@graphprotocol/graph-ts";
import {
  createDeposited,
  createWithdrawn,
  createCurveSelected,
  createCriteriaSetSelected,
} from "../events";
import { assertPoolLiquidity, assertPoolMarketData } from "../assertions";
import {
  createNewPool,
  createNewCurve,
  createNewCriteriaSet,
} from "../helpers";
import {
  MOCKED_LP,
  BIGINT_ZERO,
  BIGINT_ONE_HUNDRED_AS_COLLATERAL,
  MOCKED_CURVE_ID,
  MOCKED_CRITERIA_SET_ID,
} from "../constants";

// Test pool creation
test("It can create a pool", () => {
  log.info(
    "Trying to create a pool with poolId 0 and lp '0x0000000000000000000000000000000000000000'",
    []
  );
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "0", "");
  newPool.save();
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assert.equals(
    ethereum.Value.fromString(MOCKED_LP.toHexString()),
    ethereum.Value.fromString(storedPool.lp.toHexString())
  );
  assert.equals(
    ethereum.Value.fromUnsignedBigInt(BIGINT_ZERO),
    ethereum.Value.fromUnsignedBigInt(storedPool.poolId)
  );
  assert.equals(
    ethereum.Value.fromString("0"),
    ethereum.Value.fromString(storedPool.utilization.toString())
  );
  assertPoolMarketData(storedPool, "0", "0", "0");
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

// Test Deposit event
test("It can deposit liquidity in an already existing pool without a template", () => {
  log.info(
    "Trying to create a pool with poolId 0, lp '0x0000000000000000000000000000000000000000' and a size of 100",
    []
  );
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "100", "");
  newPool.save();
  log.info("Stored the pool, proceding with the mocked event", []);
  const mockedEvent = createDeposited(
    MOCKED_LP,
    BIGINT_ZERO,
    BIGINT_ONE_HUNDRED_AS_COLLATERAL
  );
  log.info(
    "Calling handleDeposited with poolId 0, lp '0x0000000000000000000000000000000000000000' and amount 100",
    []
  );
  handleDeposited(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "200", "200", "0", "100");
  clearStore();
});

// Test Withdrawn event
test("It can withdraw from a pool without a template leaving some liquidity inside", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "200", "");
  newPool.save();
  const mockedEvent = createWithdrawn(
    MOCKED_LP,
    BIGINT_ZERO,
    BIGINT_ONE_HUNDRED_AS_COLLATERAL
  );
  log.info(
    "Calling handleWithdrawn with poolId 0, lp '0x0000000000000000000000000000000000000000' and amount 100",
    []
  );
  handleWithdrawn(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "100", "100", "0", "200");
  clearStore();
});

test("It can withdraw from a pool without a template leaving it without liquidity", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "100", "");
  newPool.save();
  const mockedEvent = createWithdrawn(
    MOCKED_LP,
    BIGINT_ZERO,
    BIGINT_ONE_HUNDRED_AS_COLLATERAL
  );
  log.info(
    "Calling handleWithdrawn with poolId 0, lp '0x0000000000000000000000000000000000000000' and amount 100",
    []
  );
  handleWithdrawn(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "100");
  clearStore();
});

test(
  "It raises an error when we try to withdraw from a pool that doesn't exist",
  () => {
    const mockedEvent = createWithdrawn(
      MOCKED_LP,
      BIGINT_ZERO,
      BIGINT_ONE_HUNDRED_AS_COLLATERAL
    );
    log.info(
      "Calling handleWithdrawn with poolId 0, lp '0x0000000000000000000000000000000000000000' and amount 100",
      []
    );
    handleWithdrawn(mockedEvent);
    clearStore();
  },
  true
);

test(
  "It raises an error when we try to withdraw more liqudity than what was actually available in the pool",
  () => {
    const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "50", "");
    newPool.save();
    const mockedEvent = createWithdrawn(
      MOCKED_LP,
      BIGINT_ZERO,
      BIGINT_ONE_HUNDRED_AS_COLLATERAL
    );
    log.info(
      "Calling handleWithdrawn with poolId 0, lp '0x0000000000000000000000000000000000000000' and amount 100",
      []
    );
    handleWithdrawn(mockedEvent);
    clearStore();
  },
  true
);

// CurveSelected tests
test("It can assign a new curve to a new pool", () => {
  const mockedEvent = createCurveSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes
  );
  log.info(
    "Calling handleCurveSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and curveId '0x00000000000000000000000000000000000000100'",
    []
  );
  handleCurveSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

test("It can assign an existing curve to a new pool", () => {
  const curve = createNewCurve(
    MOCKED_CURVE_ID,
    BigDecimal.fromString("1"),
    BigDecimal.fromString("2"),
    BigDecimal.fromString("3"),
    BigDecimal.fromString("4"),
    BigDecimal.fromString("1")
  ) as Curve;
  curve.save();
  log.info(
    "Created curve with parameters { a: 1, b: 2, c: 3, d: 4, maxUtil: 1 }",
    []
  );
  const mockedEvent = createCurveSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes
  );
  log.info(
    "Calling handleCurveSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and curveId '0x00000000000000000000000000000000000000100'",
    []
  );
  handleCurveSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

test("It can assign a new curve to an existing pool", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "0", "");
  newPool.save();
  log.info(
    "Created pool with poolId 0 and lp '0x0000000000000000000000000000000000000000'",
    []
  );
  const mockedEvent = createCurveSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes
  );
  log.info(
    "Calling handleCurveSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and curveId '0x00000000000000000000000000000000000000100'",
    []
  );
  handleCurveSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

test("It can assign an existing curve to an exististing pool", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "0", "");
  newPool.save();
  log.info(
    "Created pool with poolId 0 and lp '0x0000000000000000000000000000000000000000'",
    []
  );
  const curve = createNewCurve(
    MOCKED_CURVE_ID,
    BigDecimal.fromString("1"),
    BigDecimal.fromString("2"),
    BigDecimal.fromString("3"),
    BigDecimal.fromString("4"),
    BigDecimal.fromString("1")
  ) as Curve;
  curve.save();
  log.info(
    "Created curve with parameters { a: 1, b: 2, c: 3, d: 4, maxUtil: 1 }",
    []
  );
  const mockedEvent = createCurveSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes
  );
  log.info(
    "Calling handleCurveSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and curveId '0x00000000000000000000000000000000000000100'",
    []
  );
  handleCurveSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

// CriteriaSetSelected tests
test("It can assign an existing criteriaSet to a new pool", () => {
  const criteriaSet = createNewCriteriaSet(
    MOCKED_CRITERIA_SET_ID
  ) as CriteriaSet;
  criteriaSet.save();
  log.info(
    "Created criteriaSet with id '0x00000000000000000000000000000000000001000'",
    []
  );
  const mockedEvent = createCriteriaSetSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CRITERIA_SET_ID) as Bytes
  );
  log.info(
    "Calling handleCriteriaSetSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and criteriaSetId '0x00000000000000000000000000000000000001000'",
    []
  );
  handleCriteriaSetSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

test("It can assign a new criteriaSet to an existing pool", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "0", "");
  newPool.save();
  log.info(
    "Created pool with poolId 0 and lp '0x0000000000000000000000000000000000000000'",
    []
  );
  const mockedEvent = createCriteriaSetSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CRITERIA_SET_ID) as Bytes
  );
  log.info(
    "Calling handleCriteriaSetSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and criteriaSetId '0x00000000000000000000000000000000000001000'",
    []
  );
  handleCriteriaSetSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});

test("It can assign an existing criteriaSet to an exististing pool", () => {
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "0", "");
  newPool.save();
  log.info(
    "Created pool with poolId 0 and lp '0x0000000000000000000000000000000000000000'",
    []
  );
  const criteriaSet = createNewCriteriaSet(
    MOCKED_CRITERIA_SET_ID
  ) as CriteriaSet;
  criteriaSet.save();
  log.info(
    "Created criteriaSet with id '0x00000000000000000000000000000000000001000'",
    []
  );
  const mockedEvent = createCriteriaSetSelected(
    MOCKED_LP,
    BIGINT_ZERO,
    Bytes.fromHexString(MOCKED_CRITERIA_SET_ID) as Bytes
  );
  log.info(
    "Calling handleCriteriaSetSelected with poolId 0, lp '0x0000000000000000000000000000000000000000' and criteriaSetId '0x00000000000000000000000000000000000001000'",
    []
  );
  handleCriteriaSetSelected(mockedEvent);
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO)) as Pool;
  assertPoolLiquidity(storedPool, "0", "0", "0", "0");
  clearStore();
});
