import { test, clearStore } from "matchstick-as/assembly/index";
import { log } from "matchstick-as/assembly/log";
import { Pool, Template } from "../../generated/schema";
import { createPoolId, handleDeposited } from "../../src/pools";
import { BigDecimal } from "@graphprotocol/graph-ts";
import { createDeposited } from "../events";
import { assertTemplateLiquidity } from "../assertions";
import { createNewPool, createNewTemplate, createNewCurve } from "../helpers";
import {
  MOCKED_LP,
  BIGINT_ZERO,
  BIGINT_ONE,
  BIGINT_ONE_HUNDRED_AS_COLLATERAL,
  MOCKED_CURVE_ID,
  MOCKED_CRITERIA_SET_ID,
} from "../constants";

// template creation
test("It can create a template", () => {
  const newTemplate = createNewTemplate(
    MOCKED_CURVE_ID,
    MOCKED_CRITERIA_SET_ID,
    "0",
    "0",
    MOCKED_LP
  );
  newTemplate.save();
  clearStore();
});

// Deposit event
test("It can deposit liquidity in an already existing pool with a template", () => {
  const curve = createNewCurve(
    MOCKED_CURVE_ID,
    BigDecimal.fromString("1"),
    BigDecimal.fromString("2"),
    BigDecimal.fromString("3"),
    BigDecimal.fromString("4"),
    BigDecimal.fromString("1")
  );
  curve.save();
  log.info(
    "Trying to create a pool with poolId 0, lp '0x0000000000000000000000000000000000000000' and a size of 100",
    []
  );
  const newTemplate = createNewTemplate(
    MOCKED_CURVE_ID,
    MOCKED_CRITERIA_SET_ID,
    "100",
    "0",
    MOCKED_LP
  );
  newTemplate.save();
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "100", newTemplate.id);
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
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO))!;
  const storedTemplate = Template.load(storedPool.template as string)!;
  assertTemplateLiquidity(storedTemplate, "200", "0");
  clearStore();
});
test("It can deposit liquidity in an already existing pool with a template that has other pools", () => {
  const curve = createNewCurve(
    MOCKED_CURVE_ID,
    BigDecimal.fromString("1"),
    BigDecimal.fromString("2"),
    BigDecimal.fromString("3"),
    BigDecimal.fromString("4"),
    BigDecimal.fromString("1")
  );
  curve.save();
  const newTemplate = createNewTemplate(
    MOCKED_CURVE_ID,
    MOCKED_CRITERIA_SET_ID,
    "150",
    "0",
    MOCKED_LP
  );
  newTemplate.save();
  const newPool = createNewPool(MOCKED_LP, BIGINT_ZERO, "100", newTemplate.id);
  newPool.save();
  log.info(
    "Created a pool with poolId 0, lp '0x0000000000000000000000000000000000000000' and a size of 100",
    []
  );
  const otherPool = createNewPool(MOCKED_LP, BIGINT_ONE, "50", newTemplate.id);
  otherPool.save();
  log.info(
    "Created a pool with poolId 1, lp '0x0000000000000000000000000000000000000000' and a size of 50",
    []
  );
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
  const storedPool = Pool.load(createPoolId(MOCKED_LP, BIGINT_ZERO))!;
  const storedTemplate = Template.load(storedPool.template as string)!;
  assertTemplateLiquidity(storedTemplate, "250", "0");
  clearStore();
});
