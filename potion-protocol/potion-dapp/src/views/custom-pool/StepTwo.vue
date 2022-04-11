<template>
  <div
    class="flex flex-col xl:flex-row xl:space-x-6 space-y-6 xl:space-y-0 mt-5"
  >
    <div class="grid grid-cols-1 gap-6 auto-rows-min w-full xl:w-1/3">
      <PoolSummary
        :liquidity="getLiquidity"
        :underlyings="selectedUnderlyings"
        :currency="stableCoinCollateral"
        @next="$router.push({ name: 'PoolReview' })"
        @back="$router.push({ name: 'PoolSetup' })"
      />
      <div class="hidden xl:block">
        <NavigateToCloneTemplateCard />
      </div>
    </div>
    <div class="w-full xl:2/3 flex flex-col">
      <BondingCurve
        :curve="storeParameters"
        :emergingCurves="emergingCurve"
        :unload-keys="unselectedUnderlyingsSymbols"
        @curve-settings-updated="setCurveSettings"
      />
    </div>
    <NavigateToCloneTemplateCard class="xl:hidden" />
  </div>
</template>

<script>
import BondingCurve from "@/components/cards/CustomBondingCurve.vue";
import PoolSummary from "@/components/cards/PoolSummary.vue";
import NavigateToCloneTemplateCard from "@/components/cards/NavigateToCloneTemplateCard.vue";

import { mapGetters, mapActions } from "vuex";

export default {
  components: {
    BondingCurve,
    PoolSummary,
    NavigateToCloneTemplateCard,
  },
  computed: {
    ...mapGetters("pools", [
      "selectedUnderlyings",
      "unselectedUnderlyingsSymbols",
      "storeParameters",
      "emergingCurve",
      "getLiquidity",
    ]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
  },
  methods: {
    ...mapActions("pools", [
      "setCurveSettings",
      "calculateEmergingCurveFromCriterias",
    ]),
  },
  mounted() {
    this.calculateEmergingCurveFromCriterias();
  },
};
</script>
