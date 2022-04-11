<template>
  <div class="flex flex-col text-white">
    <div class="w-full text-sm">Premium Bonding Curve</div>
    <div ref="chartContainer" style="height: 500px">
      <div id="customBondingChart" ref="customBondingChart"></div>
    </div>
  </div>
</template>

<script>
import { range as _range } from "lodash-es";
import bb, { spline } from "billboard.js";

const formatYAxisValue = (n) => parseFloat((100 * n).toFixed(2));

export default {
  props: {
    bondingCurve: {
      type: Array,
      default: () => [],
    },
    unloadKeys: {
      type: Array,
      default: () => [],
    },
    emergingCurves: {
      type: Array,
      default: () => [],
    },
    axis: {
      type: Object,
      default: () => {
        return {
          x: {
            label: {
              text: "Utilization",
            },
            tick: {
              values: _range(0, 101, 10),
              format: (x) => `${x}%`,
            },
          },
          y: {
            label: {
              text: "Premium",
            },
            tick: {
              format: (y) => `${y}%`,
            },
          },
        };
      },
    },
  },
  data() {
    return {
      chart: null,
      chartHeight: null,
      chartReady: false,
      point: {
        show: false,
      },
    };
  },
  computed: {
    chartData() {
      const json = {
        bondingCurve: this.bondingCurve.map(formatYAxisValue),
      };
      const colors = {
        bondingCurve: "var(--primary-500)",
      };
      const names = {
        bondingCurve: "Bonding Curve",
      };
      const unload = this.unloadKeys.map((v) => v.toUpperCase());
      if (this.emergingCurves && this.emergingCurves.length > 0) {
        this.emergingCurves.forEach((curve) => {
          if (curve.data && curve.data.length > 0) {
            json[curve.underlyingSymbol] = curve.data.map(formatYAxisValue);
            names[curve.underlyingSymbol] =
              curve.underlyingSymbol.toUpperCase();
          } else {
            unload.push(curve.underlyingSymbol);
          }
        });
      }

      return {
        type: spline(),
        json: json,
        colors: colors,
        names: names,
        unload: unload,
      };
    },
  },
  watch: {
    chartData() {
      this.updateChart();
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.chartHeight = this.$refs.chartContainer.clientHeight;
      this.createChart();
    });
  },
  methods: {
    createChart() {
      this.chart = bb.generate({
        bindto: this.$refs.customBondingChart,
        data: this.chartData,
        point: this.point,
        grid: this.grid,
        axis: this.axis,
        size: { height: this.chartHeight },
        padding: {
          right: 50,
        },
        spline: {
          interpolation: {
            type: "monotone-x",
          },
        },
      });
      this.chartReady = true;
    },
    updateChart() {
      if (this.chartReady) {
        this.chart.load(this.chartData);
      }
    },
  },
};
</script>

<style>
#customBondingChart .bb-line {
  stroke-dasharray: 7 8 !important;
}
#customBondingChart .bb-line-bondingCurve {
  stroke-dasharray: none !important;
}

.bb-tooltip {
  border-collapse: separate;
  border-spacing: 0;
  empty-cells: show;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background-color: rgba(36, 32, 56, 0.7);
  text-align: left;
  font-size: 11px;
}

.bb-tooltip th {
  font-size: 12px;
  padding: 4px 8px;
  text-align: left;
  border-bottom: solid 1px rgba(255, 255, 255, 0.1);
}
.bb-tooltip td {
  padding: 4px 6px;
  background-color: rgba(36, 32, 56, 0.7);
}

.bb-axis-y text {
  @apply text-white fill-current;
}
</style>
