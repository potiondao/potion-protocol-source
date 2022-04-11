<template>
  <div class="flex w-full space-x-4 uppercase font-bold text-xs">
    <template v-for="route in routes">
      <router-link
        class="text-dirty-white-300"
        :key="`enabled-${route.name}`"
        :to="route"
        v-if="route.alwaysVisible || enableUserRoute"
      >
        {{ route.label }}
        <div
          v-if="routeName === route.name"
          class="w-1/2 mt-2 h-[3px] bg-primary-500 bg-opacity-100"
        ></div>
      </router-link>
      <span
        class="text-opacity-50 text-dirty-white-300"
        :key="`disabled-${route.name}`"
        v-else
        >{{ route.label }}</span
      >
    </template>
  </div>
</template>

<script>
export default {
  props: {
    enableUserRoute: {
      type: Boolean,
      default: true,
    },
    routeName: {
      type: String,
      default: "",
    },
    routes: {
      type: Array,
      default: () => [],
    },
  },
};
</script>
