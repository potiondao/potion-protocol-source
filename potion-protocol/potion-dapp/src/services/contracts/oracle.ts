import { BigNumber } from "@ethersproject/bignumber";
import { formatUnits } from "@ethersproject/units";
import { initProvider } from "@/services/ethers";

import { contractsAddresses } from "@/services/contracts";
import { AddressBook__factory } from "potion-contracts/typechain/factories/AddressBook__factory";
import { Oracle__factory } from "potion-contracts/typechain/factories/Oracle__factory";

/**
 *
 * @param underlyingAddress an erc20 token address
 * @param underlyingDecimals the decimals for that token
 * @returns the price for that token from the oracle
 */
export const getPriceFromOracle = async (
  underlyingAddress: string,
  underlyingDecimals = "8"
): Promise<string> => {
  const provider = await initProvider();
  const addressBookContract = AddressBook__factory.connect(
    contractsAddresses.opynAddressBookAddress,
    provider
  );

  const oracleAddress = await addressBookContract.getOracle();

  const oracleContract = Oracle__factory.connect(oracleAddress, provider);
  const price = await oracleContract.getPrice(underlyingAddress);

  return formatUnits(
    BigNumber.from(price).toString(),
    parseFloat(underlyingDecimals)
  );
};
