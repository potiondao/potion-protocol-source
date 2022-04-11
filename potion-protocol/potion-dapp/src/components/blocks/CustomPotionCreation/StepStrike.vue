<template>
  <div class="flex justify-center w-full">
    <div
      class="
        w-full
        border border-white
        lg:w-1/2
        border-opacity-10
        rounded-3xl
        box-content
      "
    >
      <div class="flex justify-between w-full p-4 mb-6 text-sm">
        <div class="flex items-center space-x-1">
          <TokenIcon
            :address="potionNew.underlyingSelected.address"
            :name="potionNew.underlyingSelected.name"
            size="sm"
          />
          <div>Current Price</div>
        </div>
        <Value
          :value="potionNew.underlyingSelected.price"
          :symbol="stableCoinCollateral"
        ></Value>
      </div>

      <div class="relative z-50 w-full">
        <Input
          :tagLabel="stableCoinCollateral"
          title="Your Strike Price"
          footerDescription="Max Strike Price:"
          step="0.001"
          :value="strikeSelected"
          :error="!validStrikePrice"
          :footerValue="footerValue"
          :focus="inputFocus"
          @input="updateStrikeSelected"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { debounce as _debounce } from "lodash-es";
import { formatNumber } from "@/helpers";
import Input from "@/components/ui/InputWithFooter.vue";
import Value from "@/components/ui/Value.vue";
import TokenIcon from "@/components/icons/TokenIcon";

export default {
  components: {
    Input,
    TokenIcon,
    Value,
  },
  props: {
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      inputFocus: false,
      strikeSelected: "",
    };
  },
  mounted() {
    this.strikeSelected = parseFloat(
      this.potionNew.underlyingSelected.price
    ).toFixed(3);
    this.selectStrike(this.strikeSelected);
    this.setInputFocus();
  },
  watch: {
    strikeSelected: {
      handler: _debounce(async function () {
        this.selectStrike(this.strikeSelected);
        if (this.validStrikePrice) {
          await this.getSimilarPotions("strike");
        }
      }, 300),
    },
  },
  methods: {
    ...mapActions("potions/custom", ["selectStrike", "getSimilarPotions"]),
    setInputFocus() {
      this.inputFocus = !this.inputFocus;
    },
    updateStrikeSelected(value) {
      this.strikeSelected = value;
    },
  },
  computed: {
    ...mapGetters("potions/custom", ["strikePriceMax", "validStrikePrice"]),
    potionNew() {
      return this.$store.state.potions.custom;
    },
    footerValue() {
      return `${formatNumber(this.strikePriceMax)} ${
        this.stableCoinCollateral
      }`;
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
.blurred {
  backdrop-filter: blur(50px);
}
::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}
::-webkit-scrollbar-thumb {
  /* background: linear-gradient(0deg, #e373ac 0%, #fa198b 100%); */
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
  border-radius: 15px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
}
::-webkit-scrollbar-track {
  /* background: #d1d1d1;
  border-radius: 15px;
  box-shadow: inset -9px 0px 15px #ffffff; */
  @apply bg-white bg-opacity-0 rounded-full;
  backdrop-filter: blur(30px);
}
</style>
