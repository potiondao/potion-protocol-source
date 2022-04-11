import { Pools } from "@/services/api/pools";
import { contractsAddresses } from "@/services/contracts";
import { custom } from "./custom";
import { erc20Allowance } from "@/services/contracts/erc20";
import { existing } from "./existing";
import { user } from "./user";

const state = {
  underlyingsAvailable: [],
  slippage: "0.5",
};
const getters = {
  underlyingsAvailable: (state) => state.underlyingsAvailable,
  currentSlippage: (state) => state.slippage,
};
const actions = {
  selectSlippage({ commit }, slippage) {
    commit("setSlippage", slippage);
  },
  async approvePotionBuy({ dispatch, rootState }, { amount }) {
    const allowance = await erc20Allowance(
      6,
      contractsAddresses.collateralTokenAddress,
      rootState.wallet.address,
      contractsAddresses.potionLiquidityPoolAddress
    );
    if (parseFloat(amount) > 0 && parseFloat(allowance) < amount) {
      await dispatch(
        "wallet/requestApprovalForSpending",
        {
          contractAddress: contractsAddresses.potionLiquidityPoolAddress,
          amount: amount,
          formatRequired: true,
        },
        {
          root: true,
        }
      );
    }
  },
  async getAvailableUniqueUnderlyings({ commit, dispatch }) {
    const callback = async () => {
      const response = await Pools.getProductsUSDCCollateral();
      commit("setUnderlyingsAvailable", response);
    };
    const errorMessage = "Error while getting the available underlyings";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
};

const mutations = {
  setSlippage(state, payload) {
    state.slippage = payload;
  },
  setUnderlyingsAvailable(state, payload) {
    payload.forEach((asset) => {
      asset.image =
        "https://s.gravatar.com/avatar/da32ff79613d46d206a45e5a3018acf3?size=496&default=retro";
    });
    state.underlyingsAvailable = payload;
  },
};

export const potions = {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
  modules: {
    existing,
    custom,
    user,
  },
};
