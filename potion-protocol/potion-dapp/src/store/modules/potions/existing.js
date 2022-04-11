import { each as _each, get as _get } from "lodash-es";
import { buyOToken, buyOTokenOverflow } from "@/services/contracts/potions";

import { Potions } from "@/services/api/potions";
import { Router } from "@/services/api/router";
import { dateToOffset } from "@/helpers";
import { estimateBuyOtoken } from "@/services/contracts/potions";
import { getEtherscanLink } from "@/helpers";
import { getPriceFromOracle } from "@/services/contracts/oracle";
import { runWorkerRouter } from "@/services/router/worker.worker";

const state = {
  selectedPotion: {
    quantity: "0",
    underlying: {
      name: null,
      symbol: null,
      address: null,
      image: null,
      price: null,
    },
    oToken: {
      address: null,
      strikePrice: null,
      expirationUnix: null,
      orderHistory: [],
    },
    router: {
      premiumTotal: 0,
      counterparties: [],
      pools: [],
      marketDepth: "0",
      maxNumberOfOtokens: "0",
      gasUnits: "0",
    },
  },
  statusBarOpened: false,
  popularPotions: {},
  popularPotionsCanLoadMore: {
    mostPurchased: false,
    mostCollateralized: false,
  },
};

const paginator = 6;

const getters = {
  gasUnits: (state) => state.selectedPotion.router.gasUnits,
  transactionsNumber: (state, _, rootState) => {
    if (state.selectedPotion.router.counterparties.length > 0) {
      return Math.ceil(
        state.selectedPotion.router.counterparties.length /
          rootState.maxCounterparties
      );
    } else return 0;
  },
  maxNumberOfOtokens: (state) => state.selectedPotion.router.maxNumberOfOtokens,
  mostPurchased: (state) =>
    _get(state, ["popularPotions", "mostPurchased"], []),
  mostCollateralized: (state) =>
    _get(state, ["popularPotions", "mostCollateralized"], []),
  mostPurchasedCanLoadMore: (state) =>
    _get(state, ["popularPotionsCanLoadMore", "mostPurchased"], []),
  mostCollateralizedCanLoadMore: (state) =>
    _get(state, ["popularPotionsCanLoadMore", "mostCollateralized"], []),
  strikePriceRelativeSelected: (state) => {
    const strikePrice = parseFloat(state.selectedPotion.oToken.strikePrice);
    const underlyingPrice = parseFloat(state.selectedPotion.underlying.price);
    if (strikePrice && underlyingPrice) {
      return ((100 * strikePrice) / underlyingPrice).toString();
    }
    return "0";
  },
  orderSize: (state) => {
    return (
      parseFloat(state.selectedPotion.oToken.strikePrice) *
      parseFloat(state.selectedPotion.quantity)
    );
  },
  premiumPerPotion: (state) => {
    if (parseFloat(state.selectedPotion.router.premiumTotal.toFixed(6)) > 0) {
      return (
        parseFloat(state.selectedPotion.router.premiumTotal) /
        parseFloat(state.selectedPotion.quantity)
      );
    } else {
      return "Select a quantity";
    }
  },
  premium: (state) => {
    if (parseFloat(state.selectedPotion.router.premiumTotal.toFixed(6)) > 0) {
      return state.selectedPotion.router.premiumTotal;
    } else {
      return "Select a quantity";
    }
  },
  statusBarOpened: (state) => state.statusBarOpened,
  selectedPotion: (state) => state.selectedPotion,
};

const actions = {
  async getPotions({ commit, dispatch, rootGetters }) {
    const callback = async () => {
      await dispatch("getBlockEpoch", null, { root: true });
      const availableTokens = await Potions.getAvailableUniqueUnderlyings();
      const addresses = availableTokens.map((v) => v.address);
      const popularPotions = await Potions.getMostPopular(
        rootGetters.blockEpoch,
        addresses,
        paginator
      );
      commit("setPopularPotions", popularPotions);
      _each(popularPotions, (potions, key) => {
        commit("setPopularPotionsCanLoadMore", {
          key,
          value: potions.length >= paginator,
        });
      });
    };
    const errorMessage = "Error while fetching the potions";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async loadMorePotions(
    { commit, dispatch, getters, rootGetters },
    filteringMode
  ) {
    const filteringModeToData = {
      mostPurchased: getters.mostPurchased.map((item) => item.id),
      mostCollateralized: getters.mostCollateralized.map((item) => item.id),
    };
    const callback = async () => {
      const alreadyLoadedIds = filteringModeToData[filteringMode];
      await dispatch("getBlockEpoch", null, { root: true });
      const availableTokens = await Potions.getAvailableUniqueUnderlyings();
      const addresses = availableTokens.map((v) => v.address);
      const potions = await Potions.loadMorePopularPotions(
        rootGetters.blockEpoch,
        filteringMode,
        alreadyLoadedIds,
        addresses,
        paginator
      );
      commit("prependPopularPotions", { key: filteringMode, potions });
      commit("setPopularPotionsCanLoadMore", {
        key: filteringMode,
        value: potions.length >= paginator,
      });
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async selectPotion({ commit }, data) {
    commit("setSelectedPotion", data);
    const orders = await Potions.getOrders(data.oToken.id);
    commit("setOrders", orders);
  },
  toggleStatusBar({ commit }) {
    commit("toggleStatusBar");
  },
  async getPriceFromOracle({ commit, dispatch }, tokenAddress) {
    const callback = async () => {
      const response = await getPriceFromOracle(tokenAddress);
      commit("setUnderlyingPrice", response);
    };
    const errorMessage =
      "Error while getting the price of the asset from the Oracle";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getPoolsFromUnderlying({
    dispatch,
    commit,
    state,
    getters,
    rootGetters,
  }) {
    try {
      await dispatch("getBlockEpoch", null, { root: true });
      const pools = await Router.getPoolsFromCriteria(
        state.selectedPotion.underlying.address,
        getters.strikePriceRelativeSelected,
        dateToOffset(
          rootGetters.blockEpoch,
          state.selectedPotion.oToken.expirationUnix
        )
      );
      commit("setPoolsFromCriteria", pools);
      commit("calculateMarketDepth");
    } catch (error) {
      throw new Error(error);
    }
  },
  async runRouter(
    { commit, state, dispatch },
    { orderSize, gasInWei, ethPrice }
  ) {
    const callback = async () => {
      const { premium, counterparties } = await runWorkerRouter(
        state.selectedPotion.router.pools,
        orderSize,
        parseFloat(state.selectedPotion.oToken.strikePrice),
        gasInWei,
        ethPrice
      );
      commit("setRouterData", { premium, counterparties });
    };
    const errorMessage = "Failed to run the router";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
    await dispatch("estimateGas");
  },
  async estimateGas({ state, dispatch, commit }) {
    const callback = async () => {
      let gasUnits = 0;
      if (state.selectedPotion.router.counterparties.length <= 100) {
        gasUnits = await estimateBuyOtoken(
          state.selectedPotion.oToken.address,
          state.selectedPotion.router.counterparties,
          100000000
        );
      } else {
        gasUnits = 10562685;
      }

      commit("setGasEstimation", gasUnits);
    };
    const errorMessage = "Couldn't estimate gas";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async buyPotions({ state, dispatch, rootGetters }) {
    const maxPremium = parseFloat(
      (
        state.selectedPotion.router.premiumTotal *
        (1 + parseFloat(rootGetters["potions/currentSlippage"]) / 100)
      ).toFixed(6)
    );
    let callback = null;
    if (
      state.selectedPotion.router.counterparties.length >=
      rootGetters["maxCounterparties"]
    ) {
      callback = async () => {
        await buyOTokenOverflow(
          state.selectedPotion.oToken.address,
          state.selectedPotion.router.counterparties,
          maxPremium,
          rootGetters["maxCounterparties"]
        );
        dispatch(
          "showToast",
          {
            title: "Waiting for creation!",
            subtitle: `You will need to sign ${Math.ceil(
              state.selectedPotion.router.counterparties.length /
                rootGetters["maxCounterparties"]
            )} transactions now`,
          },
          { root: true }
        );
      };
    } else {
      callback = async () => {
        const transaction = await buyOToken(
          state.selectedPotion.oToken.address,
          state.selectedPotion.router.counterparties,
          maxPremium
        );
        dispatch(
          "showToast",
          {
            title: "Waiting for creation!",
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
                    title: "Your new Potion is ready",
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
    }

    const errorMessage = "Error while trying to buy the Potion";
    await dispatch(
      "potions/approvePotionBuy",
      { amount: maxPremium },
      { root: true }
    );
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async openPurchaseModal({ dispatch }, potion) {
    await dispatch("selectPotion", potion);
    await dispatch("getPriceFromOracle", potion.underlying.address);
    await dispatch("getPoolsFromUnderlying");
    dispatch("toggleStatusBar");
  },
  updateQuantity({ commit }, data) {
    commit("setQuantity", data);
  },
};

const mutations = {
  setGasEstimation(state, payload) {
    state.selectedPotion.router.gasUnits = payload;
  },
  calculateMarketDepth(state) {
    state.selectedPotion.router.marketDepth = state.selectedPotion.router.pools
      .reduce((sum, pool) => {
        return sum + parseFloat(pool.unlocked);
      }, 0)
      .toString();
    state.selectedPotion.router.maxNumberOfOtokens =
      parseFloat(state.selectedPotion.router.marketDepth) /
      parseFloat(state.selectedPotion.oToken.strikePrice);
  },
  setPoolsFromCriteria(state, payload) {
    state.selectedPotion.router.pools = payload;
  },
  setRouterData(state, payload) {
    state.selectedPotion.router.premiumTotal = payload.premium;
    state.selectedPotion.router.counterparties = payload.counterparties;
  },
  setPopularPotions(state, payload) {
    state.popularPotions = { ...state.popularPotions, ...payload };
  },
  prependPopularPotions(state, { key, potions }) {
    potions.forEach((potion) => state.popularPotions[key].unshift(potion));
  },
  setPopularPotionsCanLoadMore(state, { key, value }) {
    state.popularPotionsCanLoadMore[key] = value;
  },
  setSelectedPotion(state, payload) {
    state.selectedPotion.underlying = payload.underlying;
    state.selectedPotion.oToken = payload.oToken;
  },
  toggleStatusBar(state) {
    state.statusBarOpened = !state.statusBarOpened;
    if (state.statusBarOpened === false) {
      state.selectedPotion.quantity = "0";
      state.selectedPotion.router.premiumTotal = 0;
      state.selectedPotion.router.counterparties = [];
      state.selectedPotion.router.pools = [];
      state.selectedPotion.router.marketDepth = "0";
      state.selectedPotion.router.maxNumberOfOtokens = "0";
      state.selectedPotion.router.gasUnits = "0";
    }
  },
  setUnderlyingPrice(state, payload) {
    state.selectedPotion.underlying.price = payload;
  },
  setQuantity(state, payload) {
    state.selectedPotion.quantity = payload;
  },
  setRouterPremium(state, payload) {
    state.selectedPotion.router.premiumTotal = payload;
  },
  setCounterparties(state, payload) {
    state.selectedPotion.router.counterparties = payload;
  },
  setOrders(state, payload) {
    state.selectedPotion.oToken.orderHistory = payload;
  },
};

export const existing = {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
