<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      class="fill-current"
      d="M80.344 115.668A8 8 0 0186 102.011h34V40a8 8 0 0116 0v62.01h34a8 8 0 015.656 13.658l-42 41.99a8 8 0 01-11.312 0zM216 144a8 8 0 00-8 8v56H48v-56a8 8 0 00-16 0v56a16.018 16.018 0 0016 16h160a16.018 16.018 0 0016-16v-56a8 8 0 00-8-8z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M86 110.011L128 152l42-41.989M128 40v111.971M216 152v56a8 8 0 01-8 8H48a8 8 0 01-8-8v-56"
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
