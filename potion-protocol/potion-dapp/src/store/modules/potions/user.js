import { each as _each, map as _map, sum as _sum } from "lodash-es";
import {
  getPayouts,
  getPrices,
  getRedeemed,
} from "@/services/contracts/potions";

import { MyPotions } from "@/services/api/myPotions";
import { getEtherscanLink } from "@/helpers";
import { redeemOToken } from "@/services/contracts/potions";

const paginator = 6;
const state = {
  activePotions: [],
  activeCanLoadMore: false,
  expiredPotions: [],
  expiredCanLoadMore: false,
  priceMap: {},
  payoutMap: {},
  redeemedMap: {},
};

const getters = {
  activePotions: (state) => state.activePotions,
  activeCanLoadMore: (state) => state.activeCanLoadMore,
  expiredPotions: (state) => state.expiredPotions,
  expiredCanLoadMore: (state) => state.expiredCanLoadMore,
  currentPrices: (state) => state.priceMap,
  payouts: (state) => state.payoutMap,
  redeemed: (state) => state.redeemedMap,
  unredeemedPayouts: (_, getters) => {
    const map = {};
    _each(getters.redeemed, (redeemed, id) => {
      if (!redeemed) {
        map[id] = getters.payouts[id] || "0";
      }
    });
    return map;
  },
  availablePayout: (_, getters) =>
    _sum(_map(getters.unredeemedPayouts, parseFloat)).toString(),
};

// Actions that shouldn't be called outside the store
// They are actions only to have a more structured format
const internals = {
  async getPriceMapping({ commit }, potions) {
    try {
      const mapping = await getPrices(potions);
      commit("setPriceMap", mapping);
    } catch (error) {
      throw new Error(error);
    }
  },
  async getPayouts({ commit, getters }, { activePotions, expiredPotions }) {
    try {
      commit(
        "setPayoutMap",
        await getPayouts(activePotions, expiredPotions, getters.currentPrices)
      );
    } catch (error) {
      throw new Error(error);
    }
  },
  async getRedeemedBalance({ commit, getters }) {
    try {
      commit("setRedeemedMap", await getRedeemed(getters.expiredPotions));
    } catch (error) {
      throw new Error(error);
    }
  },
};

const actions = {
  async getUserPotions({ commit, dispatch, rootGetters }, walletAddress) {
    const callback = async () => {
      const { activePotions, expiredPotions } = await MyPotions.getUserPotions(
        walletAddress,
        rootGetters.blockEpoch,
        paginator
      );
      commit("setActivePotions", activePotions);
      commit("setExpiredPotions", expiredPotions);
      commit("setActiveLoadMore", activePotions.length >= paginator);
      commit("setExpiredLoadMore", expiredPotions.length >= paginator);
      dispatch("getPrices", { activePotions, expiredPotions });
    };
    const errorMessage = `Error while fetching the potions for walletAddress ${walletAddress}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getMoreActivePotions(
    { commit, dispatch, getters, rootGetters },
    walletAddress
  ) {
    const callback = async () => {
      let alreadyLoadedIds = getters.activePotions.map((x) => x.id);

      const activePotions = await MyPotions.getActivePotions(
        walletAddress,
        rootGetters.blockEpoch,
        paginator,
        alreadyLoadedIds
      );
      commit("setMoreActivePotions", activePotions);
      commit("setActiveLoadMore", activePotions.length >= paginator);
      dispatch("getPrices", { activePotions });
    };
    const errorMessage = `Error while fetching the potions for walletAddress ${walletAddress}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getMoreExpiredPotions(
    { commit, dispatch, getters, rootGetters },
    walletAddress
  ) {
    const callback = async () => {
      let alreadyLoadedIds = getters.expiredPotions.map((x) => x.id);

      const expiredPotions = await MyPotions.getExpiredPotions(
        walletAddress,
        rootGetters.blockEpoch,
        paginator,
        alreadyLoadedIds
      );
      commit("setMoreExpiredPotions", expiredPotions);
      commit("setExpiredLoadMore", expiredPotions.length >= paginator);
      dispatch("getPrices", { expiredPotions });
    };
    const errorMessage = `Error while fetching the potions for walletAddress ${walletAddress}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },

  async getPrices({ dispatch }, { activePotions = [], expiredPotions = [] }) {
    const callback = async () => {
      await dispatch("getBlockEpoch", null, { root: true });
      await dispatch("getPriceMapping", activePotions.concat(expiredPotions));
      await dispatch("getPayouts", { activePotions, expiredPotions });
      await dispatch("getRedeemedBalance");
    };
    const errorMessage = "Error while getting the potions prices";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async redeemOToken({ dispatch, rootState }, { address, quantity }) {
    const callback = async () => {
      const transaction = await redeemOToken(
        address,
        quantity,
        rootState.wallet.address
      );
      dispatch(
        "showToast",
        {
          title: "Redeeming Potion",
          subtitle: "Check the status on etherscan",
          etherscanLink: getEtherscanLink(transaction.hash),
        },
        { root: true }
      );
      await dispatch(
        "runWithLoader",
        {
          callback: async () => {
            const receipt = await transaction.wait();
            if (receipt.status) {
              dispatch(
                "showToast",
                {
                  title: "Succesfully redeemed!",
                  subtitle: "You can see the transaction on etherscan",
                  etherscanLink: getEtherscanLink(transaction.hash),
                },
                { root: true }
              );
            }
          },
          errorMessage: "",
        },
        { root: true }
      );
    };
    const errorMessage = "Error while trying to redeem the Potion";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  ...internals,
};

const mutations = {
  setActiveLoadMore(state, payload) {
    state.activeCanLoadMore = payload;
  },
  setExpiredLoadMore(state, payload) {
    state.expiredCanLoadMore = payload;
  },
  setMoreActivePotions(state, payload) {
    state.activePotions = state.activePotions.concat(payload);
  },
  setActivePotions(state, payload) {
    state.activePotions = payload;
  },
  setMoreExpiredPotions(state, payload) {
    state.expiredPotions = state.expiredPotions.concat(payload);
  },
  setExpiredPotions(state, payload) {
    state.expiredPotions = payload;
  },
  setPriceMap(state, payload) {
    state.priceMap = { ...state.priceMap, ...payload };
  },
  setPayoutMap(state, payload) {
    state.payoutMap = { ...state.payoutMap, ...payload };
  },
  setRedeemedMap(state, payload) {
    state.redeemedMap = { ...state.redeemedMap, ...payload };
  },
};

export const user = {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
