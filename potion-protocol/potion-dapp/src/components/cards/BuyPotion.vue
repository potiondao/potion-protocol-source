<template>
  <CardContainer color="no-bg">
    <CardBody class="px-6 py-6 font-medium">
      <div class="mb-6">Buy Potion</div>
      <div class="flex justify-between w-full text-base mb-4">
        <span>Price per Potion</span>
        <span>{{ formattedPrice }}</span>
      </div>
      <QuantityInput
        key="statusBar"
        title="Choose Quantity"
        :value="value"
        :focusEnabled="focusEnabled"
        @input.native="updateQuantity($event.target.value)"
        @increase="increase((parseFloat(value) + 0.001).toFixed(3))"
        @decrease="decrease((parseFloat(value) - 0.001).toFixed(3))"
        footerDescription="Available Potions:"
        min="0.001"
        :max="maxNumberOfOtokens.toString()"
        :error="error"
        :transactionsNumber="transactionsNumber"
      />
      <div class="flex justify-between text-secondary-500 mt-4">
        <span class="">Total</span>
        <span class="font-bold">{{ formattedPremium }}</span>
      </div>
      <SlippageSelector
        class="border border-white border-opacity-10 mt-4"
        @slippageSelected="slippageSelectedHandler"
        :currentSlippage="currentSlippage"
      />
    </CardBody>
  </CardContainer>
</template>

<script>
import QuantityInput from "@/components/ui/QuantityInput.vue";
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import SlippageSelector from "@/components/blocks/SlippageSelector.vue";
import { formatNumber } from "@/helpers";

export default {
  components: {
    QuantityInput,
    CardContainer,
    CardBody,
    SlippageSelector,
  },
  props: {
    price: {
      type: [Number, String],
      default: 0,
    },
    value: {
      type: String,
      default: "0",
    },
    premium: {
      type: [Number, String],
      default: "0",
    },
    currentSlippage: {
      type: String,
      default: "0.5",
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    maxNumberOfOtokens: {
      type: Number,
      default: 100,
    },
    error: {
      type: Boolean,
      default: false,
    },
    transactionsNumber: {
      type: Number,
      default: 1,
    },
    focusEnabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    formattedPrice() {
      if (typeof this.price === "number") {
        return `${formatNumber(this.price.toString())} ${
          this.stableCoinCollateral
        }`;
      }
      return "Select a quantity";
    },
    formattedPremium() {
      if (typeof this.premium === "number") {
        return `${formatNumber(this.premium.toString())} ${
          this.stableCoinCollateral
        }`;
      }
      return this.premium;
    },
  },

  methods: {
    increase(value) {
      this.$emit("increase", value);
    },
    decrease(value) {
      this.$emit("decrease", value);
    },
    updateQuantity(quantity) {
      this.$emit("input", quantity);
    },
    slippageSelectedHandler(payload) {
      this.$emit("slippageSelected", payload);
    },
  },
};
</script>
