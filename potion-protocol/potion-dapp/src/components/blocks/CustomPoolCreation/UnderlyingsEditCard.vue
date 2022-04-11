<template>
  <CardContainer class="w-full p-6" :full-height="false">
    <div class="grid grid-flow-row grid-cols-1 gap-6">
      <UnderlyingsSelection
        :underlyings="underlyings"
        @underlying-selected="underlyingSelected"
      />
      <div
        class="w-full h-px bg-deep-black-600"
        v-if="selectedUnderlyings.length > 0"
      ></div>
      <UnderlyingOptions
        v-for="(underlying, index) in selectedUnderlyings"
        :key="`${index}-${underlying.address}`"
        :underlying="underlying"
        :current-price="getUnderlyingPrice(underlying)"
        @close-underlying-selected="underlyingSelected"
        @underlying-updated="underlyingUpdated"
      />
    </div>
  </CardContainer>
</template>

<script>
import UnderlyingsSelection from "@/components/blocks/CustomPoolCreation/UnderlyingsSelection.vue";
import UnderlyingOptions from "@/components/blocks/CustomPoolCreation/UnderlyingOptions.vue";
import CardContainer from "@/components/ui/CardContainer.vue";

export default {
  props: {
    underlyings: {
      type: Array,
      default: () => [],
    },
    selectedUnderlyings: {
      type: Array,
      default: () => [],
    },
    underlyingsPrices: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
  components: {
    UnderlyingsSelection,
    UnderlyingOptions,
    CardContainer,
  },
  methods: {
    getUnderlyingPrice(underlying) {
      return underlying.price || this.underlyingsPrices[underlying.address];
    },
    underlyingSelected(address) {
      this.$emit("underlying-selected", address);
    },
    underlyingUpdated(data) {
      this.$emit("underlying-updated", data);
    },
  },
};
</script>
