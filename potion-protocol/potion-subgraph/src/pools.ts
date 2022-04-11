import { BigDecimal, BigInt, Bytes, log } from "@graphprotocol/graph-ts";

import {
  CriteriaSetSelected,
  CurveSelected,
  Deposited,
  OptionsBought,
  OptionSettled,
  OptionSettlementDistributed,
  OptionsSold,
  Withdrawn
} from "../generated/PotionLiquidityPool/PotionLiquidityPool";
import {
  BuyerRecord,
  LPRecord,
  OrderBookEntry,
  OToken,
  Pool,
  PoolRecord,
  PoolSnapshot,
  Template
} from "../generated/schema";
import { calculateAverageCost } from "./curves";
import {
  getOTokenIdFromAddress,
  oTokenFixedtoDecimals,
  oTokenIncrementLiquidity,
  oTokenIncrementPurchasesCount,
  oTokenSettled
} from "./otoken";
import { collateralFixedtoDecimals } from "./token";

const ZERO_BIGDECIMAL = BigDecimal.fromString("0");
const HUNDRED_BIGDECIMAL = BigDecimal.fromString("100");
const ONE_BIGINT = BigInt.fromI32(1);

// Have to manually define this Enum since codegen schema does not contain Enums
export enum Actions {
  POOL_LEFT_TEMPLATE = -3,
  CURVE_CHANGE = -2,
  CRITERIASET_CHANGE = -1,
  DEPOSIT = 0,
  WITHDRAW = 1,
  PREMIUM_RECEIVED = 2,
  CAPITAL_EXERCISED = 3,
}

export function createPoolId(lp: Bytes, poolId: BigInt): string {
  return lp.toHexString() + poolId.toHexString();
}

function createPoolSnapshotId(
  lp: Bytes,
  poolId: BigInt,
  templateId: string,
  timestamp: BigInt
): string {
  return (
    lp.toHexString() +
    poolId.toHexString() +
    timestamp.toHexString() +
    templateId
  );
}

export function createTemplateId(
  curveHash: Bytes,
  criteriaSetHash: Bytes
): string {
  return curveHash.toHexString() + criteriaSetHash.toHexString();
}

export function createTemplate(
  templateId: string,
  curveHash: string,
  criteriaSetHash: string,
  creator: Bytes
): Template {
  const template = new Template(templateId);
  template.size = BigDecimal.fromString("0");
  template.locked = BigDecimal.fromString("0");
  template.utilization = BigDecimal.fromString("0");
  template.numPools = BigInt.fromI32(0);
  template.curve = curveHash;
  template.criteriaSet = criteriaSetHash;
  template.pnlTotal = BigDecimal.fromString("0");
  template.liquidityAtTrades = BigDecimal.fromString("0");
  template.pnlPercentage = BigDecimal.fromString("0");
  template.creator = creator;
  return template;
}

function createLPRecordID(lp: Bytes, otoken: Bytes): string {
  return lp.toHexString() + otoken.toHexString();
}

function createPoolRecordID(lp: Bytes, poolId: BigInt, otoken: Bytes): string {
  return lp.toHexString() + poolId.toHexString() + otoken.toHexString();
}

function getUtilization(size: BigDecimal, locked: BigDecimal): BigDecimal {
  return size.gt(ZERO_BIGDECIMAL) ? locked.div(size) : ZERO_BIGDECIMAL;
}

function getPnlPercentage(
  liquidityAtTrades: BigDecimal,
  pnlTotal: BigDecimal
): BigDecimal {
  if (liquidityAtTrades.gt(ZERO_BIGDECIMAL)) {
    return HUNDRED_BIGDECIMAL.times(pnlTotal).div(liquidityAtTrades);
  }
  return ZERO_BIGDECIMAL;
}

/*
This function is called when there is a change in a pools curveHash or criteriaSetHash.

This function is responsible for creating or loading the new template into the pool's template
field. It also changes the values in the old and new template to reflect the change in capital
and count of pools.
*/
function updateConfigPoolTemplate(
  pool: Pool,
  pastTemplate: Template | null,
  curveHash: string,
  criteriaSetHash: string,
  timestamp: BigInt
): void {
  // Case where the old template was null or different from the current settings
  log.info("Updating the pool {} with the following curve {} and criteria {}", [
    pool.id,
    curveHash,
    criteriaSetHash,
  ]);
  if (pastTemplate != null) {
    log.info("The pastTemplate id is {}", [pastTemplate.id]);
  } else {
    log.info(
      "Updating the configuration of a new pool, there is no pastTemplate",
      []
    );
  }
  if (
    pastTemplate == null ||
    pastTemplate.curve != curveHash ||
    pastTemplate.criteriaSet != criteriaSetHash
  ) {
    log.debug("Why the condition was true?", []);
    if (pastTemplate == null) {
      log.debug("pastTemplate == null", []);
    } else {
      if (pastTemplate.curve != curveHash) {
        log.debug("pastTemplate.curve != curveHash", []);
      }
      if (pastTemplate.criteriaSet != criteriaSetHash) {
        log.debug("pastTemplate.criteriaSet != criteriaSetHash", []);
      }
    }
    const templateId = createTemplateId(
      Bytes.fromHexString(curveHash) as Bytes,
      Bytes.fromHexString(criteriaSetHash) as Bytes
    );
    let template = Template.load(templateId);
    log.info("Loading the template {}", [templateId]);

    // If the template does not exist, create a new one
    if (template == null) {
      log.info("No template found, creating a new template", []);
      template = createTemplate(
        templateId,
        curveHash,
        criteriaSetHash,
        pool.lp
      );
    }
    // increment template's fields to represent the new pool joining.
    template.numPools = template.numPools.plus(ONE_BIGINT);
    template.size = template.size.plus(pool.size);
    template.save();
    // Set the pool to use the new / loaded template
    pool.template = template.id;

    // Change the values in the past template to account for the change in pool's template
    if (pastTemplate != null) {
      log.info(
        "Updating the pastTemplate {}, size was {} and numPools was {}",
        [
          pastTemplate.id,
          pastTemplate.size.toString(),
          pastTemplate.numPools.toString(),
        ]
      );
      pastTemplate.numPools = pastTemplate.numPools.minus(ONE_BIGINT);
      pastTemplate.size = pastTemplate.size.minus(pool.size);
      pastTemplate.save();
      log.info("Updated the pastTemplate {}, size is {} and numPools is {}", [
        pastTemplate.id,
        pastTemplate.size.toString(),
        pastTemplate.numPools.toString(),
      ]);
      createPoolSnapshot(
        pool,
        timestamp,
        ZERO_BIGDECIMAL,
        Actions.POOL_LEFT_TEMPLATE,
        pastTemplate.id,
        pastTemplate as Template
      );
    }
    pool.save();
  }
}

/**
 * Creates a Pool Snapshot entity, called when a pool is updated.
 * @param {Pool} pool Pool instance.
 * @param {BigInt} timestamp Timestamp of the transaction, epoch in seconds.
 * @param {BigDecimal} actionAmount Amount to increment or decrement the pool size
 * or locked by.
 * @param {string} actionType Enumerated action value.
 * @param {string} templateId The id of the template for which we are creating a snapshot
 */
export function createPoolSnapshot(
  pool: Pool,
  timestamp: BigInt,
  actionAmount: BigDecimal,
  actionType: Actions,
  templateId: string,
  template: Template
): void {
  const poolSnapshotId = createPoolSnapshotId(
    pool.lp,
    pool.poolId,
    templateId,
    timestamp
  );
  const poolSnapshot = new PoolSnapshot(poolSnapshotId);
  log.info("Creating Snapshot {} for Pool {}", [
    poolSnapshotId,
    pool.poolId.toString(),
  ]);
  log.info("Snapshot action info, amount: {}, type: {}", [
    actionAmount.toString(),
    actionType.toString(),
  ]);
  // log.info("This is the template you're passing, is it null??", [
  //   template.toString(),
  // ]);
  poolSnapshot.poolId = pool.poolId;
  poolSnapshot.lp = pool.lp;
  poolSnapshot.size = pool.size;
  poolSnapshot.locked = pool.locked;
  poolSnapshot.unlocked = pool.unlocked;
  poolSnapshot.utilization = pool.utilization;
  poolSnapshot.template = templateId;
  poolSnapshot.timestamp = timestamp;
  poolSnapshot.actionAmount = actionAmount;
  poolSnapshot.actionType = BigInt.fromI32(actionType);
  poolSnapshot.currentPool = pool.id;
  poolSnapshot.pnlTotal = pool.pnlTotal;
  poolSnapshot.pnlPercentage = pool.pnlPercentage;
  poolSnapshot.initialBalance = pool.initialBalance;
  poolSnapshot.liquidityAtTrades = pool.liquidityAtTrades;
  // Add also data from the template if it exists
  if (template != null) {
    poolSnapshot.templatePnlPercentage = template.pnlPercentage;
    poolSnapshot.templateSize = template.size;
    poolSnapshot.templateUtilization = template.utilization;
    poolSnapshot.templatePnlTotal = template.pnlTotal;
    poolSnapshot.templateLiquidityAtTrades = template.liquidityAtTrades;
  }

  poolSnapshot.save();
}

export function createPool(poolUUID: string, lp: Bytes, poolId: BigInt): Pool {
  const pool = new Pool(poolUUID);
  pool.locked = BigDecimal.fromString("0");
  pool.size = BigDecimal.fromString("0");
  pool.unlocked = BigDecimal.fromString("0");
  pool.utilization = BigDecimal.fromString("0");
  pool.pnlPercentage = BigDecimal.fromString("0");
  pool.lp = lp;
  pool.poolId = poolId;
  pool.pnlTotal = BigDecimal.fromString("0");
  pool.liquidityAtTrades = BigDecimal.fromString("0");
  return pool;
}

/**
 * Creates an OrderBookEntry from the buyer address, oToken address, and timestamp.
   Modifies Entities: OrderBookEntry
 * @param {Bytes} buyer The buyer's address.
 * @param {Bytes} otoken The oToken's address.
 * @param {BigDecimal} premium The premium paid by the buyer for oTokens purchased.
 * @param {BigDecimal} tokens The number of oTokens purchased by the buyer.
 * @param {BigInt} timestamp The timestamp of the block, given as an epoch in seconds.
 * @return {void}
 */
function createOrderBookEntry(
  buyer: Bytes,
  otoken: Bytes,
  premium: BigDecimal,
  tokens: BigDecimal,
  timestamp: BigInt
): void {
  const entryId =
    buyer.toHexString() + otoken.toHexString() + timestamp.toString();
  const entry = new OrderBookEntry(entryId);

  entry.buyer = buyer;
  // to set field to an entity, set to the string of the entity's ID.
  entry.otoken = getOTokenIdFromAddress(otoken);
  entry.premium = premium;
  entry.numberOfOTokens = tokens;
  entry.timestamp = timestamp;
  entry.save();
}

/**
 * Called when a Deposited event is emitted. Changes the size of the pool for the
 * deposit amount, or creates a new pool
 * @param {Deposited} event Descriptor of the event emitted.
 */
export function handleDeposited(event: Deposited): void {
  //Deposited(address indexed lp, uint256 indexed poolId, uint256 amount);
  const poolId = createPoolId(event.params.lp, event.params.poolId);
  const pool = Pool.load(poolId);
  const tokenAmount = collateralFixedtoDecimals(event.params.amount);
  if (pool) {
    pool.size = pool.size.plus(tokenAmount);
    pool.unlocked = pool.unlocked.plus(tokenAmount);

    // If this is the first deposit for the pool
    if (!pool.initialBalance) {
      pool.initialBalance = pool.size;
    }

    if (pool.template) {
      const template = Template.load(pool.template as string)!;
      template.size = template.size.plus(tokenAmount);
      template.save();
      if (template.curve) {
        pool.averageCost = calculateAverageCost(
          template.curve as string,
          pool.utilization,
          pool.locked,
          pool.size
        );
      }
      pool.save();

      createPoolSnapshot(
        pool as Pool,
        event.block.timestamp,
        tokenAmount,
        Actions.DEPOSIT,
        pool.template as string,
        template as Template
      );
    } else {
      log.warning("Deposited {} in the pool {} that doesn't have a template", [
        tokenAmount.toString(),
        poolId,
      ]);
      pool.save();
    }
  } else {
    log.error(
      "Tried to Deposit {} in a pool that doesn't exists, poolId was {}",
      [tokenAmount.toString(), poolId]
    );
  }
}

/**
 * Called when a Withdrawn event is emitted. Changes the size of the pool for the
 * amount removed.
 * @param {Withdrawn} event Descriptor of the event emitted.
 */
export function handleWithdrawn(event: Withdrawn): void {
  const poolId = createPoolId(event.params.lp, event.params.poolId);
  const pool = Pool.load(poolId);
  const withdrawalAmount = collateralFixedtoDecimals(event.params.amount);

  if (pool == null) {
    log.error(
      "Tried to Withdraw {} from a pool that doesn't exists, used the following lp {} and poolId {}",
      [
        withdrawalAmount.toString(),
        event.params.lp.toString(),
        event.params.poolId.toString(),
      ]
    );
  } else {
    if (pool.unlocked < withdrawalAmount) {
      log.error(
        "Tried to Withdraw {} from a pool that only has {} of unlocked liquidity, used the following lp {} and poolId {}",
        [
          withdrawalAmount.toString(),
          pool.unlocked.toString(),
          event.params.lp.toString(),
          event.params.poolId.toString(),
        ]
      );
    } else {
      pool.size = pool.size.minus(withdrawalAmount);
      pool.unlocked = pool.unlocked.minus(withdrawalAmount);

      if (pool.template) {
        const template = Template.load(pool.template as string)!;
        template.size = template.size.minus(withdrawalAmount);
        template.save();
        if (template.curve) {
          pool.averageCost = calculateAverageCost(
            template.curve as string,
            pool.utilization,
            pool.locked,
            pool.size
          );
        }
        pool.save();

        createPoolSnapshot(
          pool as Pool,
          event.block.timestamp,
          withdrawalAmount,
          Actions.WITHDRAW,
          pool.template as string,
          template as Template
        );
      } else {
        log.warning("Withdrawn {} from pool {} that is missing a template", [
          withdrawalAmount.toString(),
          poolId,
        ]);
        pool.save();
      }
    }
  }
}

/**
 * Called when a CriteriaSetSelected event is emitted. Changes the CriteriaSet
   for the pool and updates the template associated with the pool.
 * @param {CriteriaSetSelected} event Descriptor of the event emitted.
 */
export function handleCriteriaSetSelected(event: CriteriaSetSelected): void {
  const poolId = createPoolId(event.params.lp, event.params.poolId);
  let pool = Pool.load(poolId);
  if (pool == null) {
    pool = createPool(poolId, event.params.lp, event.params.poolId);
  }
  const criteriaSetHashId = event.params.criteriaSetHash.toHexString();
  log.info("Setting a criteria for {}, criteria hash id is {}", [
    poolId,
    criteriaSetHashId,
  ]);

  if (pool.template == null) {
    log.info("pool.template is null, creating a new template", []);
    updateConfigPoolTemplate(
      pool as Pool,
      null,
      "",
      criteriaSetHashId,
      event.block.timestamp
    );
  } else {
    const pastTemplate = Template.load(pool.template as string)!;
    if (pastTemplate.criteriaSet == null) {
      log.info("Pool already have the partial template {}, completing it", [
        pool.template as string,
      ]);
    }
    updateConfigPoolTemplate(
      pool as Pool,
      pastTemplate as Template,
      pastTemplate.curve as string,
      criteriaSetHashId,
      event.block.timestamp
    );
  }

  const template = Template.load(pool.template as string);
  createPoolSnapshot(
    pool as Pool,
    event.block.timestamp,
    BigDecimal.fromString("0"),
    Actions.CRITERIASET_CHANGE,
    pool.template as string,
    template as Template
  );
}

/**
 * Called when a CurveSelected event is emitted. Changes the Curve
   for the pool and updates the template associated with the pool.
 * @param {CurveSelected} event Descriptor of the event emitted.
 */
export function handleCurveSelected(event: CurveSelected): void {
  const poolId = createPoolId(event.params.lp, event.params.poolId);
  let pool = Pool.load(poolId);
  if (pool == null) {
    pool = createPool(poolId, event.params.lp, event.params.poolId);
  }
  const curveId = event.params.curveHash.toHexString();
  log.info("Setting a curve for {}, curve id is {}", [poolId, curveId]);

  if (pool.template == null) {
    log.info("pool.template is null, creating a new template", []);
    updateConfigPoolTemplate(
      pool as Pool,
      null,
      curveId,
      "",
      event.block.timestamp
    );
  } else {
    const pastTemplate = Template.load(pool.template as string)!;
    if (pastTemplate.curve == null) {
      log.info("Pool already have the partial template {}, completing it", [
        pool.template as string,
      ]);
    }
    updateConfigPoolTemplate(
      pool as Pool,
      pastTemplate as Template,
      curveId,
      pastTemplate.criteriaSet as string,
      event.block.timestamp
    );
  }

  pool.averageCost = calculateAverageCost(
    curveId,
    pool.utilization,
    pool.locked,
    pool.size
  );

  const template = Template.load(pool.template as string);
  createPoolSnapshot(
    pool as Pool,
    event.block.timestamp,
    BigDecimal.fromString("0"),
    Actions.CURVE_CHANGE,
    pool.template as string,
    template as Template
  );
}

/**
 * Called when a buyer purchases oTokens from at least one LP.
 * Updates the BuyerRecord based on the order.
 * Modifies Entities: BuyerRecord, OToken, OrderBookEntry.
 * @param {OptionsBought} event Data for OptionsBought event.
 * @return {void}
 */
export function handleOptionsBought(event: OptionsBought): void {
  const recordID =
    event.params.buyer.toHexString() + event.params.otoken.toHexString();
  let record = BuyerRecord.load(recordID);
  const tokenAmount = oTokenFixedtoDecimals(
    event.params.otoken,
    event.params.numberOfOtokens
  );
  const premiumPaid = collateralFixedtoDecimals(event.params.totalPremiumPaid);

  if (record == null) {
    const otokenAddress = getOTokenIdFromAddress(event.params.otoken);
    const otoken = OToken.load(otokenAddress)!;
    record = new BuyerRecord(recordID);
    record.buyer = event.params.buyer;
    record.otoken = otokenAddress;
    record.premium = BigDecimal.fromString("0");
    record.numberOfOTokens = BigDecimal.fromString("0");
    record.expiry = otoken.expiry;
  }
  record.premium = premiumPaid.plus(record.premium);
  record.numberOfOTokens = tokenAmount.plus(record.numberOfOTokens);
  record.save();

  oTokenIncrementPurchasesCount(event.params.otoken);
  createOrderBookEntry(
    event.params.buyer,
    event.params.otoken,
    premiumPaid,
    tokenAmount,
    event.block.timestamp
  );
}

/**
 * Called when a OptionsSold event is emitted. Modifies the locked amount of
   the pool, as well as updates the LPRecord and oToken entities.
 * @param {OptionsSold} event Descriptor of the event emitted.
 */
export function handleOptionsSold(event: OptionsSold): void {
  const poolId = createPoolId(event.params.lp, event.params.poolId);
  const pool = Pool.load(poolId);
  if (pool) {
    const tokenAmount = oTokenFixedtoDecimals(
      event.params.otoken,
      event.params.numberOfOtokens
    );
    const premiumAmount = collateralFixedtoDecimals(
      event.params.premiumReceived
    );
    const liquidityCollateralized = collateralFixedtoDecimals(
      event.params.liquidityCollateralized
    );

    // Updates the template to reflect the new liquidity, utilization and PnL
    const template = Template.load(pool.template as string);
    if (template) {
      template.size = template.size.plus(premiumAmount);
      template.pnlTotal = template.pnlTotal.plus(premiumAmount);
      template.liquidityAtTrades = template.liquidityAtTrades.plus(pool.size);
      template.locked = template.locked.plus(liquidityCollateralized);
      template.utilization = getUtilization(template.size, template.locked);
      template.save();
    }

    // Update the pool
    pool.liquidityAtTrades = pool.liquidityAtTrades.plus(pool.size);
    pool.locked = liquidityCollateralized.plus(pool.locked);
    pool.size = premiumAmount.plus(pool.size);
    pool.unlocked = pool.size.minus(pool.locked);
    pool.utilization = getUtilization(pool.size, pool.locked);
    pool.pnlTotal = pool.pnlTotal.plus(premiumAmount);

    if (template && template.curve) {
      pool.averageCost = calculateAverageCost(
        template.curve as string,
        pool.utilization,
        pool.locked,
        pool.size
      );
    }
    pool.save();

    createPoolSnapshot(
      pool as Pool,
      event.block.timestamp,
      premiumAmount,
      Actions.PREMIUM_RECEIVED,
      pool.template as string,
      template as Template
    );

    const recordID = createLPRecordID(event.params.lp, event.params.otoken);
    let record = LPRecord.load(recordID);
    if (record == null) {
      record = new LPRecord(recordID);
      record.lp = event.params.lp;
      record.otoken = getOTokenIdFromAddress(event.params.otoken);
      record.numberOfOTokens = BigDecimal.fromString("0");
      record.liquidityCollateralized = BigDecimal.fromString("0");
      record.premiumReceived = BigDecimal.fromString("0");
    }
    record.premiumReceived = record.premiumReceived.plus(premiumAmount);
    record.liquidityCollateralized = record.liquidityCollateralized.plus(
      liquidityCollateralized
    );
    record.numberOfOTokens = record.numberOfOTokens.plus(tokenAmount);

    const poolRecordID = createPoolRecordID(
      event.params.lp,
      event.params.poolId,
      event.params.otoken
    );
    let poolRecord = PoolRecord.load(poolRecordID);

    if (poolRecord == null) {
      // The oToken (and record) has not received liquidity from this pool
      poolRecord = new PoolRecord(poolRecordID);
      poolRecord.pool = poolId;
      poolRecord.lpRecord = record.id;
      poolRecord.otoken = getOTokenIdFromAddress(event.params.otoken);
      poolRecord.collateral = liquidityCollateralized;
      poolRecord.premiumReceived = premiumAmount;
      poolRecord.numberOfOTokens = tokenAmount;
      poolRecord.save();
    } else {
      // Liquidity has been added from this pool, just change the poolRecord object.
      poolRecord.collateral = poolRecord.collateral.plus(
        liquidityCollateralized
      );
      poolRecord.premiumReceived =
        poolRecord.premiumReceived.plus(premiumAmount);
      poolRecord.numberOfOTokens = poolRecord.numberOfOTokens.plus(tokenAmount);
      poolRecord.save();
    }
    record.save();

    oTokenIncrementLiquidity(
      event.params.otoken,
      event.params.numberOfOtokens,
      event.params.liquidityCollateralized,
      event.params.premiumReceived
    );
  }
}

/**
 * Called when a OptionSettlementDistributed event is emitted. Modifies the locked and size
   fields of the pool. This returns unclaimed collateral from the oToken to the pool.
 * @param {OptionSettlementDistributed} event Descriptor of the event emitted.
 */
export function handleOptionSettlementDistributed(
  event: OptionSettlementDistributed
): void {
  const recordID = createLPRecordID(event.params.lp, event.params.otoken);
  const record = LPRecord.load(recordID);

  if (record) {
    const collateralReturned = collateralFixedtoDecimals(
      event.params.collateralReturned
    );
    record.liquidityCollateralized =
      record.liquidityCollateralized.minus(collateralReturned);

    record.save();

    const poolId = createPoolId(event.params.lp, event.params.poolId);
    const pool = Pool.load(poolId)!;

    const poolRecordID = createPoolRecordID(
      event.params.lp,
      event.params.poolId,
      event.params.otoken
    );
    const poolRecord = PoolRecord.load(poolRecordID)!;
    poolRecord.returned = collateralReturned;
    poolRecord.save();

    const poolTotalCollateralized: BigDecimal = poolRecord.collateral;
    const deltaCollateralizedAndReturned: BigDecimal =
      poolTotalCollateralized.minus(collateralReturned);

    // Updates the template to reflect the new liquidity, utilization and PnL
    const template = Template.load(pool.template as string)!;
    template.size = template.size.minus(deltaCollateralizedAndReturned);
    template.locked = template.locked.minus(poolTotalCollateralized);
    template.utilization = getUtilization(template.size, template.locked);
    template.pnlTotal = template.pnlTotal.minus(deltaCollateralizedAndReturned);
    template.pnlPercentage = getPnlPercentage(
      template.liquidityAtTrades,
      template.pnlTotal
    );
    template.save();

    // Update the pool
    pool.size = pool.size.minus(deltaCollateralizedAndReturned);
    pool.locked = pool.locked.minus(poolTotalCollateralized);
    pool.unlocked = pool.size.minus(pool.locked);
    pool.utilization = getUtilization(pool.size, pool.locked);
    pool.pnlTotal = pool.pnlTotal.minus(deltaCollateralizedAndReturned);
    pool.pnlPercentage = getPnlPercentage(
      pool.liquidityAtTrades,
      pool.pnlTotal
    );

    if (template.curve) {
      pool.averageCost = calculateAverageCost(
        template.curve as string,
        pool.utilization,
        pool.locked,
        pool.size
      );
    }

    pool.save();

    createPoolSnapshot(
      pool as Pool,
      event.block.timestamp,
      deltaCollateralizedAndReturned,
      Actions.CAPITAL_EXERCISED,
      pool.template as string,
      template as Template
    );
  }
}

/**
 * Called when a OptionSettled event is emitted. This happens when an
   oToken is settled.
 * @param {OptionSettled} event Descriptor of the event emitted.
 */
export function handleOptionsSettled(event: OptionSettled): void {
  oTokenSettled(event.params.otoken, event.params.collateralReturned);
}
