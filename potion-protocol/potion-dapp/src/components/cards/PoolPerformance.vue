<template>
  <CardContainer :fullHeight="false">
    <CardBody class="p-6">
      <div class="flex justify-between w-full">
        <Dropdown
          title="Enable/disable"
          :items="datasets"
          :items-selected-status="visibility"
          @dropdown-item-selected="selectDataset"
        />
        <div class="inline-flex items-center bg-white rounded-lg bg-opacity-10">
          <div
            class="px-7 h-full py-1.5 text-center text-xs cursor-pointer"
            :class="{
              'rounded-lg bg-gradient-to-r from-primary-500 to-primary-400 text-dirty-white-300':
                interval.name === selectedInterval,
            }"
            v-for="interval in intervals"
            :key="interval.name"
            @click="selectInterval(interval.name)"
          >
            {{ interval.label }}
          </div>
        </div>
      </div>

      <PerformanceChart
        :performance-data="performanceData"
        :today-timestamp="todayTimestamp"
        :visibility="visibility"
        :mode="selectedInterval"
        :intraday="intraday"
      />
    </CardBody>
  </CardContainer>
</template>

<script>
import PerformanceChart from "../charts/PoolPerformance.vue";
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import Dropdown from "@/components/ui/Dropdown.vue";

export default {
  props: {
    performanceData: {
      type: Array,
      required: true,
    },
    todayTimestamp: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      intraday: false,
      selectedInterval: "week",
      datasets: [
        {
          label: "Total liquidity",
          name: "liquidity",
        },
        {
          label: "Utilization",
          name: "utilization",
        },
        {
          label: "Profit & Loss",
          name: "pnl",
        },
      ],
      intervals: [
        {
          label: "Last Week",
          name: "week",
        },
        {
          label: "Last Month",
          name: "month",
        },
        {
          label: "Last Year",
          name: "year",
        },
        {
          label: "All",
          name: "all",
        },
      ],
      visibility: {
        liquidity: true,
        utilization: true,
        pnl: true,
      },
    };
  },
  methods: {
    selectInterval(name) {
      this.selectedInterval = name;
    },
    selectDataset(name) {
      this.visibility[name] = !this.visibility[name];
    },
  },
  components: {
    PerformanceChart,
    CardContainer,
    CardBody,
    Dropdown,
  },
};
</script>
