import {
  CurveCriteria,
  HyperbolicCurve,
  OrderedCriteria,
} from "potion-contracts/scripts/lib/typeHelpers";
import { PotionLiquidityPool__factory } from "potion-contracts/typechain/factories/PotionLiquidityPool__factory";

import { contractsAddresses } from "@/services/contracts";
import { initProvider } from "@/services/ethers";
import { getAccounts } from "@/services/metamask";
import {
  Criteria,
  CurveParams,
  PoolIdentifier,
  PoolRecord,
  PoolRecordIdentifier,
} from "@/types";
import { BigNumber } from "@ethersproject/bignumber";
import { ContractTransaction } from "@ethersproject/contracts";
import { parseUnits } from "@ethersproject/units";

import { Pools } from "../api/pools";

const formatCollateral = (amount: number): BigNumber => {
  return parseUnits(amount.toFixed(6), 6);
};
const collateralToReadable = (amount: number): number => amount / 10 ** 6;

const createCurve = (params: CurveParams): HyperbolicCurve => {
  return new HyperbolicCurve(
    parseFloat(params["a"]),
    parseFloat(params["b"]),
    parseFloat(params["c"]),
    parseFloat(params["d"]),
    parseFloat(params["maxUtil"])
  );
};

const createCriteria = (criteria: Criteria): CurveCriteria =>
  new CurveCriteria(
    criteria.address,
    contractsAddresses.collateralTokenAddress,
    true,
    parseFloat(criteria.strike),
    parseInt(criteria.duration)
  );

const createOrderedCriterias = (criterias: CurveCriteria[]): CurveCriteria[] =>
  OrderedCriteria.from(criterias);

/**
 *
 * @param depositAmount amount to deposit in number, not formatted
 * @param curveParams
 * @param criterias
 * @param poolId
 * @returns a string with the cost in gas units
 */
const estimateSavePool = async (
  depositAmount: number,
  curveParams: CurveParams,
  criterias: Criteria[],
  poolId: number
): Promise<string> => {
  const curve = createCurve(curveParams);
  const curveCriterias = criterias.map(createCriteria);
  const orderedCriteria = createOrderedCriterias(curveCriterias);
  const provider = await initProvider();

  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider
  );

  const gasUnits =
    await PotionContract.estimateGas.depositAndCreateCurveAndCriteria(
      poolId,
      formatCollateral(depositAmount),
      curve.asSolidityStruct(),
      orderedCriteria
    );
  return gasUnits.toString();
};

/**
 *
 * @param depositAmount
 * @param curveParams
 * @param criterias
 * @param poolId
 * @returns this method runs the 'depositAndCreateCurveAndCriteria' method from the potionLiquidityPool smartcontract
 */
const savePool = async (
  depositAmount: number,
  curveParams: CurveParams,
  criterias: Criteria[],
  poolId: number
): Promise<ContractTransaction> => {
  const curve = createCurve(curveParams);
  const curveCriterias = criterias.map(createCriteria);
  const orderedCriteria = createOrderedCriterias(curveCriterias);

  /**
   * @todo do we want to inform the user if he's deploying an existing curve/criteriaset?
   */
  const provider = await initProvider();

  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  return PotionContract.depositAndCreateCurveAndCriteria(
    poolId,
    formatCollateral(depositAmount),
    curve.asSolidityStruct(),
    orderedCriteria
  );
};

/**
 *
 * @param depositAmount
 * @param curveParams
 * @param criterias
 * @returns wrap for the savePool() function
 */
const createNewPool = async (
  depositAmount: number,
  curveParams: CurveParams,
  criterias: Criteria[]
): Promise<ContractTransaction> => {
  try {
    const poolId = (await Pools.getNumberOfPools((await getAccounts())[0])) + 1;
    return await savePool(depositAmount, curveParams, criterias, poolId);
  } catch (error) {
    throw new Error("Error in the pool creation");
  }
};

/**
 *
 * @param depositAmount
 * @param curveParams
 * @param criterias
 * @param poolId
 * @returns wrap for the savePool() - accept a poolId that points to the pool to be edited
 */
const editPool = async (
  depositAmount: number,
  curveParams: CurveParams,
  criterias: Criteria[],
  poolId: number
): Promise<ContractTransaction> => {
  try {
    return await savePool(depositAmount, curveParams, criterias, poolId);
  } catch (error) {
    throw new Error("Error while trying to edit the pool");
  }
};

/**
 *
 * @param poolId
 * @param depositAmount
 * @returns gas estimation method for the collateral deposit interaction
 */
const estimateDepositCollateral = async (
  poolId: number,
  depositAmount: number
): Promise<string> => {
  const provider = await initProvider();
  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  const gasUnits = await PotionContract.estimateGas.deposit(
    poolId,
    formatCollateral(depositAmount)
  );
  return gasUnits.toString();
};

/**
 *
 * @param poolId
 * @param depositAmount
 * @returns this triggers the deposit method from the potionLiquidityPool smart contract
 */
const depositCollateral = async (
  poolId: number,
  depositAmount: number
): Promise<ContractTransaction> => {
  const provider = await initProvider();
  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );

  return PotionContract.deposit(poolId, formatCollateral(depositAmount));
};

/**
 *
 * @param poolId
 * @param withdrawAmount
 * @returns gas estimation for the withdraw method of the potionLiquidityPool smart contract
 */
const estimateWithdrawCollateral = async (
  poolId: number,
  withdrawAmount: number
): Promise<string> => {
  const provider = await initProvider();

  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  const gasUnits = await PotionContract.estimateGas.withdraw(
    poolId,
    formatCollateral(withdrawAmount)
  );
  return gasUnits.toString();
};

/**
 *
 * @param poolId
 * @param withdrawAmount
 * @returns this triggers the withdraw method from the potionLiquidityPool smart contract
 */
const withdrawCollateral = async (
  poolId: number,
  withdrawAmount: number
): Promise<ContractTransaction> => {
  const provider = await initProvider();

  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  return PotionContract.withdraw(poolId, formatCollateral(withdrawAmount));
};

/**
 *
 * @param oTokenAddress
 * @param poolIdentifierObject
 * @returns Total settlement for an oToken and given LP's pool
 */
const oTokenCreditForPool = async (
  oTokenAddress: string,
  poolIdentifierObject: PoolIdentifier
): Promise<number> => {
  const provider = await initProvider();
  const PotionContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider
  );
  const refund = await PotionContract.outstandingSettlement(
    oTokenAddress,
    poolIdentifierObject
  );

  return refund.toNumber();
};

/**
 *
 * @param poolRecords
 * @returns This returns a map made by the poolRecordID and his reclaimable value
 */
const totalCredit = async (poolRecords: PoolRecord[]): Promise<{}> => {
  const result = {};
  await Promise.all(
    poolRecords.map(async (item) => {
      const refund = await oTokenCreditForPool(item.lpRecord.otoken.id, {
        lp: item.lpRecord.lp,
        poolId: item.pool.poolId,
      });
      result[item.id] = collateralToReadable(refund);
    })
  );
  return result;
};

/**
 *
 * @param poolRecords
 * @returns it conditionally settle the collateral and redistribute it for every lp's pool
 */
const reclaimCollateralFromPoolRecord = async (
  poolRecords: PoolRecordIdentifier[]
): Promise<ContractTransaction> => {
  const poolsParam = poolRecords.map((pool) => {
    return {
      lp: pool.lp,
      poolId: pool.poolId,
    };
  });
  try {
    const provider = await initProvider();
    const PotionContract = PotionLiquidityPool__factory.connect(
      contractsAddresses.potionLiquidityPoolAddress,
      provider.getSigner()
    );

    const otokenAddress = poolRecords[0].otokenAddress;
    const isSettled = await PotionContract.isSettled(otokenAddress);

    if (!isSettled) {
      const settleTransaction = await PotionContract.settleAfterExpiry(
        otokenAddress
      );
      await settleTransaction.wait();
      return await PotionContract.redistributeSettlement(
        otokenAddress,
        poolsParam
      );
    }
    return PotionContract.redistributeSettlement(otokenAddress, poolsParam);
  } catch (error) {
    throw new Error("Error reclaiming");
  }
};

export {
  createNewPool,
  editPool,
  depositCollateral,
  withdrawCollateral,
  formatCollateral,
  createCurve,
  totalCredit,
  reclaimCollateralFromPoolRecord,
  estimateSavePool,
  estimateWithdrawCollateral,
  estimateDepositCollateral,
};
