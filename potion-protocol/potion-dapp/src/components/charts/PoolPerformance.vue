<template>
  <div class="mt-4"></div>
</template>

<script>
import { _lastUniqBy } from "@/helpers";
import { createResponsiveChart } from "@/helpers/charts.ts";
import {
  rangeRight as _rangeRight,
  findLast as _findLast,
  sortBy as _sortBy,
} from "lodash-es";

import dayjs from "dayjs";

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
    mode: {
      type: String,
      default: "week",
      validator: (value) => ["week", "month", "year", "all"].includes(value),
    },
    intraday: {
      type: Boolean,
      default: false,
    },
    visibility: {
      type: Object,
      default: () => {
        return {
          liquidity: true,
          utilization: true,
          pnl: true,
        };
      },
    },
  },
  data() {
    return {
      chart: null,
      liquidity: null,
      utilization: null,
      pnl: null,
    };
  },
  watch: {
    performanceData() {
      this.reloadDatasets();
    },
    mode() {
      this.reloadDatasets();
    },
    intraday() {
      this.reloadDatasets();
      this.chart.applyOptions({
        timeScale: {
          timeVisible: this.mode === "week" || this.intraday,
        },
      });
    },
    visibility: {
      deep: true,
      handler() {
        this.setVisibility();
      },
    },
  },
  methods: {
    createChart() {
      this.chart = createResponsiveChart(this.$el, {
        height: 500,
        timeScale: {
          timeVisible: this.mode === "week" || this.intraday,
        },
        leftPriceScale: {
          visible: true,
        },
        layout: {
          textColor: "#fff",
          backgroundColor: "transparent",
        },
        crosshair: {
          vertLine: {
            color: "rgba(114, 76, 249, .3)",
          },
          horzLine: {
            color: "rgba(114, 76, 249, .3)",
          },
        },
        grid: {
          vertLines: {
            color: "transparent",
          },
          horzLines: {
            color: "rgba(255, 255, 255, .1)",
          },
        },
      });
      this.utilization = this.chart.addLineSeries({
        priceFormat: {
          type: "custom",
          minmove: 0.01,
          formatter: (p) => `${p.toFixed(2)}%`,
        },
        title: "utilization",
        color: "rgba(250, 25, 139, .7)",
      });
      this.liquidity = this.chart.addAreaSeries({
        priceScaleId: "left",
        priceFormat: {
          type: "volume",
        },
        title: "liquidity",
        lineColor: "rgb(114, 76, 249)",
        topColor: "transparent",
        bottomColor: "rgba(114, 76, 249, .7)",
      });
      this.pnl = this.chart.addHistogramSeries({
        priceFormat: {
          type: "custom",
          minmove: 0.01,
          formatter: (p) => `${p.toFixed(2)}%`,
        },
        title: "pnl",
        color: "rgba(61, 220, 151, .6)",
      });
    },
    setDatasets(liquidity, utilization, pnl) {
      this.liquidity.setData(liquidity);
      this.utilization.setData(utilization);
      this.pnl.setData(pnl);
    },
    setVisibility() {
      this.liquidity.applyOptions({
        visible: this.visibility.liquidity,
      });
      this.utilization.applyOptions({
        visible: this.visibility.utilization,
      });
      this.pnl.applyOptions({
        visible: this.visibility.pnl,
      });
      this.chart.applyOptions({
        leftPriceScale: {
          visible: this.visibility.liquidity,
        },
        rightPriceScale: {
          visible: this.visibility.utilization || this.visibility.pnl,
        },
      });
    },
    reloadDatasets() {
      this.setDatasets([], [], []);
      this.setDatasets(
        this.liquidityDataset,
        this.utilizationDataset,
        this.pnlDataset
      );
      this.setTimescale();
    },
    setTimescale() {
      this.chart.timeScale().setVisibleRange({
        from: this.fromTimestamp,
        to: this.timestamps.endOfDay,
      });
    },
    getChartTime(timestamp) {
      if (this.intraday) {
        return dayjs.unix(timestamp).startOf("second").unix();
      }
      return dayjs.unix(timestamp).endOf(this.tickData[this.mode].unit).unix();
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.createChart();
      this.setVisibility();
      this.setDatasets(
        this.liquidityDataset,
        this.utilizationDataset,
        this.pnlDataset
      );
      this.setTimescale();
    });
  },
  computed: {
    dayjsNow() {
      return dayjs.unix(this.todayTimestamp);
    },
    today() {
      return this.dayjsNow.startOf("day");
    },
    timestamps() {
      return {
        now: this.dayjsNow.unix(),
        today: this.today.unix(),
        endOfDay: this.today.endOf("day").unix(),
        previousWeek: this.today.subtract(1, "week").unix(),
        previousMonth: this.today.subtract(1, "month").unix(),
        previousYear: this.today.subtract(1, "year").unix(),
        firstItem: Math.min(
          ...this.performanceData.map((item) => item.timestamp)
        ),
      };
    },
    datasetTotalYears() {
      const difference = dayjs
        .unix(this.timestamps.endOfDay)
        .diff(dayjs.unix(this.timestamps.firstItem), "year", true);
      return Math.ceil(difference);
    },
    fromTimestamp() {
      if (this.mode === "month") {
        return this.timestamps.previousMonth;
      }
      if (this.mode === "year") {
        return this.timestamps.previousYear;
      }
      if (this.mode === "all") {
        return this.timestamps.firstItem;
      }
      return this.timestamps.previousWeek;
    },
    tickData() {
      return {
        week: {
          steps: 7 * 24,
          unit: "hour",
        },
        month: {
          steps: 30,
          unit: "day",
        },
        year: {
          steps: 365,
          unit: "day",
        },
        all: {
          steps: 365 * this.datasetTotalYears,
          unit: "day",
        },
      };
    },
    tickFills() {
      const { steps, unit } = this.tickData[this.mode];
      const timestamps = _rangeRight(steps).map((v) =>
        this.today.subtract(v, unit).unix()
      );
      let lastValidPoint = {
        liquidity: 0,
        utilization: 0,
        pnl: 0,
      };
      return timestamps.map((timestamp) => {
        const nearestValue = _findLast(
          this.performanceData,
          (item) => item.timestamp <= timestamp
        );
        if (nearestValue) {
          lastValidPoint = nearestValue;
          return {
            timestamp,
            liquidity: nearestValue.liquidity,
            utilization: nearestValue.utilization,
            pnl: nearestValue.pnl,
          };
        }
        return {
          timestamp,
          liquidity: lastValidPoint.liquidity,
          utilization: lastValidPoint.utilization,
          pnl: lastValidPoint.pnl,
        };
      });
    },
    chartDataset() {
      const dataset = _sortBy(this.performanceData.concat(this.tickFills), [
        "timestamp",
        "actionType",
      ])
        .map(({ timestamp, liquidity, utilization, pnl }) => {
          return {
            time: this.getChartTime(timestamp),
            liquidity,
            pnl,
            utilization,
          };
        })
        .filter(
          (point) =>
            point.time >= this.fromTimestamp &&
            point.time < this.timestamps.endOfDay
        );
      return _lastUniqBy(dataset, "time");
    },
    liquidityDataset() {
      const dataset = this.chartDataset.map(({ time, liquidity }) => {
        return {
          time,
          value: liquidity,
        };
      });
      return dataset;
    },
    utilizationDataset() {
      return this.chartDataset.map(({ time, utilization }) => {
        return {
          time,
          value: utilization,
        };
      });
    },
    pnlDataset() {
      return this.chartDataset.map(({ time, pnl }) => {
        return {
          time,
          value: pnl,
        };
      });
    },
  },
};
</script>
