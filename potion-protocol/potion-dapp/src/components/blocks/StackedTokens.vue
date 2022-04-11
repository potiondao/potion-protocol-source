<template>
  <div class="flex">
    <token-icon
      v-for="(token, index) in tokens"
      :key="`card-tokens-${index}`"
      :size="size"
      class="rounded-full bg-deep-black-700"
      :class="index > 0 ? '-ml-3' : ''"
      :address="token.address"
      :name="token.name"
    />
  </div>
</template>

<script>
import TokenIcon from "../icons/TokenIcon.vue";
export default {
  components: {
    TokenIcon,
  },
  props: {
    tokens: {
      type: Array,
      required: true,
    },
    size: {
      type: String,
      default: "md",
    },
  },
};
</script>
