import { BigNumberish, BigNumber } from "@ethersproject/bignumber";
import { formatUnits } from "@ethersproject/units";
import { ERC20Upgradeable__factory } from "potion-contracts/typechain/factories/ERC20Upgradeable__factory";
import { initProvider } from "@/services/ethers";
import { ContractTransaction } from "@ethersproject/contracts";

const formatCollateral = (amount: number) => amount * 10 ** 6;

/**
 *
 * @param tokenUnits token digits in number
 * @param tokenAddress token address
 * @param owner address of the owner
 * @param spender address of the spender
 * @returns the allowance for a specific token on a specific contract
 */
const erc20Allowance = async (
  tokenUnits: number,
  tokenAddress: string,
  owner: string,
  spender: string
): Promise<string> => {
  const provider = await initProvider();
  const ERC20 = ERC20Upgradeable__factory.connect(
    tokenAddress,
    provider.getSigner()
  );
  try {
    const response = await ERC20.allowance(owner, spender);
    return formatUnits(response, tokenUnits);
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Error getting the allowance");
    }
  }
};

/**
 *
 * @param tokenAddress erc20 address
 * @param contractAddress contract to interact with
 * @param amount amount to spend
 * @param formatRequired if a format is required for the amount
 * @returns a ContractTransaction for the approval of the spending
 */
const erc20Approval = async (
  tokenAddress: string,
  contractAddress: string,
  amount: BigNumberish,
  formatRequired = true
): Promise<ContractTransaction> => {
  const provider = await initProvider();
  const ERC20 = ERC20Upgradeable__factory.connect(
    tokenAddress,
    provider.getSigner()
  );

  return ERC20.approve(
    contractAddress,
    formatRequired ? formatCollateral(amount as number) : amount
  );
};

/**
 *
 * @param tokenAddress a valid erc20 address
 * @returns the symbol for that token
 */
const erc20Symbol = async (tokenAddress: string): Promise<string> => {
  const provider = await initProvider();
  const ERC20 = ERC20Upgradeable__factory.connect(tokenAddress, provider);
  return await ERC20.symbol();
};

/**
 *
 * @param walletAddress a valid wallet address
 * @param tokenAddress a valid erc20 address
 * @returns the balance as a BigNumber for the given token of the given address
 */
const erc20Balance = async (
  walletAddress: string,
  tokenAddress: string
): Promise<BigNumber> => {
  const provider = await initProvider();
  const ERC20 = ERC20Upgradeable__factory.connect(tokenAddress, provider);
  return await ERC20.balanceOf(walletAddress);
};

export { erc20Allowance, erc20Approval, erc20Balance, erc20Symbol };
