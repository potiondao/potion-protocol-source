<template>
  <div class="flex flex-wrap space-x-2">
    <div
      class="
        inline-flex
        alig-center
        justify-center
        rounded-3xl
        py-2
        px-4
        mb-2
        filter
        cursor-pointer
      "
      v-for="filter in filters"
      :key="filter.name"
      @click="$emit('filter-selected', filter.name)"
      :class="filterClass(filter.selected)"
    >
      {{ filter.label }}
    </div>
  </div>
</template>

<script>
export default {
  props: {
    filters: {
      type: Array,
      default: () => [
        {
          label: "All",
          name: "all",
          selected: true,
        },
        {
          label: "Crypto Natives",
          name: "crypto-natives",
          selected: false,
        },
        {
          label: "Lending Protocol",
          name: "lending-protocol",
          selected: false,
        },
        {
          label: "AMM Dex",
          name: "amm-dex",
          selected: false,
        },
        {
          label: "Oracles",
          name: "oracles",
          selected: false,
        },
        {
          label: "Traditional Finance",
          name: "traditional-finance",
          selected: false,
        },
      ],
    },
  },
  methods: {
    filterClass(selected) {
      return selected
        ? "bg-primary-500"
        : "border border-white border-opacity-10";
    },
  },
};
</script>

<style scoped>
.filter {
  min-width: 2.75rem;
  font-size: 0.75rem;
}
</style>
