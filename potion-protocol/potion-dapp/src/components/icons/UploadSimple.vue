<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      class="fill-current"
      d="M78.609 85.05a7.999 7.999 0 011.735-8.718l42-41.99a8 8 0 0111.312 0l42 41.99A8 8 0 01170 89.989h-34V152a8 8 0 01-16 0V89.99H86a7.999 7.999 0 01-7.391-4.94zM216 144a8 8 0 00-8 8v56H48v-56a8 8 0 00-16 0v56a16.018 16.018 0 0016 16h160a16.018 16.018 0 0016-16v-56a8 8 0 00-8-8z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M86 81.989L128 40l42 41.989M128 152V40.029M216 152v56a8 8 0 01-8 8H48a8 8 0 01-8-8v-56"
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
