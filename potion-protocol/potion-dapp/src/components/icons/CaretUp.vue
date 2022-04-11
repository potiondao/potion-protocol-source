<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      d="M214 154l-80-80a8 8 0 00-12 0l-80 80a8 8 0 006 14h160a8 8 0 006-14z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M48 160l80-80 80 80"
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
