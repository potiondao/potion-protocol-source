<template>
  <div
    class="
      flex flex-col
      items-center
      justify-center
      w-full
      px-8
      py-4
      rounded-b-3xl
    "
    :class="{ 'radial-bg border-white border-opacity-5 border-t': glass }"
  >
    <slot />
  </div>
</template>

<script>
export default {
  props: {
    glass: {
      type: Boolean,
      default: true,
    },
  },
};
</script>
<style scoped>
.radial-bg {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(67, 60, 104, 0.3) 0%,
    rgba(67, 60, 104, 0.05) 100%
  );
}
</style>
