import {
  test,
  clearStore,
  createMockedFunction,
} from "matchstick-as/assembly/index";
import { log } from "matchstick-as/assembly/log";
import { ethereum, BigInt, BigDecimal, Address } from "@graphprotocol/graph-ts";
import { OToken } from "../../generated/schema";
import {
  MOCKED_TOKEN_A_ID,
  MOCKED_TOKEN_B_ID,
  MOCKED_TOKEN_C_ID,
  MOCKED_OTOKEN_ID,
  MOCKED_LP,
  COLLATERAL_PRECISION_DECIMALS,
} from "../constants";
import { createNewOtoken, formatStrike } from "../helpers";
import { createOtokenCreated } from "../events";
import { assertOtokenEquality } from "../assertions";
import { handleOtokenCreate } from "../../src/otoken";

// otoken creation
test("It can create an otoken", () => {
  const newOtoken = createNewOtoken(
    MOCKED_OTOKEN_ID,
    MOCKED_TOKEN_A_ID,
    MOCKED_LP.toHexString(),
    MOCKED_TOKEN_B_ID,
    MOCKED_TOKEN_C_ID,
    MOCKED_TOKEN_C_ID,
    BigDecimal.fromString("100"),
    BigInt.fromString("30"),
    true,
    BigInt.fromString("18"),
    false,
    BigDecimal.fromString("200"),
    BigDecimal.fromString("100"),
    BigDecimal.fromString("0"),
    BigDecimal.fromString("5"),
    BigInt.fromString("12")
  ) as OToken;
  newOtoken.save();
  const storedOtoken = OToken.load(MOCKED_OTOKEN_ID) as OToken;
  assertOtokenEquality(
    storedOtoken,
    MOCKED_TOKEN_A_ID,
    MOCKED_LP.toHexString(),
    MOCKED_TOKEN_B_ID,
    MOCKED_TOKEN_C_ID,
    MOCKED_TOKEN_C_ID,
    BigDecimal.fromString("100"),
    BigInt.fromString("30"),
    true,
    BigInt.fromString("18"),
    false,
    BigDecimal.fromString("200"),
    BigDecimal.fromString("100"),
    BigDecimal.fromString("0"),
    BigDecimal.fromString("5"),
    BigInt.fromString("12")
  );
  clearStore();
});

// OtokenCreated event
test("It can handle the OtokenCreated event", () => {
  const mockedEvent = createOtokenCreated(
    Address.fromString(MOCKED_TOKEN_A_ID),
    MOCKED_LP,
    Address.fromString(MOCKED_TOKEN_B_ID),
    Address.fromString(MOCKED_TOKEN_C_ID),
    Address.fromString(MOCKED_TOKEN_C_ID),
    formatStrike("1000"),
    BigInt.fromString("30"),
    true
  );
  log.info("Preparing the mocked decimals function, it will return an 8", []);
  createMockedFunction(
    Address.fromString(MOCKED_TOKEN_A_ID) as Address,
    "decimals",
    "decimals():(uint8)"
  )
    .withArgs([])
    .returns([ethereum.Value.fromI32(COLLATERAL_PRECISION_DECIMALS)]);
  log.info(
    "Calling handleOtokenCreate with parameters: { strikePrice: 1000, expiry: 30 }",
    []
  );
  handleOtokenCreate(mockedEvent);
  const storedOtoken = OToken.load(MOCKED_TOKEN_A_ID) as OToken;
  assertOtokenEquality(
    storedOtoken,
    MOCKED_TOKEN_A_ID,
    MOCKED_LP.toHexString(),
    MOCKED_TOKEN_B_ID,
    MOCKED_TOKEN_C_ID,
    MOCKED_TOKEN_C_ID,
    BigDecimal.fromString("1000"),
    BigInt.fromString("30"),
    true,
    BigInt.fromI32(COLLATERAL_PRECISION_DECIMALS),
    false,
    BigDecimal.fromString("0"),
    BigDecimal.fromString("0"),
    BigDecimal.fromString("0"),
    BigDecimal.fromString("0"),
    BigInt.fromString("0")
  );
  clearStore();
});
