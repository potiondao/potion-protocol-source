<template>
  <CardContainer
    class="fixed inset-x-0 bottom-0 p-5 border-0 border-t"
    :full-height="false"
    rounded="none"
  >
    <div class="container flex flex-col w-full mx-auto">
      <div class="w-full flex items-start justify-between mb-4">
        <Tag :address="oToken.address" direction="horizzontal" />
        <Btn color="transparent" label="" size="icon" @click="closeModal">
          <template v-slot:pre-icon>
            <XIcon class="h-4" weight="bold" />
          </template>
        </Btn>
      </div>
      <div class="w-full flex items-start justify-between">
        <LabelTokens title="Asset" :tokens="[underlying]" labelSize="lg" />
        <LabelValue
          title="Strike Price"
          :value="oToken.strikePrice"
          :symbol="stableCoinCollateral"
        />
        <LabelValue
          valueType="timestamp"
          title="Expiration"
          :value="oToken.expirationUnix"
        />
        <Btn
          label="Buy Potion"
          color="secondary"
          @click="buyAndCloseModal"
          :disabled="disableBuy"
        />
      </div>
    </div>
    <div
      class="
        container
        grid grid-cols-2
        gap-5
        mx-auto
        transition-all
        lg:grid-cols-3
        py-5
        mt-5
        h-[500px]
        lg:h-auto
        overflow-y-scroll
        lg:overflow-y-auto
        border-t border-dirty-white-300 border-opacity-10
      "
    >
      <div class="col-span-2 lg:hidden">
        <BuyPotion
          :transactionsNumber="transactionsNumber"
          :price="premiumPerPotion"
          :focusEnabled="focusEnabled"
          :maxNumberOfOtokens="maxNumberOfOtokens"
          :error="disableBuy"
          :value="value"
          :premium="premium"
          :currentSlippage="currentSlippage"
          @input.native="updateQuantity($event.target.value)"
          @slippageSelected="slippageSelected"
          @increase="increase"
          @decrease="decrease"
        />
      </div>
      <OrderBook :orderHistory="oToken.orderHistory" />
      <GasEstimationCard fiat-currency="$" :gasUnits="gasUnits" />

      <div class="hidden lg:block">
        <BuyPotion
          :transactionsNumber="transactionsNumber"
          :focusEnabled="focusEnabled"
          :price="premiumPerPotion"
          :maxNumberOfOtokens="maxNumberOfOtokens"
          :error="disableBuy"
          :value="value"
          :premium="premium"
          :currentSlippage="currentSlippage"
          :stable-coin-collateral="stableCoinCollateral"
          @input.native="updateQuantity($event.target.value)"
          @slippageSelected="slippageSelected"
          @increase="increase"
          @decrease="decrease"
        />
      </div>
    </div>
  </CardContainer>
</template>

<script>
import Btn from "@/components/ui/Button.vue";
import BuyPotion from "@/components/cards/BuyPotion.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";

import LabelTokens from "@/components/blocks/LabelTokens.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import OrderBook from "@/components/cards/OrderBook.vue";
import Tag from "@/components/blocks/OptionAdressTag.vue";
import XIcon from "@/components/icons/XIcon.vue";

export default {
  components: {
    Btn,
    BuyPotion,
    CardContainer,
    GasEstimationCard,
    LabelTokens,
    LabelValue,
    OrderBook,
    Tag,
    XIcon,
  },
  props: {
    transactionsNumber: {
      type: Number,
      default: 0,
    },
    value: {
      type: String,
      default: "0.001",
    },
    oToken: {
      type: Object,
      default: () => {
        return {
          address: "",
          strikePrice: "",
          expirationUnix: "",
          orderHistory: [],
        };
      },
    },
    status: {
      type: String,
      default: "pending",
    },
    underlying: {
      type: Object,
      default: () => {
        return {
          address: "",
          name: "",
          image: "",
          price: "",
          symbol: "",
        };
      },
    },
    currentSlippage: {
      type: String,
      default: "0",
    },
    premium: {
      type: [String, Number],
      default: "0",
    },
    premiumPerPotion: {
      type: [String, Number],
      default: "0",
    },
    orderSize: {
      type: Number,
      default: 0,
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    disableBuy: {
      type: Boolean,
      default: false,
    },
    maxNumberOfOtokens: {
      type: Number,
      default: 100,
    },
    gasUnits: {
      type: String,
      default: "21700",
    },
    focusEnabled: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    updateQuantity(value) {
      this.$emit("input", value);
    },
    increase(value) {
      this.$emit("input", value);
    },
    decrease(value) {
      this.$emit("input", value);
    },
    slippageSelected(payload) {
      this.$emit("slippage-selected", payload);
    },
    buyAndCloseModal() {
      this.$emit("buy-and-close-modal");
    },
    closeModal() {
      this.$emit("close");
    },
  },
};
</script>
