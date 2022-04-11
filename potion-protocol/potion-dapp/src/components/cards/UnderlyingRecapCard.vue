<template>
  <CardContainer
    :full-height="false"
    rounded="internal"
    color="no-bg"
    class="p-3"
  >
    <div
      class="
        grid grid-cols-3
        gap-3
        mb-3
        text-sm
        font-medium
        text-center text-xs
      "
    >
      <span class="text-left">Asset</span>
      <span>Max Strike</span>
      <span>Max Duration</span>
    </div>
    <div class="grid grid-cols-3 gap-x-3 gap-y-6 font-semibold text-center">
      <template v-for="underlying in underlyings">
        <span
          class="inline-flex items-center"
          :key="`underlying-icon-${underlying.symbol}`"
        >
          <TokenIcon
            :name="underlying.name"
            :image="underlying.image"
            :address="underlying.address"
            class="mr-2"
            size="base"
          />
          {{ underlying.symbol }}
        </span>
        <span :key="`underlying-strike-${underlying.symbol}`">{{
          percentage(underlying.strike)
        }}</span>
        <span :key="`underlying-duration-${underlying.symbol}`">{{
          duration(underlying.duration)
        }}</span>
      </template>
    </div>
  </CardContainer>
</template>

<script>
import { formatRelativeDate } from "@/helpers";
import CardContainer from "@/components/ui/CardContainer.vue";
import TokenIcon from "@/components/icons/TokenIcon.vue";

export default {
  props: {
    underlyings: {
      type: Array,
      default: () => [],
    },
  },
  components: {
    CardContainer,
    TokenIcon,
  },
  methods: {
    percentage(value) {
      return `${value}%`;
    },
    duration(days) {
      return formatRelativeDate(days);
    },
  },
};
</script>
