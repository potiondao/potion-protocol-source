<template>
  <div class="grid items-start w-full grid-cols-2 gap-4 lg:grid-cols-3">
    <QuantityInput
      key="custom-potion"
      class="col-span-2 lg:col-span-1"
      title="Choose Quantity (oToken)"
      v-model="quantity"
      @increase="increase"
      @decrease="decrease"
      footerDescription="Available Potions:"
      :footerValue="maxNumberOfOtokens.toString()"
      min="0.001"
      :max="maxNumberOfOtokens.toString()"
      :error="!validQuantity"
      :transactionsNumber="transactionsNumber"
      :focusEnabled="focusEnabled"
    />

    <div
      class="
        text-sm
        border border-white border-opacity-10
        rounded-3xl
        leading-none
        self-stretch
        flex flex-col
        justify-between
      "
    >
      <div class="p-4 flex justify-between w-full">
        <div>Price Per Potion</div>
        <p>
          {{ potionPrice }}
        </p>
      </div>
      <div class="p-4 flex justify-between w-full">
        <div>Quantity</div>
        <p>{{ quantity }}</p>
      </div>
      <div class="p-4 flex justify-between w-full text-secondary-500">
        <div>Total</div>
        <p>{{ totalPrice }}</p>
      </div>
      <SlippageSelector
        class="border-white border-opacity-10 border-t"
        @slippageSelected="slippageSelectedHandler"
        :currentSlippage="currentSlippage"
      />
    </div>
    <GasEstimationCard :gasUnits="getGasUnits" fiat-currency="$" />
  </div>
</template>

<script>
import QuantityInput from "@/components/ui/QuantityInput.vue";
import { mapActions, mapGetters } from "vuex";
import { debounce as _debounce } from "lodash-es";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";
import { CurrencyService } from "@/services/api/currency";
import { getGas } from "@/services/api/gas";

import SlippageSelector from "@/components/blocks/SlippageSelector.vue";
import { formatNumber } from "@/helpers";

export default {
  components: {
    QuantityInput,
    GasEstimationCard,
    SlippageSelector,
  },
  props: {
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      quantity: "0.001",
      gasUnits: "21000",
      focusEnabled: false,
      ethPrice: 0,
      gasInGwei: null,
    };
  },
  async mounted() {
    this.updateQuantity(this.quantity);
    await this.updateEthPrice();
    await this.updateGasPrice();
    await this.getPoolsFromUnderlying();
    await this.runRouter({
      orderSize: this.orderSize,
      gasInWei: this.gasInWei,
      ethPrice: this.ethPrice,
    });
    this.focusEnabled = true;
  },
  watch: {
    quantity: {
      handler: _debounce(async function () {
        this.updateQuantity(this.quantity);
        this.focusEnabled = false;
        await this.updatePremium();
        this.focusEnabled = true;
      }, 300),
    },
  },
  computed: {
    ...mapGetters("potions/custom", [
      "premiumPerPotion",
      "orderSize",
      "validQuantity",
      "getGasUnits",
      "maxNumberOfOtokens",
      "transactionsNumber",
      "premium",
    ]),
    ...mapGetters("potions", ["currentSlippage"]),
    gasInWei() {
      return this.gasInGwei.ProposeGasPrice * 10e8;
    },
    totalPrice() {
      if (typeof this.premium === "number") {
        return `${formatNumber(this.premium)} ${this.stableCoinCollateral}`;
      }
      return this.premium;
    },
    potionPrice() {
      if (typeof this.premiumPerPotion === "number") {
        return `${formatNumber(this.premiumPerPotion)} ${
          this.stableCoinCollateral
        }`;
      } else {
        return this.premiumPerPotion;
      }
    },
    floatQuantity() {
      return parseFloat(this.quantity);
    },
  },
  methods: {
    ...mapActions("potions/custom", [
      "updateQuantity",
      "getPoolsFromUnderlying",
      "runRouter",
    ]),
    ...mapActions("potions", ["selectSlippage"]),

    slippageSelectedHandler(payload) {
      this.selectSlippage(payload);
      this.slippage = payload;
    },
    async updateEthPrice() {
      this.ethPrice = await CurrencyService.getEthToUsd();
    },
    async updateGasPrice() {
      this.gasInGwei = await getGas();
    },
    async updatePremium() {
      if (this.floatQuantity > 0) {
        await this.updateEthPrice();
        await this.updateGasPrice();
        await this.runRouter({
          orderSize: this.orderSize,
          gasInWei: this.gasInWei,
          ethPrice: this.ethPrice,
        });
      }
    },
    increase() {
      this.quantity = (this.floatQuantity + 0.001).toFixed(3);
    },
    decrease() {
      if (this.floatQuantity > 0) {
        this.quantity = (this.floatQuantity - 0.001).toFixed(3);
      }
    },
  },
};
</script>
<style scoped>
.arrowless::-webkit-outer-spin-button,
.arrowless::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
  -moz-appearance: textfield;
}
</style>
