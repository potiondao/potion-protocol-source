import { test, clearStore } from "matchstick-as/assembly/index";
import { log } from "matchstick-as/assembly/log";
import {
  Criteria,
  CriteriaSet,
  CriteriaJoinedCriteriaSet,
} from "../../generated/schema";
import {
  handleCriteriaAdded,
  handleCriteriaSetAdded,
} from "../../src/criterias";
import { BigDecimal, BigInt, Bytes, Address } from "@graphprotocol/graph-ts";
import {
  createNewCriteria,
  createNewCriteriaSet,
  createNewCriteriaJoinedCriteriaSet,
} from "../helpers";
import { createCriteriaAdded, createCriteriaSetAdded } from "../events";
import { assertCriteriaEquality } from "../assertions";
import {
  MOCKED_CRITERIA_ID,
  MOCKED_CRITERIA_A_ID,
  MOCKED_CRITERIA_B_ID,
  MOCKED_CRITERIA_SET_ID,
  MOCKED_TOKEN_A_ID,
  MOCKED_TOKEN_B_ID,
} from "../constants";

// criteria creation
test("It can create a criteria", () => {
  const newCriteria = createNewCriteria(
    MOCKED_CRITERIA_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_TOKEN_B_ID,
    true,
    BigDecimal.fromString("100"),
    BigInt.fromString("30")
  ) as Criteria;
  newCriteria.save();
  log.info(
    "Created criteria with maxStrikePercent 100 and maxDurationInDays 30",
    []
  );
  const storedCriteria = Criteria.load(MOCKED_CRITERIA_ID) as Criteria;
  assertCriteriaEquality(storedCriteria, true, "100", "30");
  clearStore();
});

// criteriaSet creation
test("It can create a criteriaSet", () => {
  const newCriteriaSet = createNewCriteriaSet(
    MOCKED_CRITERIA_SET_ID
  ) as CriteriaSet;
  newCriteriaSet.save();
  clearStore();
});

// criteria joined to a CriteriaSet
test("It can join a criteria with a CriteriaSet", () => {
  const newCriteria = createNewCriteria(
    MOCKED_CRITERIA_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_TOKEN_B_ID,
    true,
    BigDecimal.fromString("100"),
    BigInt.fromString("30")
  ) as Criteria;
  newCriteria.save();
  log.info(
    "Created criteria with maxStrikePercent 100 and maxDurationInDays 30",
    []
  );
  const newCriteriaSet = createNewCriteriaSet(
    MOCKED_CRITERIA_SET_ID
  ) as CriteriaSet;
  newCriteriaSet.save();
  const newCriteriaJoinedCriteriaSet = createNewCriteriaJoinedCriteriaSet(
    MOCKED_CRITERIA_ID,
    MOCKED_CRITERIA_SET_ID
  ) as CriteriaJoinedCriteriaSet;
  newCriteriaJoinedCriteriaSet.save();
  clearStore();
});

// CriteriaAdded event
test("In can handle the CriteriaAdded event whn the criteria doesn't exist", () => {
  const mockedEvent = createCriteriaAdded(
    Bytes.fromHexString(MOCKED_CRITERIA_ID) as Bytes,
    Address.fromString(MOCKED_TOKEN_A_ID),
    Address.fromString(MOCKED_TOKEN_B_ID),
    true,
    BigInt.fromString("100"),
    BigInt.fromString("30")
  );
  log.info(
    "Invoking handleCriteriaAdded with parameters { isPut: true, maxStrikePercent: 100, maxDurationInDays: 30 }",
    []
  );
  handleCriteriaAdded(mockedEvent);
  const storedCriteria = Criteria.load(MOCKED_CRITERIA_ID) as Criteria;
  assertCriteriaEquality(storedCriteria, true, "100", "30");
  clearStore();
});
test("In can handle the CriteriaAdded event when the criteria is already present", () => {
  const newCriteria = createNewCriteria(
    MOCKED_CRITERIA_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_TOKEN_B_ID,
    true,
    BigDecimal.fromString("100"),
    BigInt.fromString("30")
  ) as Criteria;
  newCriteria.save();
  log.info(
    "Created criteria with maxStrikePercent 100 and maxDurationInDays 30",
    []
  );
  const mockedEvent = createCriteriaAdded(
    Bytes.fromHexString(MOCKED_CRITERIA_ID) as Bytes,
    Address.fromString(MOCKED_TOKEN_A_ID),
    Address.fromString(MOCKED_TOKEN_B_ID),
    true,
    BigInt.fromString("100"),
    BigInt.fromString("30")
  );
  log.info(
    "Invoking handleCriteriaAdded with parameters { maxStrikePercent: 1000, maxDurationInDays: 200 }",
    []
  );
  handleCriteriaAdded(mockedEvent);
  const storedCriteria = Criteria.load(MOCKED_CRITERIA_ID) as Criteria;
  assertCriteriaEquality(storedCriteria, true, "100", "30");
  clearStore();
});

// CriteriaSetAdded event
test("In can handle CriteriaSetAdded", () => {
  const newCriteria = createNewCriteria(
    MOCKED_CRITERIA_A_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_TOKEN_B_ID,
    true,
    BigDecimal.fromString("100"),
    BigInt.fromString("30")
  ) as Criteria;
  newCriteria.save();
  log.info(
    "Created criteria with maxStrikePercent 100 and maxDurationInDays 30",
    []
  );
  const secondNewCriteria = createNewCriteria(
    MOCKED_CRITERIA_B_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_TOKEN_B_ID,
    true,
    BigDecimal.fromString("200"),
    BigInt.fromString("13")
  ) as Criteria;
  secondNewCriteria.save();
  log.info(
    "Created criteria with maxStrikePercent 200 and maxDurationInDays 13",
    []
  );
  const mockedEvent = createCriteriaSetAdded(
    Bytes.fromHexString(MOCKED_CRITERIA_SET_ID) as Bytes,
    [
      Bytes.fromHexString(MOCKED_CRITERIA_A_ID) as Bytes,
      Bytes.fromHexString(MOCKED_CRITERIA_B_ID) as Bytes,
    ]
  );
  log.info(
    "Invoking handleCriteriaSetAdded passing criteriaSetId '0x0000000000000000000000000000000000001000' and as criterias ['0x0000000000000000000000000000000000000200', '0x0000000000000000000000000000000000000300']",
    []
  );
  handleCriteriaSetAdded(mockedEvent);
  clearStore();
});
