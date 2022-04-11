import detectEthereumProvider from "@metamask/detect-provider";
import { ExternalProvider } from "@ethersproject/providers";

/* This returns the provider (window.ethereum) OR an error */
const checkProvider = async (): Promise<ExternalProvider> => {
  try {
    const provider = (await detectEthereumProvider({
      mustBeMetaMask: true,
    })) as ExternalProvider;
    if (provider !== null) {
      return provider;
    }
    throw new Error("Error getting your Wallet");
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error getting your wallet");
    }
  }
};

/**
 * @returns an Error or a log - an array of accounts if we have a provider.
 * for now, the array will be empty if we do not have the permissions from the user or
 * have one item if we have the permission
 */
const getAccounts = async (): Promise<string[]> => {
  try {
    const provider = await checkProvider();
    return await provider.request?.({
      method: "eth_accounts",
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error trying to get your accounts[s]");
    }
  }
};

/**
 * It fire up the wallet access request or return the array of account(s)
 */
const requestAccounts = async (): Promise<string[]> => {
  try {
    const provider = await checkProvider();
    return await provider.request?.({
      method: "eth_requestAccounts",
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error during the dApp approval");
    }
  }
};

/**
 * This method add a custom ERC20 asset to the wallet
 * @param type
 * @param address address of the asset to add to the wallet
 * @param symbol symbol for the custom ERC20
 * @param decimals decimals for the custom ERC20
 * @returns true or false based on the esit
 */
const watchAsset = async (
  type = "ERC20",
  address: string,
  symbol: string,
  decimals: number
) => {
  try {
    const metamask = await checkProvider();
    await metamask.request({
      method: "wallet_watchAsset",
      params: {
        //@ts-expect-error
        type: type,
        options: {
          address: address,
          symbol: symbol,
          decimals: decimals,
          image: "https://potion.fi/favicon.png",
        },
      },
    });
    return true;
  } catch (error) {
    throw new Error(error);
  }
};

export { checkProvider, getAccounts, requestAccounts, watchAsset };
