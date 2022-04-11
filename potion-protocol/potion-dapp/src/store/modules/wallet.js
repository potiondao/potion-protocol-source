import {
  getEthBalance as _getEthBalance,
  getCollateralBalance,
  lookupAddress,
} from "../../services/ethers";
import {
  checkProvider,
  getAccounts,
  requestAccounts,
} from "../../services/metamask";
import { erc20Approval, erc20Symbol } from "@/services/contracts/erc20";

import { contractsAddresses } from "@/services/contracts";
import { getEtherscanLink } from "@/helpers";

const metamaskErrorToast = {
  title: "Metamask Error",
  subtitle: "Check your Metamask extension",
  etherscanLink: null,
  icon: "wallet",
};

const metamaskMissingToast = {
  title: "Metamask not found",
  subtitle: "It seems that you don't have Metamask installed",
  etherscanLink: null,
  icon: "wallet",
};

const state = {
  provider: null,
  address: null,
  ens: null,
  ethBalance: null,
  usdcBalance: null,
  collateralBalances: null,
  collateralBalance: null,
  stableCoinCollateral:
    process.env.VUE_APP_ETH_NETWORK === "ganache" ? "PUSDC" : "USDC",
  collateralAddress: contractsAddresses.collateralTokenAddress,
};
const getters = {
  metamaskInstalled: (state) => state.provider !== null,
  connectedToMetamask: (state) => typeof state.address === "string",
  walletAddress: (state) => {
    return state.address;
  },
  ens: (state) => {
    return state.ens;
  },
  stableCoinCollateral: (state) => state.stableCoinCollateral,
  stableCoinCollateralBalance: (state) => state.collateralBalance || "0",
};
const mutations = {
  setEns(state, payload) {
    state.ens = payload;
  },
  setProvider(state, payload) {
    state.provider = payload;
  },
  setAddress(state, payload) {
    state.address = payload;
  },
  setEthBalance(state, payload) {
    state.ethBalance = payload;
  },
  setCollateralBalances(state, payload) {
    state.collateralBalances = payload;
  },
  setCollateralBalance(state, payload) {
    state.collateralBalance = payload;
  },
  setCollateralSymbol(state, payload) {
    state.stableCoinCollateral = payload;
  },
};
const actions = {
  setChangedAccount({ commit }, payload) {
    commit("setAddress", payload);
  },
  async providerErrorToast({ dispatch }) {
    dispatch("showToast", metamaskErrorToast, { root: true });
  },
  async providerMissingToast({ dispatch }) {
    dispatch("showToast", metamaskMissingToast, { root: true });
  },
  async checkProvider({ commit, dispatch }) {
    try {
      const response = await checkProvider();
      commit("setProvider", response);
    } catch (error) {
      dispatch("providerErrorToast");
      throw error;
    }
  },
  async getAccounts({ commit, dispatch }) {
    try {
      const response = await getAccounts();
      commit("setAddress", response[0]);
      const ens = await lookupAddress(response[0]);
      commit("setEns", ens);
    } catch (error) {
      dispatch("providerErrorToast");
      throw error;
    }
  },
  async requestApprovalForSpending(
    { dispatch, state },
    { contractAddress, amount, formatRequired = false }
  ) {
    const callback = async () => {
      const transaction = await erc20Approval(
        state.collateralAddress,
        contractAddress,
        amount,
        formatRequired
      );
      dispatch(
        "showToast",
        {
          title: "Waiting for Approval",
          subtitle: `You are approving to spend ${amount}`,
          etherscanLink: getEtherscanLink(transaction.hash),
        },
        { root: true }
      );
      const receipt = await transaction.wait();
      if (receipt.status) {
        dispatch(
          "showToast",
          {
            title: "Transaction Approved",
            subtitle: `You approved spending ${amount} .`,
            etherscanLink: getEtherscanLink(transaction.hash),
          },
          { root: true }
        );
      }
    };
    const errorMessage = "Approval error";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async requestAccounts({ commit, dispatch }) {
    try {
      const response = await requestAccounts();
      commit("setAddress", response[0]);
      const ens = await lookupAddress(response[0]);
      commit("setEns", ens);
    } catch (error) {
      dispatch("providerErrorToast");
      throw error;
    }
  },
  async connectToMetamask({ dispatch, getters }) {
    if (!getters.connectedToMetamask) {
      try {
        await dispatch("checkProvider");
        await dispatch("getAccounts");
        await dispatch("requestAccounts");
      } catch (error) {
        dispatch("providerErrorToast");
        throw error;
      }
    }
  },
  async getEthBalance({ commit, dispatch }, wallet) {
    const callback = async () => {
      const response = await _getEthBalance(wallet);
      commit("setEthBalance", response);
    };
    const errorMessage = `Error getting the ETH balance for wallet ${wallet}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getCollateralBalance({ commit, dispatch }, wallet) {
    const callback = async () => {
      const response = await getCollateralBalance(wallet);
      commit("setCollateralBalance", response);
    };
    const errorMessage = `Error getting the collateral balance for wallet ${wallet}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getCollateralSymbol({ commit, state }) {
    const symbol = await erc20Symbol(state.collateralAddress);
    commit("setCollateralSymbol", symbol);
  },
};

export const wallet = {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
