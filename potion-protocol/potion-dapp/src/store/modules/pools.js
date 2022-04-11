import {
  each as _each,
  filter as _filter,
  get as _get,
  isArray as _isArray,
  last as _last,
  size as _size,
  sum as _sum,
} from "lodash-es";
import {
  depositCollateral,
  reclaimCollateralFromPoolRecord,
  withdrawCollateral,
} from "@/services/contracts/pools";

import { Pools } from "../../services/api/pools";
import { contractsAddresses } from "@/services/contracts";
import { createNewPool } from "@/services/contracts/pools";
import { erc20Allowance } from "@/services/contracts/erc20";
import { estimateSavePool } from "@/services/contracts/pools";
import { getEmergingBondingCurvesFromCriterias } from "@/services/router/worker.worker.ts";
import { getEtherscanLink } from "@/helpers";
import { getPriceFromOracle } from "@/services/contracts/oracle";
import router from "@/routes";

const defaultLiquidity = "100";
const getDefaultCurveSettings = () => {
  return {
    parameters: {
      a: "2.5",
      b: "2.5",
      c: "2.5",
      d: "2.5",
      maxUtil: "1",
    },
  };
};

const poolsToLoad = 8;

const state = {
  myPools: [],
  myPoolsCanLoadMore: false,
  mostPopular: null,
  mostPopularCanLoadMore: {
    byNumber: false,
    bySize: false,
    byPnl: false,
  },
  selectedTemplate: null,
  statusBarOpened: false,
  refundPerOToken: null,
  poolOTokens: null,
  focusedPool: null,
  customPool: {
    gasUnits: "0",
    underlyingsModalOpened: false,
    underlyings: [],
    liquidity: defaultLiquidity,
    curveSettings: getDefaultCurveSettings(),
    emergingCurve: [],
  },
};

const getters = {
  getGas: (state) => state.customPool.gasUnits,
  myPools: (state) => state.myPools,
  myLastLoadedPoolId: (state) => _get(_last(state.myPools), "poolId", -1),
  myPoolsCanLoadMore: (state) => state.myPoolsCanLoadMore,
  myPoolsNumber: (state) => _size(state.myPools).toString(),
  myPoolsLiquidityProvided: (state) =>
    _sum(state.myPools.map((v) => parseFloat(v.size))).toString(),
  myPoolsAveragePnl: (state) => {
    if (state.myPools.length > 0) {
      const sum = _sum(state.myPools.map((v) => parseFloat(v.pnlPercentage)));
      return (sum / state.myPools.length).toString();
    }
    return "0";
  },
  mostCookedTemplates: (state) => _get(state, ["mostPopular", "byNumber"], []),
  biggestTemplates: (state) => _get(state, ["mostPopular", "bySize"], []),
  highestPnlTemplates: (state) => _get(state, ["mostPopular", "byPnl"], []),
  mostCookedTemplatesCanLoadMore: (state) =>
    _get(state, ["mostPopularCanLoadMore", "byNumber"], false),
  biggestTemplatesCanLoadMore: (state) =>
    _get(state, ["mostPopularCanLoadMore", "bySize"], false),
  highestPnlTemplatesCanLoadMore: (state) =>
    _get(state, ["mostPopularCanLoadMore", "byPnl"], false),
  totalRefund: (state) => _sum(state.refundPerOToken),
  poolOTokens: (state) => state.poolOTokens,
  expiredOTokens: (state, _, _1, rootGetters) =>
    _filter(
      state.poolOTokens,
      (pool) => pool.otoken.expiry <= rootGetters.blockEpoch
    ),
  activeOTokens: (state, _, _1, rootGetters) =>
    _filter(
      state.poolOTokens,
      (pool) => pool.otoken.expiry > rootGetters.blockEpoch
    ),
  refundPerOToken: (state) => state.refundPerOToken,
  focusedPool: (state) => state.focusedPool,
  underlyings: (state) =>
    state.customPool.underlyings.filter(
      (underlying) => underlying.price !== ""
    ),
  getLiquidity: (state) => state.customPool.liquidity,
  curveSettings: (state) => state.customPool.curveSettings,
  storeParameters: (state) => state.customPool.curveSettings.parameters,
  emergingCurve: (state) => state.customPool.emergingCurve,
  selectedUnderlyings: (state) =>
    state.customPool.underlyings.filter((obj) => obj.selected),
  criteriasForRouter: (_, getters) =>
    getters.selectedUnderlyings.map((underlying) => {
      return {
        underlyingAsset: {
          symbol: underlying.symbol,
          id: underlying.address,
        },
        maxStrikePercent: underlying.strike,
        maxDurationInDays: underlying.duration,
      };
    }),
  unselectedUnderlyingsSymbols: (state) =>
    state.customPool.underlyings
      .filter((obj) => !obj.selected)
      .map((obj) => obj.symbol),
  customPoolRoutes: (state, getters) => [
    {
      name: "PoolSetup",
      label: "Pool Setup",
      description: "Choose one or more assets this pool will insure",
      completed: getters.selectedUnderlyings.length > 0,
    },
    {
      name: "CurveSettings",
      label: "Curve Settings",
      description:
        "Curve the pool will use to determine sell prices, as a function of your pool utilization.",
      moreInfo: {
        label: "Learn More",
        url: "",
      },
      completed: state.customPool.curveSettings !== {},
    },
    {
      name: "PoolReview",
      label: "Review and Create",
      description: "Review your choices before creating the pool on chain.",
      moreInfo: {
        label: "Are you unsure about the risk you are taking?",
        url: "",
      },
      completed: false,
    },
  ],
};

const mutations = {
  appendFocusedPoolSnapshots(state, payload) {
    payload.forEach((snapshot) => state.focusedPool.snapshots.push(snapshot));
  },
  setEstimateCreatePool(state, payload) {
    state.customPool.gasUnits = payload;
  },
  setMyPools(state, payload) {
    state.myPools = payload;
  },
  appendMyPools(state, payload) {
    if (_isArray(payload)) {
      payload.forEach((item) => state.myPools.push(item));
    } else {
      state.myPools.push(payload);
    }
  },
  setMyPoolsCanLoadMore(state, payload) {
    state.myPoolsCanLoadMore = payload;
  },
  setBiggestTemplates(state, payload) {
    state.biggestTemplates = payload;
  },
  setMostCookedTemplates(state, payload) {
    state.mostCookedTemplates = payload;
  },
  toggleStatusBar(state) {
    state.statusBarOpened = !state.statusBarOpened;
  },
  selectTemplate(state, payload) {
    state.selectedTemplate = payload;
  },
  setFocusedPool(state, payload) {
    state.focusedPool = payload;
  },
  setFocusedPoolSize(state, payload) {
    state.focusedPool.size = payload;
  },
  setPoolOTokens(state, payload) {
    state.poolOTokens = payload;
  },
  setRefundPerOToken(state, payload) {
    state.refundPerOToken = payload;
  },
  toggleUnderlyingsModal(state) {
    state.customPool.underlyingsModalOpened =
      !state.customPool.underlyingsModalOpened;
  },
  setUnderlyings(state, payload) {
    state.customPool.underlyings = payload;
  },
  setFormattedUnderlyings(state, payload) {
    payload.forEach((underlying) => {
      underlying.selected = false;
      underlying.strike = "100";
      underlying.duration = "30";
      underlying.price = "";
    });
    state.customPool.underlyings = payload;
  },
  toggleUnderlying(state, payload) {
    state.customPool.underlyings.forEach((underlying) => {
      if (underlying.address === payload) {
        underlying.selected = !underlying.selected;
      }
    });
  },
  setUnderlyingValue(state, payload) {
    state.customPool.underlyings.forEach((underlying) => {
      if (underlying.address === payload.address) {
        underlying.strike = payload.strike;
        underlying.duration = payload.duration;
      }
    });
  },
  setLiquidity(state, payload) {
    state.customPool.liquidity = payload;
  },
  setCurveSettings(state, payload) {
    state.customPool.curveSettings = payload;
  },
  setEmergingCurve(state, payload) {
    state.customPool.emergingCurve = payload;
  },
  setUnderlyingsPrices(state, payload) {
    state.customPool.underlyings.forEach((underlying) => {
      payload.forEach((x) => {
        if (Object.keys(x)[0] === underlying.address.replace(/ /g, "")) {
          underlying.price = x[underlying.address.replace(/ /g, "")];
        }
      });
    });
  },
  setPopularTemplates(state, payload) {
    state.mostPopular = payload;
  },
  appendPopularTemplates(state, { key, templates }) {
    templates.forEach((template) => state.mostPopular[key].push(template));
  },
  setPopularTemplatesCanLoadMore(state, { key, value }) {
    state.mostPopularCanLoadMore[key] = value;
  },
};

const actions = {
  toggleStatusBar({ commit }) {
    commit("toggleStatusBar");
  },
  async selectTemplate({ commit, dispatch }, data) {
    const callback = async () => {
      data.snapshots = await Pools.getSnapshotsByTemplate(data.address);
      commit("selectTemplate", data);
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },

  async getSnapshots({ commit }, { templateAddress, alreadyLoadedIds, num }) {
    commit("startLoading", null, { root: true });
    try {
      const snapshots = await Pools.getSnapshotsByTemplate(
        templateAddress,
        alreadyLoadedIds,
        num
      );
      commit("stopLoading", null, { root: true });
      return snapshots;
    } catch (error) {
      throw new Error(error);
    }
  },
  async getMyPools({ commit, dispatch, getters, rootGetters }) {
    const callback = async () => {
      const pools = await Pools.getPools(
        rootGetters["wallet/walletAddress"],
        getters.myLastLoadedPoolId,
        poolsToLoad
      );
      commit("setMyPoolsCanLoadMore", !(pools.length < poolsToLoad));
      commit("appendMyPools", pools);
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },

  async getTemplate({ commit }, params) {
    commit("startLoading", null, { root: true });
    try {
      const template = await Pools.getTemplate(params);
      commit("stopLoading", null, { root: true });
      return template;
    } catch (error) {
      throw new Error(error);
    }
  },
  async getPopularTemplates({ commit, dispatch }) {
    const callback = async () => {
      const popularTemplates = await Pools.getPopularTemplates({
        num: poolsToLoad,
        size: 0,
        minClones: 1,
        minPnl: 0,
        orderDirection: "desc",
      });
      commit("setPopularTemplates", popularTemplates);
      _each(popularTemplates, (templates, key) => {
        commit("setPopularTemplatesCanLoadMore", {
          key,
          value: !(templates.length < poolsToLoad),
        });
      });
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async loadMoreTemplates({ commit, dispatch, getters }, filteringMode) {
    const filteringModeToData = {
      byNumber: {
        filteringValue: 1,
        alreadyLoadedIds: getters.mostCookedTemplates.map((item) => item.id),
      },
      bySize: {
        filteringValue: 0,
        alreadyLoadedIds: getters.biggestTemplates.map((item) => item.id),
      },
      byPnl: {
        filteringValue: 0,
        alreadyLoadedIds: getters.highestPnlTemplates.map((item) => item.id),
      },
    };
    const callback = async () => {
      const { filteringValue, alreadyLoadedIds } =
        filteringModeToData[filteringMode];
      const templates = await Pools.loadMoreTemplates({
        num: poolsToLoad,
        filteringMode,
        filteringValue,
        alreadyLoadedIds,
        orderDirection: "desc",
      });
      commit("appendPopularTemplates", { key: filteringMode, templates });
      commit("setPopularTemplatesCanLoadMore", {
        key: filteringMode,
        value: !(templates.length < poolsToLoad),
      });
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getTemplatesBySize({ commit, dispatch }, params) {
    const callback = async () => {
      commit(
        "setBiggestTemplates",
        await Pools.getTemplatesBySize({
          num: params.num,
          size: params.size,
          orderDirection: params.orderDirection,
        })
      );
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getTemplatesByNumbers({ commit, dispatch }, params) {
    const callback = async () => {
      commit(
        "setMostCookedTemplates",
        await Pools.getTemplatesByNumbers({
          num: params.num,
          minClones: params.minClones,
          orderDirection: params.orderDirection,
        })
      );
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  resetFocusedPool({ commit }) {
    commit("setFocusedPool", null);
  },
  async getPool({ commit, dispatch }, params) {
    const { id } = params;
    const callback = async () => {
      commit("setFocusedPool", await Pools.getPool(id));
      const oTokens = await Pools.getOTokens(id);
      commit("setPoolOTokens", oTokens);
    };
    const errorMessage = "";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async getMoreFocusedPoolSnapshots({ commit, state }) {
    const id = state.focusedPool.id;
    const alreadyLoadedIds = state.focusedPool.snapshots.map((s) => s.id);
    const snapshots = await Pools.getSnapshotsByPool(id, alreadyLoadedIds);
    commit("appendFocusedPoolSnapshots", snapshots);
  },
  toggleUnderlyingsModal({ commit }) {
    commit("toggleUnderlyingsModal");
  },
  destroyUnderlyings({ commit }) {
    commit("setUnderlyings", []);
  },
  async setFormattedUnderlyings({ commit, dispatch }) {
    const callback = async () => {
      const response = await Pools.getProductsUSDCCollateral();
      commit("setFormattedUnderlyings", response);
    };
    const errorMessage = "Error while getting the underlyings";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  toggleUnderlying({ commit }, underlying) {
    commit("toggleUnderlying", underlying);
  },
  setUnderlyingValue({ commit }, values) {
    commit("setUnderlyingValue", values);
  },
  setLiquidity({ commit }, value) {
    commit("setLiquidity", value);
  },
  setCurveSettings({ commit }, settings) {
    commit("setCurveSettings", settings);
  },
  async approveDeposit({ dispatch, rootState }, { amount }) {
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
        { root: true }
      );
    }
  },
  async estimateCreateCustomPool({ getters, commit }) {
    const response = await estimateSavePool(
      parseFloat(parseFloat(getters.getLiquidity).toFixed(6)),
      getters.storeParameters,
      getters.selectedUnderlyings,
      0
    );
    commit("setEstimateCreatePool", response);
  },
  async createCustomPool({ getters, dispatch }) {
    const callback = async () => {
      const transaction = await createNewPool(
        parseFloat(parseFloat(getters.getLiquidity).toFixed(6)),
        getters.storeParameters,
        getters.selectedUnderlyings
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
      const receipt = await transaction.wait();
      if (receipt.status) {
        dispatch(
          "showToast",
          {
            title: "Your new Pool is ready",
            subtitle: "You can see the transaction on etherscan",
            etherscanLink: getEtherscanLink(transaction.hash),
          },
          { root: true }
        );
        router.push({ name: "MyPools" });
      }
    };
    const errorMessage = "Error in the pool creation";
    await dispatch("approveDeposit", { amount: getters.getLiquidity });
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async resetCustomPool({ dispatch }, alreadyCreatingCustomPool) {
    if (!alreadyCreatingCustomPool) {
      dispatch("setLiquidity", defaultLiquidity);
      dispatch("setCurveSettings", getDefaultCurveSettings());
      dispatch("destroyUnderlyings");
      await dispatch("setFormattedUnderlyings");
      await dispatch("getUnderlyingsPrices");
    } else {
      console.log("Already Creating customPool");
    }
  },
  async getUnderlyingsPrices({ commit, state }) {
    const results = [];
    for (let underlying of state.customPool.underlyings) {
      try {
        results.push({
          [underlying.address.replace(/ /g, "")]: await getPriceFromOracle(
            underlying.address
          ),
        });
      } catch (e) {
        console.log(e);
      }
    }
    commit("setUnderlyingsPrices", results);
  },

  async calculateEmergingCurveFromCriterias({ commit, getters, dispatch }) {
    const callback = async () => {
      const emergingCurve = await getEmergingBondingCurvesFromCriterias(
        getters.criteriasForRouter
      );
      commit("setEmergingCurve", emergingCurve);
    };
    const errorMessage = "Error calculating emerging curves";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },

  updateFocusedPoolSize({ commit, state }, payload) {
    const size = parseFloat(state.focusedPool.size) + payload;
    commit("setFocusedPoolSize", size.toString());
  },
  async depositCollateral({ dispatch, state }, { depositAmount }) {
    const callback = async () => {
      const transaction = await depositCollateral(
        parseInt(state.focusedPool.poolId),
        depositAmount
      );
      dispatch(
        "showToast",
        {
          title: "Depositing liquidity",
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
              dispatch("updateFocusedPoolSize", depositAmount);
              dispatch(
                "showToast",
                {
                  title: "Succesfully Deposited!",
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
    const errorMessage = "Error while trying to deposit liquidity";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async withdrawCollateral({ dispatch, state }, { withdrawAmount }) {
    const callback = async () => {
      const transaction = await withdrawCollateral(
        parseInt(state.focusedPool.poolId),
        withdrawAmount
      );
      dispatch(
        "showToast",
        {
          title: "Withdrawing liquidity",
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
              dispatch("updateFocusedPoolSize", -withdrawAmount);
              dispatch(
                "showToast",
                {
                  title: "Succesfully Withdrawn!",
                  subtitle: "You can see the transaction on etherscan",
                  etherscanLink: getEtherscanLink(transaction.hash),
                },
                { root: true }
              );
            }
          },
          errorMessage: "Error in the receipt update",
        },
        { root: true }
      );
    };
    const errorMessage = "Error while trying to withdraw liquidity";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
  async reclaimCollateralFromPoolRecord({ dispatch }, { mappedPools }) {
    const callback = async () => {
      const transaction = await reclaimCollateralFromPoolRecord(mappedPools);
      dispatch(
        "showToast",
        {
          title: "Reclaiming collateral",
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
                  title: "Succesfully reclaimed collateral!",
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
    const errorMessage = "Error while trying to withdraw liquidity";
    await dispatch("runWithLoader", { callback, errorMessage }, { root: true });
  },
};

export const pools = {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
