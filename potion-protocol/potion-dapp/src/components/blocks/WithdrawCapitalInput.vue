<template>
  <CurrencyInput
    description="Unutilized capital:"
    :title="title"
    :value="value"
    @input="updateValue"
    :currency="currency"
    :max-available-balance="unlockedCapital.toString()"
    :disable-external-border="disableExternalBorder"
    :onlyTopBorder="onlyTopBorder"
    :error="error"
  />
</template>

<script>
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
    unlockedCapital: {
      type: [String, Number],
      default: "0",
    },
    currency: {
      type: String,
      default: "",
    },
    disableExternalBorder: {
      type: Boolean,
      default: false,
    },
    error: {
      type: Boolean,
      default: false,
    },
    onlyTopBorder: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    updateValue(value) {
      this.$emit("value-updated", value);
    },
  },
};
</script>
