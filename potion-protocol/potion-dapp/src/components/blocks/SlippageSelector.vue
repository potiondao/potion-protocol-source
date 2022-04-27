<template>
  <div class="px-4 py-3 rounded-3xl">
    <div class="mb-3 text-base">Slippage Tolerance</div>
    <div class="flex gap-2">
      <button
        v-for="option in options"
        :key="option"
        class="
          transition-colors
          rounded-md
          px-1.5
          pt-1
          outline-none
          focus:outline-none
        "
        :class="{
          'bg-primary-500': option === currentSlippage,
          'bg-white bg-opacity-10': option !== currentSlippage,
        }"
        @click="slippageSelection(option)"
      >
        {{ option }}%
      </button>
    </div>
  </div>
</template>
<script lang="ts">
export default {
  props: {
    currentSlippage: {
      type: String,
      default: "0.5",
    },
  },
  data() {
    return {
      options: ["0.5", "2", "5"],
    };
  },
  methods: {
    slippageSelection(slippage) {
      this.$emit("slippageSelected", slippage);
    },
  },
};
</script>
