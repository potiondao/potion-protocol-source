<template>
  <CurrencyInput
    description="Your Balance:"
    :title="title"
    :value="value"
    @input="updateValue"
    :currency="stableCoinCollateral"
    :max-available-balance="stableCoinCollateralBalance"
    :error="error"
  />
</template>

<script>
import { mapGetters } from "vuex";
import CurrencyInput from "@/components/ui/CurrencyInput.vue";

export default {
  components: {
    CurrencyInput,
  },
  props: {
    value: {
      type: String,
      default: "0",
    },
    title: {
      type: String,
      default: "",
    },
    error: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    updateValue(value) {
      this.$emit("value-updated", value);
    },
  },
  computed: {
    ...mapGetters("wallet", [
      "stableCoinCollateral",
      "stableCoinCollateralBalance",
    ]),
  },
};
</script>
