import { getBlockGasLimit, getLatestBlockTimestamp } from "@/services/ethers";

import Toast from "@/components/cards/Toast.vue";
import Vue from "vue";
import Vuex from "vuex";
import { pools } from "./modules/pools";
import { potions } from "./modules/potions";
import { wallet } from "./modules/wallet";

Vue.use(Vuex);

const encoder = new TextEncoder();

const getHash = async (item) => {
  const text = item.toString();
  if (window.isSecureContext) {
    const encoded = encoder.encode(text);
    const buffer = await crypto.subtle.digest("SHA-1", encoded);
    const ar = Array.from(new Uint8Array(buffer));
    return ar.map((b) => b.toString(16).padStart(2, "0")).join("");
  }
  return text;
};

export default new Vuex.Store({
  state: {
    loadingQueue: [],
    loading: false,
    transactionStatus: null,
    blockEpoch: null,
    maxCounterparties: 100,
    blockGasLimit: "0",
  },
  getters: {
    maxCounterparties: (state) => state.maxCounterparties,
    blockEpoch: (state) => state.blockEpoch,
    isLoading: (state) => state.loading || state.loadingQueue.length > 0,
    blockGasLimit: (state) => (state.blockGasLimit ? state.blockGasLimit : "0"),
  },
  mutations: {
    setBlockGasLimit(state, payload) {
      state.blockGasLimit = payload;
    },
    addToLoadingQueue(state, payload) {
      state.loadingQueue.push(payload);
    },
    removeFromLoadingQueue(state, payload) {
      window.requestAnimationFrame(() => {
        const index = state.loadingQueue.indexOf(payload);
        if (index > -1) {
          state.loadingQueue.splice(index, 1);
        }
      });
    },
    flushLoadingQueue(state) {
      while (state.loadingQueue.length > 0) {
        state.loadingQueue.pop();
      }
    },
    startLoading(state) {
      state.loading = true;
    },
    stopLoading(state) {
      window.requestAnimationFrame(() => {
        state.loading = false;
      });
    },
    setTransactionStatus(state, payload) {
      state.transactionStatus = payload;
    },
    updateBlockEpoch(state, payload) {
      state.blockEpoch = payload;
    },
  },
  actions: {
    async getBlockGasLimit({ commit }) {
      const response = await getBlockGasLimit();
      commit("setBlockGasLimit", response);
    },
    async getBlockEpochBackground({ commit }) {
      try {
        const response = await getLatestBlockTimestamp();
        commit("updateBlockEpoch", response);
      } catch (e) {
        throw new Error("Eror while trying to get the block epoch");
      }
    },
    async getBlockEpoch({ commit, dispatch }) {
      const callback = async () => {
        const response = await getLatestBlockTimestamp();
        commit("updateBlockEpoch", response);
      };
      const errorMessage = "";
      await dispatch("runWithLoader", { callback, errorMessage });
    },
    async runWithLoader({ commit }, { callback, errorMessage }) {
      const key = await getHash(errorMessage);
      commit("addToLoadingQueue", key);
      try {
        await callback();
        commit("removeFromLoadingQueue", key);
        return true;
      } catch (error) {
        commit("removeFromLoadingQueue", key);
        if (error.reason) {
          throw new Error(error.reason);
        }
        throw new Error(error);
      }
    },
    showToast({ commit }, payload) {
      commit("flushLoadingQueue");
      commit("stopLoading");
      Vue.$toast(
        {
          component: Toast,

          props: {
            title: payload.title,
            subtitle: payload.subtitle,
            etherscanLink: payload.etherscanLink,
            icon: payload.icon,
          },
        },
        {
          closeButton: false,
          timeout: 5000,
          toastClassName: [
            "border",
            "border-primary-500",
            "shadow-lg",
            "toast-gradient-background",
            "py-3",
            "pl-3",
            "pr-7",
            "!rounded-2xl",
          ],
          icon: false,
        }
      );
    },
  },
  modules: {
    potions,
    pools,
    wallet,
  },
});
