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
    :class="{
      'overflow-hidden h-screen w-screen absolute inset-0':
        underlyingsModalOpened,
    }"
  >
    <MainHeader />
    <div class="container py-8 mx-auto">
      <CustomPoolCreationHeader :routes="customPoolRoutes" />
      <transition
        enter-active-class="transition-all "
        leave-active-class="transition-all"
        enter-class="opacity-0 "
        enter-to-class="opacity-100"
        leave-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <router-view />
      </transition>
    </div>
    <div
      class="transition"
      :class="{
        'absolute inset-0 z-50 w-screen h-screen bg-opacity-50 bg-deep-black-900 blurred':
          underlyingsModalOpened,
      }"
    ></div>
  </div>
</template>

<script>
import MainHeader from "../components/Header.vue";
import CustomPoolCreationHeader from "../components/cards/CustomPoolCreationHeader.vue";
import { mapGetters } from "vuex";

export default {
  components: {
    MainHeader,
    CustomPoolCreationHeader,
  },
  computed: {
    ...mapGetters("pools", ["customPoolRoutes"]),
    underlyingsModalOpened() {
      return this.$store.state.pools.customPool.underlyingsModalOpened;
    },
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
.blurred {
  backdrop-filter: blur(20px);
}
</style>
