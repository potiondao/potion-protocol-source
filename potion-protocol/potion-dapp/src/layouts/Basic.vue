<template>
  <div
    class="
      min-h-screen
      px-6
      py-5
      md:px-12
      basic
      font-poppins
      text-dirty-white-300
    "
  >
    <MainHeader></MainHeader>
    <transition
      enter-active-class="transition-all "
      leave-active-class="transition-all"
      enter-class="opacity-0 "
      enter-to-class="opacity-100"
      leave-class="opacity-100"
      leave-to-class="opacity-0 "
    >
      <router-view />
    </transition>
  </div>
</template>

<script>
import MainHeader from "../components/Header.vue";

export default {
  props: {},
  components: {
    MainHeader,
  },
};
</script>

<style scoped>
.basic {
  background: linear-gradient(
    113.69deg,
    var(--deep-blue) 23.72%,
    var(--deep-black-900) 81.45%
  );
}
</style>
