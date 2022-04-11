import {
  Web3Provider,
  Network,
  BlockTag,
  Block,
} from "@ethersproject/providers";
import { checkProvider, getAccounts } from "@/services/metamask";

import { contractsAddresses } from "@/services/contracts";
import { erc20Balance } from "@/services/contracts/erc20";
import { formatUnits } from "@ethersproject/units";
import { isAddress } from "@ethersproject/address";

/**
 * @returns a new instance of a Web3Provider used to fetch blockchain data
 */
async function initProvider(): Promise<Web3Provider> {
  const provider = await checkProvider();
  return new Web3Provider(provider);
}

/**
 *
 * @param block BlockTag interface, ex: "latest"
 * @returns a Block
 */
const getBlock = async (block?: BlockTag): Promise<Block> => {
  try {
    const provider = await initProvider();
    return await provider.getBlock(block);
  } catch (error) {
    throw new Error(error);
  }
};

/**
 *
 * @returns the block gas limit
 */
const getBlockGasLimit = async (): Promise<string> => {
  try {
    const provider = await initProvider();
    return await (await provider.getBlock("latest")).gasLimit.toString();
  } catch (error) {
    throw new Error(error);
  }
};

/**
 *
 * @param walletAddress a valid wallet address
 * @returns eth balance as a string in ETH - ex: 1.337
 */
const getEthBalance = async (walletAddress: string): Promise<string> => {
  try {
    const provider = await initProvider();
    const response = await provider.getBalance(walletAddress);
    return formatUnits(response);
  } catch (error) {
    throw new Error(error);
  }
};

/**
 *
 * @returns the latest block timestamp
 */
const getLatestBlockTimestamp = async (): Promise<number> => {
  return (await getBlock("latest")).timestamp;
};

/**
 *
 * @param walletAddress a valid wallet address
 * @returns the collateral token balance for that address
 */
const getCollateralBalance = async (walletAddress: string): Promise<string> => {
  try {
    const balance = await erc20Balance(
      walletAddress,
      contractsAddresses.collateralTokenAddress
    );
    return formatUnits(balance, 6);
  } catch (error) {
    throw new Error(error);
  }
};

/**
 *
 * @returns a Network object
 */
const getNetwork = async (): Promise<Network> => {
  try {
    const provider = await initProvider();
    return await provider.getNetwork();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error getting the network");
    }
  }
};

/**
 *
 * @param walletAddress Wallet address as string
 * @returns Returns an ENS domain associated to the wallet or a wallet address
 */
const lookupAddress = async (walletAddress: string): Promise<string> => {
  try {
    if (isAddress(walletAddress)) {
      const provider = await initProvider();
      const network = await getNetwork();
      if (network.chainId !== 1) {
        return walletAddress;
      } else {
        const ENS = await provider.lookupAddress(walletAddress);
        if (ENS !== null) {
          return ENS;
        } else {
          return walletAddress;
        }
      }
    } else {
      return walletAddress;
    }
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error getting the ENS name");
    }
  }
};

/**
 *
 * @param tokenAddress an oToken address
 * @returns otoken balance formatted like 1.666
 */
const getOTokenBalance = async (tokenAddress: string): Promise<string> => {
  const walletAddress = (await getAccounts())[0];
  const balance = await erc20Balance(walletAddress, tokenAddress);
  return formatUnits(balance, 8);
};

const chainIdToName = {
  "0x1": "mainnet",
  "0x3": "ropsten",
  "0x4": "rinkeby",
  "0x5": "goerli",
  "0x2a": "kovan",
};

export {
  getBlock,
  getBlockGasLimit,
  getLatestBlockTimestamp,
  getCollateralBalance,
  getOTokenBalance,
  initProvider,
  chainIdToName,
  lookupAddress,
  getEthBalance,
};
