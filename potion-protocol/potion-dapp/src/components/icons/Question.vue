<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      class="fill-current"
      d="M128 24a104 104 0 10104 104A104 104 0 00128 24zm0 168a12 12 0 1112-12 12 12 0 01-12 12zm8-49v1a8 8 0 11-16 0v-8a8 8 0 018-8 20 20 0 10-20-20 8 8 0 01-16 0 36 36 0 1144 35z"
      v-if="weight === 'fill'"
    />
    <g v-else>
      <circle
        cx="128"
        cy="128"
        r="96"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        :stroke-width="strokeWidth"
      />
      <circle class="fill-current" cx="128" cy="180" :r="dotSize" />
      <path
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M128 144v-8a28 28 0 10-28-28"
        :stroke-width="strokeWidth"
      />
    </g>
  </svg>
</template>

<script>
import { weightValidator, weightToStroke } from "@/helpers/PhosphorIcons";
const weightToDotSize = {
  bold: 16,
  light: 10,
  thin: 8,
  regular: 12,
};

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
    dotSize() {
      return weightToDotSize[this.weight];
    },
  },
};
</script>
