<template>
  <CardContainer :fullHeight="false">
    <div class="flex flex-col-reverse lg:flex-row">
      <Chart
        :bonding-curve="bondingCurve"
        :emerging-curves="emergingCurves"
        class="w-full lg:w-3/4 py-4 pl-4 lg:pl-6"
      />
      <BondingCurveParams
        class="w-full lg:w-1/4 p-4 lg:px-6"
        :parameters="parameters"
      />
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import Chart from "@/components/charts/BondingCurve.vue";
import { curveParamsToHyperbolic } from "@/helpers/pools";
import BondingCurveParams from "@/components/ui/BondingCurveParams.vue";

export default {
  props: {
    emergingCurves: {
      type: Array,
      default: () => {
        return [];
      },
    },
    parameters: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
  components: {
    Chart,
    CardContainer,
    BondingCurveParams,
  },
  computed: {
    bondingCurve() {
      return curveParamsToHyperbolic(this.parameters);
    },
  },
};
</script>
