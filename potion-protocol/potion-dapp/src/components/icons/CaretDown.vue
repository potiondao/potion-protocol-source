<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      d="M215 93a8 8 0 00-7-5H48a8 8 0 00-6 14l80 80a8 8 0 0012 0l80-80a8 8 0 001-9z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M208 96l-80 80-80-80"
      v-else
    />
  </svg>
</template>

<script>
import { weightValidator, weightToStroke } from "@/helpers/PhosphorIcons";

export default {
  props: {
    weight: {
      type: String,
      default: "regular",
      validator: weightValidator,
    },
  },
  computed: {
    strokeWidth() {
      return weightToStroke(this.weight);
    },
  },
};
</script>
