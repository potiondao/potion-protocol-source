<template>
  <div
    class="flex flex-col xl:flex-row xl:space-x-6 space-y-6 xl:space-y-0 mt-5"
  >
    <div class="grid grid-cols-1 gap-6 auto-rows-min w-full xl:w-1/3">
      <PoolSettings
        @next="$router.push({ name: 'CurveSettings' })"
        @back="$router.push({ name: 'MyPools' })"
        :backDisabled="false"
        :nextDisabled="
          selectedUnderlyings.length === 0 ||
          parseFloat(getLiquidity) <= 0 ||
          parseFloat(getLiquidity) > parseFloat(stableCoinCollateralBalance)
        "
        :liquidityError="
          parseFloat(getLiquidity) <= 0 ||
          parseFloat(getLiquidity) > parseFloat(stableCoinCollateralBalance)
        "
        :value="getLiquidity"
        @input="debouncedSetLiquidity"
      />
      <div class="hidden xl:block">
        <NavigateToCloneTemplateCard />
      </div>
    </div>
    <UnderlyingsEditCard
      :underlyings="underlyings"
      :selectedUnderlyings="selectedUnderlyings"
      @underlying-selected="toggleUnderlying"
      @underlying-updated="setUnderlyingValue"
    />
    <NavigateToCloneTemplateCard class="xl:hidden" />
  </div>
</template>

<script>
import { debounce as _debounce } from "lodash-es";
import PoolSettings from "@/components/cards/PoolSettings.vue";
import UnderlyingsEditCard from "@/components/blocks/CustomPoolCreation/UnderlyingsEditCard.vue";
import NavigateToCloneTemplateCard from "@/components/cards/NavigateToCloneTemplateCard.vue";

import { mapActions, mapGetters } from "vuex";

export default {
  components: {
    PoolSettings,
    NavigateToCloneTemplateCard,
    UnderlyingsEditCard,
  },
  computed: {
    ...mapGetters("pools", [
      "underlyings",
      "selectedUnderlyings",
      "getLiquidity",
    ]),
    ...mapGetters("wallet", ["stableCoinCollateralBalance"]),
  },
  methods: {
    ...mapActions("pools", [
      "toggleUnderlying",
      "setUnderlyingValue",
      "setLiquidity",
      "getUnderlyingsPrices",
    ]),
    debouncedSetLiquidity: _debounce(function (liquidity) {
      this.setLiquidity(liquidity);
    }, 500),
  },
};
</script>
