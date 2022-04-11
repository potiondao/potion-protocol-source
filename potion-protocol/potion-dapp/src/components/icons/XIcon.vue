<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      class="fill-current"
      d="M139.313 128l66.344-66.343a8 8 0 00-11.314-11.314L128 116.687 61.657 50.343a8 8 0 00-11.314 11.314L116.687 128l-66.344 66.343a8 8 0 1011.314 11.314L128 139.313l66.343 66.344a8 8 0 0011.314-11.314z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M200 56L56 200M200 200L56 56"
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
