import { BigDecimal, Bytes } from "@graphprotocol/graph-ts";
import { test, clearStore } from "matchstick-as/assembly/index";
import { log } from "matchstick-as/assembly/log";
import { Curve } from "../../generated/schema";
import { handleCurveAdded } from "../../src/curves";
import { createCurveAdded } from "../events";
import { createNewCurve, toCurveParam } from "../helpers";
import { assertCurveEquality } from "../assertions";
import { MOCKED_CURVE_ID } from "../constants";

// template creation
test("It can create a curve", () => {
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
  const storedCurve = Curve.load(MOCKED_CURVE_ID)!;
  assertCurveEquality(storedCurve, "1", "2", "3", "4", "1");
  clearStore();
});

// curveAdded
test("It can handle the curveAdded event when the curve doesn't exist", () => {
  const mockedEvent = createCurveAdded(
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes,
    toCurveParam("1"),
    toCurveParam("2"),
    toCurveParam("3"),
    toCurveParam("4"),
    toCurveParam("1")
  );
  log.info(
    "Invoking handleCurveAdded with parameters { a: 1, b: 2, c: 3, d: 4, maxUtil: 1 }",
    []
  );
  handleCurveAdded(mockedEvent);
  const storedCurve = Curve.load(MOCKED_CURVE_ID)!;
  assertCurveEquality(storedCurve, "1", "2", "3", "4", "1");
  clearStore();
});

test("It can handle the curveAdded event when the curve is already present", () => {
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
  const mockedEvent = createCurveAdded(
    Bytes.fromHexString(MOCKED_CURVE_ID) as Bytes,
    toCurveParam("2"),
    toCurveParam("3"),
    toCurveParam("4"),
    toCurveParam("5"),
    toCurveParam("2")
  );
  log.info(
    "Invoking handleCurveAdded with parameters { a: 2, b: 3, c: 4, d: 5, maxUtil: 2 }",
    []
  );
  handleCurveAdded(mockedEvent);
  const storedCurve = Curve.load(MOCKED_CURVE_ID)!;
  assertCurveEquality(storedCurve, "1", "2", "3", "4", "1");
  clearStore();
});
