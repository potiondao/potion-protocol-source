<template>
  <CardContainer color="no-bg" class="pb-6 font-medium" :fullHeight="false">
    <div class="px-6 pt-6 pb-6 flex">
      <GasIcon weight="fill" class="w-4 mr-[.5ch]"></GasIcon
      ><span>Gas Estimation</span>
    </div>
    <div
      class="grid grid-cols-4 gap-3 text-sm leading-none"
      v-if="gas !== null"
    >
      <span class="ml-6 text-left capitalize">Rapid</span>
      <span class="text-center font-bold">{{ gas.FastGasPrice }}</span>
      <span class="text-center">{{
        formatPrice(
          ((gweiToWei(gas.FastGasPrice) * parseFloat(gasUnits)) / 1e18) *
            ethPrice
        )
      }}</span>
      <span
        class="mr-6 text-right text-deep-black-500 text-opacity-50 text-xs"
        >{{ timeEstimations[0] }}</span
      >
      <div class="h-px bg-white opacity-10 col-span-4"></div>
      <span class="ml-6 text-left capitalize">Fast</span>
      <span class="text-center font-bold">{{ gas.ProposeGasPrice }}</span>
      <span class="text-center">{{
        formatPrice(
          ((gweiToWei(gas.ProposeGasPrice) * parseFloat(gasUnits)) / 1e18) *
            ethPrice
        )
      }}</span>
      <span
        class="mr-6 text-right text-deep-black-500 text-opacity-50 text-xs"
        >{{ timeEstimations[1] }}</span
      >
      <div class="h-px bg-white opacity-10 col-span-4"></div>
      <span class="ml-6 text-left capitalize">Standard</span>
      <span class="text-center font-bold">{{ gas.SafeGasPrice }}</span>
      <span class="text-center">{{
        formatPrice(
          ((gweiToWei(gas.SafeGasPrice) * parseFloat(gasUnits)) / 1e18) *
            ethPrice
        )
      }}</span>
      <span
        class="mr-6 text-right text-deep-black-500 text-opacity-50 text-xs"
        >{{ timeEstimations[2] }}</span
      >
      <div class="h-px bg-white opacity-10 col-span-4"></div>
      <span class="ml-6 text-left capitalize">Slow</span>
      <span class="text-center font-bold">{{
        parseFloat(gas.suggestBaseFee).toFixed(0)
      }}</span>
      <span class="text-center">{{
        formatPrice(
          ((gweiToWei(gas.suggestBaseFee) * parseFloat(gasUnits)) / 1e18) *
            ethPrice
        )
      }}</span>
      <span
        class="mr-6 text-right text-deep-black-500 text-opacity-50 text-xs"
        >{{ timeEstimations[3] }}</span
      >
    </div>
    <div class="px-6" v-else>Loading...</div>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import { CurrencyService } from "@/services/api/currency";
import { getGas } from "@/services/api/gas";
import GasIcon from "@/components/icons/Gas.vue";

export default {
  props: {
    gasUnits: {
      type: String,
      default: "21000",
    },
    fiatCurrency: {
      type: String,
      default: "$",
    },
  },
  data() {
    return {
      gas: null,
      ethPrice: null,
      timeEstimations: ["15sec", "1min", "3min", ">10min"],
    };
  },
  components: {
    CardContainer,
    GasIcon,
  },
  methods: {
    formatPrice(price) {
      return `${price.toFixed(2)}${this.fiatCurrency}`;
    },
    getGweiPrice(gwei) {
      return this.formatPrice(gwei * this.gweiPrice);
    },
    weiToGwei(wei) {
      return (wei / 10e8).toFixed(0);
    },
    gweiToWei(gwei) {
      return parseFloat((gwei * 10e8).toFixed(0));
    },
  },
  async mounted() {
    this.ethPrice = await CurrencyService.getEthToUsd();
    this.gas = await getGas();
  },
};
</script>
<style scoped>
.emoji {
  height: 24px;
  width: auto;
}
</style>
