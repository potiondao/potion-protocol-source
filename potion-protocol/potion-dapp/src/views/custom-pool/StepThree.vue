<template>
  <div class="mt-6">
    <div
      class="flex flex-col xl:flex-row xl:space-x-6 space-y-6 xl:space-y-0 mt-5"
    >
      <div class="grid grid-cols-1 gap-6 auto-rows-min w-full xl:w-1/3">
        <CreatePool
          :liquidity="getLiquidity"
          :underlyings="selectedUnderlyings"
          :currency="stableCoinCollateral"
          @navigationBack="$router.push({ name: 'CurveSettings' })"
          @createPool="createCustomPool"
          :gasUnits="getGas"
        />
      </div>
      <div class="w-full xl:2/3">
        <BondingCurve
          :emerging-curves="emergingCurve"
          :parameters="curveSettings.parameters"
        />
      </div>
    </div>
  </div>
</template>

<script>
import BondingCurve from "@/components/cards/BondingCurve.vue";
import CreatePool from "@/components/cards/CreatePool.vue";
import { mapGetters, mapActions } from "vuex";

export default {
  components: {
    CreatePool,
    BondingCurve,
  },
  computed: {
    ...mapGetters("pools", [
      "selectedUnderlyings",
      "curveSettings",
      "getLiquidity",
      "emergingCurve",
      "storeParameters",
      "getGas",
    ]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
  },
  methods: {
    ...mapActions("pools", ["createCustomPool", "estimateCreateCustomPool"]),
  },
  async mounted() {
    await this.estimateCreateCustomPool();
  },
};
</script>
