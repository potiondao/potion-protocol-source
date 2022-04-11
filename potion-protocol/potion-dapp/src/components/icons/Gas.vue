<template>
  <svg class="stroke-current" viewBox="0 0 256 256" @click="$emit('click')">
    <path
      class="fill-current"
      d="m240.97 69.656-19.313-19.313a8 8 0 1 0-11.314 11.314l19.313 19.313A7.948 7.948 0 0 1 232 86.627V168a8 8 0 0 1-16 0v-40a24.027 24.027 0 0 0-24-24h-16V56a24.027 24.027 0 0 0-24-24H72a24.027 24.027 0 0 0-24 24v152H32a8 8 0 0 0 0 16h160a8 8 0 0 0 0-16h-16v-88h16a8.01 8.01 0 0 1 8 8v40a24 24 0 0 0 48 0V86.627a23.845 23.845 0 0 0-7.03-16.97ZM144 120H80a8 8 0 0 1 0-16h64a8 8 0 0 1 0 16Z"
      v-if="weight === 'fill'"
    />
    <path
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      :stroke-width="strokeWidth"
      d="M56 216V56a16 16 0 0 1 16-16h80a16 16 0 0 1 16 16v160M32 216h160M168 112h24a16 16 0 0 1 16 16v40a16 16 0 0 0 16 16h4a16 16 0 0 0 16-16V86.627a16 16 0 0 0-4.686-11.313L220 56M128 112H96"
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
