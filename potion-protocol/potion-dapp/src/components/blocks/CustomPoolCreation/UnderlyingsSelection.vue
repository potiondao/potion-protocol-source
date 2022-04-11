<template>
  <div class="grid gap-3">
    <UnderlyingCard
      class="flex flex-col items-center px-4 py-3 cursor-pointer w-[80px]"
      v-for="(underlying, index) in underlyings"
      :key="index"
      @underlying-selected="selectedUnderlying"
      :symbol="underlying.symbol"
      :name="underlying.name"
      :address="underlying.address"
      :image="underlying.image"
      :active="underlying.selected"
    />
  </div>
</template>

<script>
import UnderlyingCard from "@/components/cards/UnderlyingCard.vue";

export default {
  components: {
    UnderlyingCard,
  },
  props: {
    underlyings: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    selectedUnderlying(address) {
      this.$emit("underlying-selected", address);
    },
  },
};
</script>

<style scoped>
.grid {
  grid-template-columns: repeat(auto-fill, 4.45rem);
}
</style>
