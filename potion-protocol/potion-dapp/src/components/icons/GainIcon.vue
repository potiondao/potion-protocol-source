<template>
  <svg
    class="block stroke-current"
    :class="grow === 'down' ? 'text-secondary-500' : 'text-accent-500 mirror-v'"
    width="32"
    height="32"
    viewBox="0 0 32 32"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M29.0002 25L17.0002 13L12.0002 18L3.00024 9"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M29.0002 17V25H21.0002"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script>
export default {
  props: {
    grow: {
      type: String,
      validator: function (value) {
        return ["up", "down"].indexOf(value) !== -1;
      },
    },
  },
};
</script>

<style scoped>
.mirror-v {
  transform: scale(1, -1);
}
</style>
