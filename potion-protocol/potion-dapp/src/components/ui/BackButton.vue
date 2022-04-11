<template>
  <button @click="$emit('click')" class="flex items-center space-x-1">
    <BackIcon />
    <span class="text-xs font-extrabold uppercase">Back</span>
  </button>
</template>

<script>
import BackIcon from "../icons/BackIcon.vue";
export default {
  components: {
    BackIcon,
  },
};
</script>

<style lang="scss" scoped></style>
