<template>
  <div class="container p-6 mx-auto" v-if="editingPool">
    <div
      class="
        flex flex-col
        xl:flex-row xl:space-x-6
        space-y-6
        xl:space-y-0
        mt-5
        h-full
      "
    >
      <div class="w-full xl:w-1/3">
        <EditPoolSettings
          :liquidity="liquidity"
          v-model="additionalLiquidity"
          @pool-edit="editPool"
          @cancel-edit="returnToPool"
          :enabled="editEnabled"
          :inputError="inputError"
          :gasUnits="gasUnits"
        />
      </div>
      <div class="w-full xl:overflow-y-scroll">
        <UnderlyingsEditCard
          :underlyings="underlyings"
          :underlyings-prices="priceMap"
          :selectedUnderlyings="selectedUnderlyings"
          @underlying-selected="underlyingSelected"
          @underlying-updated="underlyingUpdated"
        />
        <BondingCurve
          class="my-6"
          :curve="editingPool.template.curve"
          :emergingCurves="emergingCurves"
          :unload-keys="unselectedUnderlyingsSimbols"
          @curve-settings-updated="updateCurveSettings"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Pools } from "@/services/api/pools";
import { editPool } from "@/services/contracts/pools";
import EditPoolSettings from "@/components/cards/EditPoolSettings.vue";
import UnderlyingsEditCard from "@/components/blocks/CustomPoolCreation/UnderlyingsEditCard.vue";
import BondingCurve from "@/components/cards/CustomBondingCurve.vue";
import { estimateSavePool } from "@/services/contracts/pools";

import {
  isNil as _isNil,
  get as _get,
  cloneDeep as _cloneDeep,
  merge as _merge,
} from "lodash-es";

import { getEmergingBondingCurvesFromCriterias } from "@/services/router/emergingBondingCurve";
import { getEtherscanLink, getUnderlyingsPriceMap } from "@/helpers";
import { mapActions, mapGetters } from "vuex";
import { debounce as _debounce } from "lodash-es";

const getUnderlyingAddress = (item) =>
  _get(item, ["criteria", "underlyingAsset", "address"], "");

const createDefaultUnderlying = (item, underlying) => {
  const result = {
    id: underlying.address,
    selected: !_isNil(item),
    strike: _isNil(item) ? "100" : item.criteria.maxStrikePercent,
    duration: _isNil(item) ? "30" : item.criteria.maxDurationInDays,
  };
  _merge(result, underlying);
  return result;
};

const formatUnderlyings = (underlyings, criterias) =>
  underlyings.map((underlying) =>
    createDefaultUnderlying(
      criterias.find(
        (item) => getUnderlyingAddress(item) === underlying.address
      ),
      underlying
    )
  );

export default {
  props: {
    initialEmergingCurves: {
      type: Array,
      default: () => [],
    },
    underlyingsPriceMap: {
      type: Object,
      default: () => {
        return {};
      },
    },
    inModal: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    EditPoolSettings,
    BondingCurve,
    UnderlyingsEditCard,
  },
  data() {
    return {
      additionalLiquidity: "0",
      underlyings: [],
      emergingCurves: [],
      editingPool: null,
      localPriceMap: null,
      gasUnits: "21700",
    };
  },
  watch: {
    additionalLiquidity: {
      handler: _debounce(async function () {
        this.gasUnits = await this.estimateGas();
      }, 1000),
    },
    editingPool: {
      deep: true,
      handler: _debounce(async function () {
        this.gasUnits = await this.estimateGas();
      }, 1000),
    },
    selectedUnderlyings: {
      deep: true,
      handler: _debounce(async function () {
        this.gasUnits = await this.estimateGas();
      }, 1000),
    },
  },
  computed: {
    ...mapGetters("wallet", [
      "stableCoinCollateral",
      "stableCoinCollateralBalance",
    ]),
    ...mapGetters("pools", ["focusedPool"]),

    inputError() {
      return parseFloat(this.additionalLiquidity) >
        parseFloat(this.stableCoinCollateralBalance) ||
        parseFloat(this.additionalLiquidity) < 0
        ? true
        : false;
    },
    criteriaSet() {
      return _get(this, ["editingPool", "template", "criteriaSet"], {});
    },
    selectedUnderlyings() {
      return this.underlyings.filter((item) => item.selected);
    },
    selectedCriteriaSets() {
      return this.selectedUnderlyings.map((underlying) => {
        return {
          underlyingAsset: underlying,
          maxStrikePercent: underlying.strike,
          maxDurationInDays: underlying.duration,
        };
      });
    },
    unselectedUnderlyingsSimbols() {
      return this.underlyings
        .filter((item) => !item.selected)
        .map((item) => item.symbol);
    },
    liquidity() {
      const liquidity = _get(this, ["editingPool", "size"], "0");
      return `${liquidity} ${this.stableCoinCollateral}`;
    },
    editEnabled() {
      return this.selectedUnderlyings.length > 0 && !this.inputError;
    },
    priceMap() {
      return this.inModal ? this.underlyingsPriceMap : this.localPriceMap;
    },
  },
  methods: {
    ...mapActions(["runWithLoader", "showToast"]),
    ...mapActions("pools", ["getPool", "approveDeposit"]),
    async setEmergingCurves() {
      this.emergingCurves = await getEmergingBondingCurvesFromCriterias(
        this.selectedCriteriaSets
      );
    },
    searchUnderlying(address) {
      return this.underlyings.find((u) => u.address === address);
    },
    async underlyingSelected(address) {
      const underlying = this.searchUnderlying(address);
      if (underlying) {
        underlying.selected = !underlying.selected;
        await this.setEmergingCurves();
      }
    },
    async underlyingUpdated({ address, strike, duration }) {
      const underlying = this.searchUnderlying(address);
      if (underlying) {
        underlying.duration = duration;
        underlying.strike = strike;
        await this.setEmergingCurves();
      }
    },
    updateCurveSettings({ parameters }) {
      this.$set(this.editingPool.template, "curve", parameters);
    },
    returnToPool() {
      if (this.inModal) {
        this.$emit("close-edit");
      } else {
        this.$router.push({
          name: "Pool",
          params: { hash: this.editingPool.id },
        });
      }
    },
    async estimateGas() {
      return await estimateSavePool(
        parseFloat(parseFloat(this.additionalLiquidity).toFixed(6)),
        this.editingPool.template.curve,
        this.selectedUnderlyings,
        this.editingPool.poolId
      );
    },
    async editPool() {
      if (this.editEnabled) {
        const callback = async () => {
          const transaction = await editPool(
            parseFloat(parseFloat(this.additionalLiquidity).toFixed(6)),
            this.editingPool.template.curve,
            this.selectedUnderlyings,
            this.editingPool.poolId
          );
          this.showToast({
            title: "Updating your Pool",
            subtitle: "Check the status on etherscan",
            etherscanLink: getEtherscanLink(transaction.hash),
          });
          const receipt = await transaction.wait();
          if (receipt.status) {
            this.showToast({
              title: "Your pool edits are ready",
              subtitle: "You can see the transaction on etherscan",
              etherscanLink: getEtherscanLink(transaction.hash),
            });
            this.returnToPool();
          }
        };
        const errorMessage = "Error editing the pool";
        await this.approveDeposit({ amount: this.additionalLiquidity });
        await this.runWithLoader({ callback, errorMessage });
      }
    },
  },
  async created() {
    if (_isNil(this.focusedPool)) {
      await this.getPool({
        id: this.$route.params.hash,
        walletAddress: this.$store.state.wallet.address,
      });
    }
    this.$set(this, "editingPool", _cloneDeep(this.focusedPool));
    const underlyings = await Pools.getProductsUSDCCollateral();
    this.underlyings = formatUnderlyings(
      underlyings,
      _get(this, ["criteriaSet", "criterias"], [])
    );
    if (this.inModal) {
      this.$set(this, "emergingCurves", this.initialEmergingCurves);
    } else {
      this.$set(
        this,
        "localPriceMap",
        await getUnderlyingsPriceMap(this.underlyings)
      );
      await this.setEmergingCurves();
    }
  },
};
</script>
