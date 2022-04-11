<template>
  <CardContainer color="no-bg">
    <CardBody class="px-6 py-6 font-medium max-h-[500px] overflow-y-auto">
      <div class="pb-6 flex items-center">Orderbook</div>
      <div
        class="
          flex
          justify-between
          w-full
          mb-4
          py-2
          border-t border-b border-white border-opacity-10
        "
      >
        <span>Timestamp</span>
        <span>Quantity</span>
      </div>
      <div
        class="flex justify-between py-4"
        v-for="(item, index) in orderHistory"
        :key="'order-item-' + index"
      >
        <span>{{ dateFormatter(item.timestamp) }}</span>
        <span>{{ item.numberOfOTokens }}</span>
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import dayjs from "dayjs";
export default {
  components: {
    CardContainer,
    CardBody,
  },
  props: {
    orderHistory: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    dateFormatter(date) {
      return dayjs.unix(date).format("ll");
    },
  },
};
</script>
