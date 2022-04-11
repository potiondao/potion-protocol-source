<template>
  <CardContainer class="w-full p-6">
    <div class="flex items-center justify-between mb-4">
      <Title label="Create Pool" size="xs" class="uppercase" />
      <XIcon
        class="cursor-pointer h-4"
        @click="$router.push({ name: 'MyPools' })"
      />
    </div>
    <div
      class="grid md:grid-flow-col auto-cols-max justify-center my-6 gap-7 px-8"
    >
      <template v-for="(route, index) in routes">
        <router-link
          :key="`completed-${route.name}`"
          v-if="completedRoute(route, index)"
          class="
            pb-2.5
            border-b-2
            transition-all
            duration-300
            text-sm
            w-180px
            text-center
            uppercase
          "
          :class="
            currentRoute.name === route.name
              ? 'border-primary-500'
              : 'border-opacity-10 border-white'
          "
          :to="route"
        >
          <span class="flex items-center justify-center">
            {{ route.label }}
            <CheckIcon class="inline ml-2"
          /></span>
        </router-link>
        <span
          v-else
          :key="`not-completed-${route.name}`"
          class="
            pb-2.5
            border-b-2
            transition-all
            duration-300
            text-sm
            w-180px
            text-center
            uppercase
          "
          :class="
            currentRoute.name === route.name
              ? 'border-primary-500'
              : 'border-opacity-10 border-white'
          "
        >
          {{ route.label }}
        </span>
      </template>
    </div>
    <div class="text-center flex flex-col px-12">
      {{ currentRoute.description }}
      <a
        v-if="currentRoute.moreInfo"
        :href="currentRoute.moreInfo.url"
        :title="currentRoute.moreInfo.label"
        class="uppercase text-secondary-500 hover:text-secondary-600 text-xs"
        >{{ currentRoute.moreInfo.label }}</a
      >
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CheckIcon from "@/components/icons/CheckIcon.vue";
import XIcon from "@/components/icons/XIcon.vue";
import Title from "@/components/ui/Title.vue";
import { find as _find } from "lodash-es";

export default {
  props: {
    routes: {
      type: Array,
      default: () => [],
    },
  },
  components: { CardContainer, XIcon, CheckIcon, Title },
  methods: {
    completedRoute(route, index) {
      if (index < this.currentRouteIndex) {
        return route.completed;
      }
      return false;
    },
  },
  computed: {
    currentRoute() {
      return _find(this.routes, (r) => r.name === this.$route.name);
    },
    currentRouteIndex() {
      return this.routes.indexOf(this.currentRoute);
    },
  },
};
</script>
