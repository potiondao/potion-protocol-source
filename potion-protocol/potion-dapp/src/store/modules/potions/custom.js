import {
  isEmpty as _isEmpty,
  isFinite as _isFinite,
  last as _last,
} from "lodash-es";
import {
  deployAndBuyFromOToken,
  deployAndBuyFromOtokenOverflow,
} from "@/services/contracts/potions";

import { Potions } from "@/services/api/potions";
import { Router } from "@/services/api/router";
import dayjs from "dayjs";
import { estimateDeployAndBuyFromOtoken } from "@/services/contracts/potions";
import { getEtherscanLink } from "@/helpers";
import { getPriceFromOracle } from "@/services/contracts/oracle";
import { offsetToDate } from "@/helpers";
import router from "../../../routes";
import { runWorkerRouter } from "@/services/router/worker.worker";

const state = {
  step: 0,
  quantity: null,
  underlyingSelected: {
    name: null,
    symbol: null,
    address: null,
    image: null,
    price: null,
  },
  strike: {
    priceSelected: null,
    priceRelativeMax: null,
  },
  duration: {
    daysSelected: null,
    daysMax: null,
  },
  router: {
    premiumTotal: 0,
    counterparties: [],
    pools: [],
    marketDepth: "0",
    maxNumberOfOtokens: "0",
    gasUnits: "0",
  },
  similars: {
    toggle: false,
    potions: [],
  },
};
const getters = {
  underlyingSelected: (state) => state.underlyingSelected,
  transactionsNumber: (state, _, rootState) => {
    if (state.router.counterparties.length > 0) {
      return Math.ceil(
        state.router.counterparties.length / rootState.maxCounterparties
      );
    } else return 0;
  },
  maxNumberOfOtokens: (state) => state.router.maxNumberOfOtokens,
  currentStep: (state) => state.step,
  suggestedPotions: (state) => state.similars.potions,
  getGasUnits: (state) => {
    return state.router.gasUnits;
  },
  strikePriceRelativeSelected: (state) => {
    const relative = parseFloat(state.strike.priceSelected);
    const price = parseFloat(state.underlyingSelected.price);
    if (relative && price) {
      return ((relative * 100) / price).toString();
    }
    return "0";
  },
  strikePriceMax: (state) => {
    const relative = state.strike.priceRelativeMax;
    const price = parseFloat(state.underlyingSelected.price);
    if (relative && price) {
      return ((relative * price) / 100).toString();
    }
    return "0";
  },
  orderSize: (state) => {
    return parseFloat(state.strike.priceSelected) * parseFloat(state.quantity);
  },
  durationDaysMaxDate: (state, _, _1, rootGetters) => {
    return offsetToDate(rootGetters.blockEpoch, state.duration.daysMax);
  },
  durationDaysSelectedDate: (state, _, _1, rootGetters) => {
    return offsetToDate(rootGetters.blockEpoch, state.duration.daysSelected);
  },
  premium: (state) => {
    if (parseFloat(state.router.premiumTotal.toFixed(6)) > 0) {
      return state.router.premiumTotal;
    } else {
      return "Select a quantity";
    }
  },
  premiumPerPotion: (state) => {
    if (parseFloat(state.router.premiumTotal.toFixed(6)) > 0) {
      return state.router.premiumTotal / parseFloat(state.quantity);
    } else {
      return "Select a quantity";
    }
  },
  validUnderlying: (state) =>
    [state.underlyingSelected.address, state.underlyingSelected.symbol].every(
      (x) => !_isEmpty(x)
    ),
  validStrikePrice: (state, getters) =>
    parseFloat(state.strike.priceSelected) <=
      parseFloat(getters.strikePriceMax) &&
    parseFloat(state.strike.priceSelected) > 0,
  validDurationInDays: (state) =>
    parseFloat(state.duration.daysSelected) <=
      parseFloat(state.duration.daysMax) &&
    parseFloat(state.duration.daysSelected) > 0,
  validQuantity: (state) => {
    return parseFloat(state.quantity) <=
      parseFloat(state.router.maxNumberOfOtokens) &&
      parseFloat(state.quantity) >= 0.00000001
      ? true
      : false;
  },
  validPremium: (state) => {
    return parseFloat(state.router.premiumTotal.toFixed(6)) > 0;
  },
  validCustomData: (_, getters) => {
    return [
      getters.validUnderlying,
      getters.validStrikePrice,
      getters.validDurationInDays,
      getters.validQuantity,
      getters.validPremium,
    ].every((x) => x);
  },

  stepsEnabled: (_, getters) => {
    const steps = [true];
    [
      getters.validUnderlying,
      getters.validStrikePrice,
      getters.validDurationInDays,
      getters.validCustomData,
    ].forEach((step) => {
      steps.push(_last(steps) && step);
    });
    return steps;
  },
};

const actions = {
  async getPriceFromOracle({ dispatch, commit }, tokenAddress) {
    const callback = async () => {
      const response = await getPriceFromOracle(tokenAddress);
      commit("setCurrentPrice", response);
    };
    const errorMessage =
      "Error while getting the price of the asset from the Oracle";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getMaxStrikeFromUnderlying({ commit, dispatch }, underlying) {
    const callback = async () => {
      const response = await Potions.getMaxStrikeFromUnderlying(underlying);
      commit("setMaxStrike", response);
    };
    const errorMessage = `Error while getting the maximum available strike from underlying ${underlying}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getMaxDurationFromStrike({ commit, dispatch }, { underlying, strike }) {
    const callback = async () => {
      const response = await Potions.getMaxDurationFromStrike(
        underlying,
        strike
      );
      commit("setMaxDuration", response);
    };
    const errorMessage = `Error while getting the maximum duration for underlying ${underlying} with strike ${strike}`;
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  selectStep({ commit }, data) {
    commit("setStep", data);
  },
  selectUnderlying({ commit }, data) {
    commit("setUnderlyingSelected", data);
  },
  /* mode is one between ['asset', 'strike', 'duration'] = enum if we refactor everything with Typescript */
  async getSimilarPotions({ commit, state, dispatch, rootGetters }, mode) {
    await dispatch("getBlockEpoch", null, { root: true });
    const params = {
      addresses: [state.underlyingSelected.address],
      expiry: rootGetters.blockEpoch,
    };
    if (["asset"].includes(mode)) {
      params["assetPrice"] = parseFloat(state.underlyingSelected.price);
    }
    if (["strike", "duration"].includes(mode)) {
      params["strikePrice"] = parseFloat(state.strike.priceSelected);
    }
    if (["duration"].includes(mode)) {
      params["duration"] = dayjs
        .unix(rootGetters.blockEpoch)
        .add(state.duration.daysSelected, "day")
        .unix();
    }
    commit("setSimilarPotions", await Potions.getSimilarPotions(params, mode));
  },
  selectStrike({ commit }, strikePrice) {
    commit("setStrikeSelected", strikePrice);
  },
  selectDuration({ commit }, duration) {
    commit("setDurationSelected", duration);
  },
  async getPoolsFromUnderlying({ commit, state, getters, dispatch }) {
    const callback = async () => {
      const pools = await Router.getPoolsFromCriteria(
        state.underlyingSelected.address,
        getters.strikePriceRelativeSelected,
        state.duration.daysSelected
      );
      commit("setPoolsFromCriteria", pools);
      commit("calculateMarketDepth");
    };
    const errorMessage = "Failed to get pools from the subgraph";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async runRouter(
    { commit, state, dispatch },
    { orderSize, gasInWei, ethPrice }
  ) {
    const callback = async () => {
      const { premium, counterparties } = await runWorkerRouter(
        state.router.pools,
        orderSize,
        parseFloat(state.strike.priceSelected),
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
      if (state.router.counterparties.length <= 100) {
        gasUnits = await estimateDeployAndBuyFromOtoken(
          state.underlyingSelected.address,
          parseFloat(state.strike.priceSelected).toFixed(8),
          parseInt(state.duration.daysSelected),
          state.router.counterparties
        );
      } else {
        gasUnits = 10562685;
      }

      commit("setGasEstimation", gasUnits);
    };
    const errorMessage = "Couldn't estimate gas";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  toggleSimilars({ commit }, status) {
    commit("toggleSimilars", status);
  },
  resetCustomPotion({ commit }) {
    commit("setStep", 0);
    commit("setUnderlyingSelected", {
      address: null,
      symbol: null,
      name: null,
      image: null,
      price: null,
    });
    commit("setStrikeSelected", null);
    commit("setDurationSelected", null);
    commit("setSimilarPotions", []);
    commit("resetRouterData");
  },
  updateQuantity({ commit }, data) {
    commit("setQuantity", data);
  },

  async createPotion({ state, dispatch, rootGetters }) {
    const maxPremium = parseFloat(
      (
        state.router.premiumTotal *
        (1 + parseFloat(rootGetters["potions/currentSlippage"]) / 100)
      ).toFixed(6)
    );
    let callback = null;
    const errorMessage = "Error in the potion creation";
    if (
      state.router.counterparties.length >= rootGetters["maxCounterparties"]
    ) {
      callback = async () => {
        await deployAndBuyFromOtokenOverflow(
          state.underlyingSelected.address,
          parseFloat(state.strike.priceSelected).toFixed(8),
          parseInt(state.duration.daysSelected),
          state.router.counterparties,
          maxPremium,
          rootGetters["maxCounterparties"]
        );
        router.push({ name: "MyPotions" });
        dispatch("resetCustomPotion");
      };

      dispatch(
        "showToast",
        {
          title: "Waiting for creation!",
          subtitle: `You will need to sign ${Math.ceil(
            state.router.counterparties.length /
              rootGetters["maxCounterparties"]
          )} transactions now`,
        },
        { root: true }
      );
    } else {
      callback = async () => {
        const transaction = await deployAndBuyFromOToken(
          state.underlyingSelected.address,
          parseFloat(state.strike.priceSelected).toFixed(8),
          parseInt(state.duration.daysSelected),
          state.router.counterparties,
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
                router.push({ name: "MyPotions" });
                dispatch("resetCustomPotion");
              }
            },
            errorMessage: "",
          },
          { root: true }
        );
      };
    }

    await dispatch(
      "potions/approvePotionBuy",
      { amount: maxPremium },
      { root: true }
    );
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
};

const mutations = {
  resetRouterData(state) {
    state.router.premiumTotal = 0;
    state.router.counterparties = [];
    state.router.pools = [];
    state.router.marketDepth = "0";
    state.router.maxNumberOfOtokens = "0";
    state.router.gasUnits = "0";
  },
  calculateMarketDepth(state) {
    state.router.marketDepth = state.router.pools
      .reduce((sum, pool) => {
        return sum + parseFloat(pool.unlocked);
      }, 0)
      .toString();
    state.router.maxNumberOfOtokens =
      parseFloat(state.router.marketDepth) /
      parseFloat(state.strike.priceSelected);
  },
  setGasEstimation(state, payload) {
    state.router.gasUnits = payload;
  },
  setPoolsFromCriteria(state, payload) {
    state.router.pools = payload;
  },
  setRouterData(state, payload) {
    state.router.premiumTotal = payload.premium;
    state.router.counterparties = payload.counterparties;
  },
  setOrderTable(state, payload) {
    state.router.orderTable = payload;
  },
  setCriterias(state, criterias) {
    state.criterias = criterias;
  },
  setCurrentPrice(state, value) {
    state.underlyingSelected.price = value;
  },
  setMaxStrike(state, payload) {
    state.strike.priceRelativeMax = payload;
  },
  setMaxDuration(state, payload) {
    state.duration.daysMax = payload;
  },
  setStep(state, payload) {
    state.step = payload;
  },
  setUnderlyingSelected(state, payload) {
    state.underlyingSelected = payload;
  },
  setStrikeSelected(state, payload) {
    const num = parseFloat(payload);
    state.strike.priceSelected = _isFinite(num) ? num.toString() : "";
  },
  setDurationSelected(state, payload) {
    const num = parseFloat(payload);
    state.duration.daysSelected = _isFinite(num) ? num.toString() : "";
  },
  toggleSimilars(state, payload) {
    state.similars.toggle = payload;
  },
  setQuantity(state, payload) {
    state.quantity = payload;
  },
  setRouterPremium(state, payload) {
    state.router.premiumTotal = payload;
  },
  setCounterparties(state, payload) {
    state.router.counterparties = payload;
  },
  setSimilarPotions(state, payload) {
    state.similars.potions = payload;
  },
};

export const custom = {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
