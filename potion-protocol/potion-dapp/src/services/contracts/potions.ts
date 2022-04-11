import { AddressBook__factory } from "potion-contracts/typechain/factories/AddressBook__factory";
import { ControllerInterface__factory } from "potion-contracts/typechain/factories/ControllerInterface__factory";
import { OtokenFactoryInterface__factory } from "potion-contracts/typechain/factories/OtokenFactoryInterface__factory";
import { OtokenFactory__factory } from "potion-contracts/typechain/factories/OtokenFactory__factory";
import { PotionLiquidityPool__factory } from "potion-contracts/typechain/factories/PotionLiquidityPool__factory";
import type { CounterpartyDetails, ICriteria, IPotions } from "@/types";
import {
  getLatestBlockTimestamp,
  getBlock,
  initProvider,
} from "@/services/ethers";
import { chunk as _chunk, map as _map } from "lodash-es";
import { formatUnits, parseUnits } from "@ethersproject/units";

import { ContractTransaction } from "@ethersproject/contracts";
import { MaxUint256 } from "@ethersproject/constants";
import { contractsAddresses } from "@/services/contracts";
import dayjs from "dayjs";
import { getAccounts } from "@/services/metamask";
import { getOTokenBalance } from "@/services/ethers";
import { getUnderlyingsPriceMap } from "@/helpers";

const REDEEM_ACTION_OPCODE = 8;
const COLLATERAL_DECIMALS = 10 ** 6;
const SECONDS_TO_8AM = 28800;
const SECONDS_IN_DAY = 86400;

const setup = async (tokenAmount: string) => {
  const provider = await initProvider();
  const amount = parseUnits(tokenAmount, 8);
  const rawAmount = amount.toString();
  const addressBookContract = AddressBook__factory.connect(
    contractsAddresses.opynAddressBookAddress,
    provider.getSigner()
  );
  const controllerAddress = await addressBookContract.getController();
  const controllerContract = ControllerInterface__factory.connect(
    controllerAddress,
    provider.getSigner()
  );
  return {
    rawAmount,
    controllerContract,
  };
};

const redeemOToken = async (
  oTokenAddress: string,
  tokenAmount: string,
  buyerAddress: string
) => {
  const { rawAmount, controllerContract } = await setup(tokenAmount);
  const buyerVault = await controllerContract.getAccountVaultCounter(
    buyerAddress
  );

  const redeemArgs = [
    {
      actionType: REDEEM_ACTION_OPCODE,
      owner: buyerAddress,
      secondAddress: buyerAddress,
      asset: oTokenAddress,
      vaultId: buyerVault.toString(),
      amount: rawAmount,
      index: "0",
      data: "0x0000000000000000000000000000000000000000",
    },
  ];
  return await controllerContract.operate(redeemArgs);
};

const getPayout = async (
  oTokenAddress: string,
  tokenAmount: string
): Promise<string> => {
  try {
    const { rawAmount, controllerContract } = await setup(tokenAmount);

    const payout = await controllerContract.getPayout(oTokenAddress, rawAmount);
    return payout.div(COLLATERAL_DECIMALS).toString();
  } catch (error) {
    return "0";
  }
};

const getDurationsFromStrike = async (
  criterias: ICriteria[],
  underlyingAddress: string,
  strike: string
): Promise<string[]> => {
  const block = await getBlock();
  // Convert block timestamp in epoch time (seconds) to milliseconds
  const blockTimestamp = block.timestamp * 1000;

  let filteredCriterias = [];
  // Strike could be unset, if null select all criterias
  if (strike) {
    // Find criterias that match the same strike price as the
    // one that is selected.
    filteredCriterias = criterias.filter((criteria) => {
      return (
        criteria.underlyingAsset.id.toLowerCase() ==
          underlyingAddress.toLowerCase() && criteria.stylizedStrike === strike
      );
    });
  } else {
    // null case
    filteredCriterias = criterias;
  }

  for (const criteria of filteredCriterias) {
    const days: number = parseInt(criteria.maxDurationInDays);
    criteria.endDate = dayjs(blockTimestamp)
      .add(days, "day")
      .format("MM-DD-YYYY");
  }

  let endDates: string[] = filteredCriterias.map((item) => item.endDate);
  endDates = endDates.sort((a: string, b: string) =>
    dayjs(a).isAfter(dayjs(b)) ? 1 : -1
  );
  return endDates;
};

/*
 * Returns a expiry epoch timestamp that is described by:
 * now + number of days, at 8AM UTC.
 */
const createValidExpiry = (now: number, days: number): number => {
  const multiplier = (now - SECONDS_TO_8AM) / SECONDS_IN_DAY;
  return (
    Number(multiplier.toFixed(0)) * SECONDS_IN_DAY +
    days * SECONDS_IN_DAY +
    SECONDS_TO_8AM
  );
};

const oTokenExsists = async (
  underlyingAddress: string,
  strike: string,
  validExpiry
): Promise<{
  exists: boolean;
  address: string;
}> => {
  const provider = await initProvider();
  const otokenFactoryContract = OtokenFactoryInterface__factory.connect(
    contractsAddresses.otokenFactoryAddress,
    provider.getSigner()
  );

  const newOTokenAddress = await otokenFactoryContract.getTargetOtokenAddress(
    underlyingAddress,
    contractsAddresses.collateralTokenAddress,
    contractsAddresses.collateralTokenAddress,
    parseUnits(strike, 8),
    validExpiry,
    true
  );

  const exists = await otokenFactoryContract.getOtoken(
    underlyingAddress,
    contractsAddresses.collateralTokenAddress,
    contractsAddresses.collateralTokenAddress,
    parseUnits(strike, 8),
    validExpiry,
    true
  );

  return {
    exists: newOTokenAddress === exists,
    address: newOTokenAddress,
  };
};

/**
 *
 * @param oTokenAddress a valid otoken address
 * @param counterparties an array of counterparties to buy from
 * @param maxPremium the max premium the user is willing to pay
 * @returns a contract transaction.
 */
const buyOToken = async (
  oTokenAddress: string,
  counterparties: CounterpartyDetails[],
  maxPremium: number
) => {
  const provider = await initProvider();
  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  return await potionLiquidityPoolContract.buyOtokens(
    oTokenAddress,
    counterparties,
    parseUnits(maxPremium.toFixed(6), 6)
  );
};

/**
 *
 * @param oTokenAddress a valid otoken address
 * @param counterparties an array of counterparties to buy from
 * @param maxPremium the max premium the user is willing to pay
 * @param maxCounterparties the max number of counterparties allowed per transaction
 *
 * this method is used to split the buy in multiple transactions, based on the maximum amount of counterparties
 * this way we do not hit the block gas limit
 */
const buyOTokenOverflow = async (
  oTokenAddress: string,
  counterparties: CounterpartyDetails[],
  maxPremium: number,
  maxCounterparties: number
) => {
  const provider = await initProvider();
  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  const contractInterface = potionLiquidityPoolContract.interface;

  const cpChunks = _chunk(counterparties, maxCounterparties);
  let newMaxPremium = 0;
  for (const chunk of cpChunks) {
    const receipt = await (
      await potionLiquidityPoolContract.buyOtokens(
        oTokenAddress,
        chunk,
        parseUnits((maxPremium - newMaxPremium).toFixed(6), 6)
      )
    ).wait();

    const log = contractInterface.parseLog(
      receipt.logs[receipt.logs.length - 1]
    );
    newMaxPremium = newMaxPremium + parseFloat(formatUnits(log.args[3], 6));
  }
};

/**
 *
 * @param underlyingAddress the underlying token address for the otoken
 * @param strike the strike token address for the otoken
 * @param duration otoken expiry date
 * @param counterparties an array of counterparties to buy from
 * @param maxPremium the max amount of premium the user is willing to pay
 * @param maxCounterparties the max number of counterparties allowed per transaction
 *
 * this method is used to split the buy in multiple transactions, based on the maximum amount of counterparties
 * this way we do not hit the block gas limit
 */
const deployAndBuyFromOtokenOverflow = async (
  underlyingAddress: string,
  strike: string,
  duration: string,
  counterparties: CounterpartyDetails[],
  maxPremium: number,
  maxCounterparties: number
) => {
  const provider = await initProvider();
  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  const contractInterface = potionLiquidityPoolContract.interface;

  const now = await getLatestBlockTimestamp();
  const validExpiry = createValidExpiry(now, parseInt(duration));

  const cpChunks = _chunk(counterparties, maxCounterparties);

  const { exists, address } = await oTokenExsists(
    underlyingAddress,
    strike,
    validExpiry
  );
  if (exists) {
    let newMaxPremium = 0;

    for (const chunk of cpChunks) {
      const receipt = await (
        await buyOToken(
          address,
          chunk,
          parseFloat((maxPremium - newMaxPremium).toFixed(6))
        )
      ).wait();

      const log = contractInterface.parseLog(
        receipt.logs[receipt.logs.length - 1]
      );
      newMaxPremium = newMaxPremium + parseFloat(formatUnits(log.args[3], 6));
    }
  } else {
    let newMaxPremium = 0;
    const receipt = await (
      await potionLiquidityPoolContract.createAndBuyOtokens(
        underlyingAddress.toLowerCase(),
        contractsAddresses.collateralTokenAddress.toLowerCase(),
        contractsAddresses.collateralTokenAddress.toLowerCase(),
        parseUnits(strike, 8),
        validExpiry,
        true,
        cpChunks[0],
        parseUnits((maxPremium - newMaxPremium).toFixed(6), 6)
      )
    ).wait();
    const log = contractInterface.parseLog(
      receipt.logs[receipt.logs.length - 1]
    );
    newMaxPremium = newMaxPremium + parseFloat(formatUnits(log.args[3], 6));

    const { exists, address } = await oTokenExsists(
      underlyingAddress,
      strike,
      validExpiry
    );
    if (exists) {
      for (let index = 1; index < cpChunks.length; index++) {
        const receipt = await (
          await buyOToken(
            address,
            cpChunks[index],
            parseFloat((maxPremium - newMaxPremium).toFixed(6))
          )
        ).wait();
        const log = contractInterface.parseLog(
          receipt.logs[receipt.logs.length - 1]
        );

        newMaxPremium = newMaxPremium + parseFloat(formatUnits(log.args[3], 6));
      }
    }
  }
};

/**
 *
 * @param underlyingAddress the underlying token address for the otoken
 * @param strike the strike token address for the otoken
 * @param duration otoken expiry date
 * @param counterparties an array of counterparties to buy from
 * @param maxPremium the max amount of premium the user is willing to pay
 * @returns a transaction for the otoken creation. This method will check if the otoken already exists based on the params passed.
 */
const deployAndBuyFromOToken = async (
  underlyingAddress: string,
  strike: string,
  duration: string,
  counterparties: CounterpartyDetails[],
  maxPremium: number
): Promise<ContractTransaction> => {
  const provider = await initProvider();
  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );

  const now = await getLatestBlockTimestamp();
  const validExpiry = createValidExpiry(now, parseInt(duration));

  const { exists, address } = await oTokenExsists(
    underlyingAddress,
    strike,
    validExpiry
  );

  if (!exists) {
    return await potionLiquidityPoolContract.createAndBuyOtokens(
      underlyingAddress.toLowerCase(),
      contractsAddresses.collateralTokenAddress.toLowerCase(),
      contractsAddresses.collateralTokenAddress.toLowerCase(),
      parseUnits(strike, 8),
      validExpiry,
      true,
      counterparties,
      parseUnits(maxPremium.toFixed(6), 6)
    );
  } else {
    return await buyOToken(address, counterparties, maxPremium);
  }
};

/**
 *
 * @param oTokenAddress
 * @param counterparties
 * @param maxPremium
 * @returns the gas units for the "buyOtokens" transaction
 */
const estimateBuyOtoken = async (
  oTokenAddress: string,
  counterparties: CounterpartyDetails[],
  maxPremium: number
) => {
  const provider = await initProvider();
  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );
  const gasUnits = await potionLiquidityPoolContract.estimateGas.buyOtokens(
    oTokenAddress,
    counterparties,
    parseUnits(maxPremium.toFixed(6), 6)
  );

  return gasUnits.toString();
};

/**
 *
 * @param underlyingAddress
 * @param strike
 * @param duration
 * @param counterparties
 * @returns the gas units for the "createAndBuyOtokens" or "buyOtokens" transaction
 */
const estimateDeployAndBuyFromOtoken = async (
  underlyingAddress: string,
  strike: string,
  duration: string,
  counterparties: CounterpartyDetails[]
) => {
  const provider = await initProvider();

  const potionLiquidityPoolContract = PotionLiquidityPool__factory.connect(
    contractsAddresses.potionLiquidityPoolAddress,
    provider.getSigner()
  );

  const now = await getLatestBlockTimestamp();

  const validExpiry = createValidExpiry(now, parseInt(duration));

  const { exists, address } = await oTokenExsists(
    underlyingAddress,
    strike,
    validExpiry
  );

  if (!exists) {
    const gasUnits =
      await potionLiquidityPoolContract.estimateGas.createAndBuyOtokens(
        underlyingAddress.toLowerCase(),
        contractsAddresses.collateralTokenAddress.toLowerCase(),
        contractsAddresses.collateralTokenAddress.toLowerCase(),
        parseUnits(strike, 8),
        validExpiry,
        true,
        counterparties,
        MaxUint256
      );
    return gasUnits.toString();
  } else {
    const gasUnits = await potionLiquidityPoolContract.estimateGas.buyOtokens(
      address,
      counterparties,
      MaxUint256
    );
    return gasUnits.toString();
  }
};

/**
 *
 * @param potions
 * @param decimals
 * @returns Retrieves the pricing of the underlying asset of a potion from the oracle
 */
const getPrices = async (potions: IPotions[], decimals = 8) =>
  getUnderlyingsPriceMap(
    _map(potions, (p) => p.otoken.underlyingAsset),
    decimals
  );

const formatPrice = (price: number, strike: number, tokens: number): string =>
  price < strike ? ((strike - price) * tokens).toString() : "0";

/**
 *
 * @param activePotions
 * @param expiredPotions
 * @param prices
 * @returns retrieve the payout value of every potion
 * If the potion is active, it will try to estimate the payout
 * If the potion is expired it will retrieve the payout from the blockchain
 */
const getPayouts = async (
  activePotions: IPotions[],
  expiredPotions: IPotions[],
  prices: { [price: string]: string }
) => {
  const map = {};
  activePotions.forEach((potion) => {
    const id = potion.otoken.id;
    const underlying = potion.otoken.underlyingAsset;
    const underlyingPrice = prices[underlying.address];

    map[id] = formatPrice(
      parseFloat(underlyingPrice),
      parseFloat(potion.otoken.strikePrice),
      parseFloat(potion.numberOfOTokens)
    );
  });

  for (const potion of expiredPotions) {
    const id = potion.otoken.id;
    const payout = await getPayout(id, potion.numberOfOTokens);
    map[id] = payout ? payout : "0";
  }

  return map;
};

/**
 *
 * @param potions
 * @returns return the redeem status of an array of potions
 */
const getRedeemed = async (potions: IPotions[]) => {
  const map = {};
  for (const potion of potions) {
    // If the token balance is greater than 0, then capital from the oToken has not been redeemed yet, so it can be withdrawn.
    map[potion.otoken.id] =
      parseFloat(await getOTokenBalance(potion.otoken.id)) <= 0;
  }
  return map;
};

export {
  buyOToken,
  deployAndBuyFromOToken,
  getDurationsFromStrike,
  getPayout,
  oTokenExsists,
  redeemOToken,
  deployAndBuyFromOtokenOverflow,
  estimateDeployAndBuyFromOtoken,
  estimateBuyOtoken,
  getPrices,
  getPayouts,
  getRedeemed,
  buyOTokenOverflow,
};
