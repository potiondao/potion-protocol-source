<template>
  <CardContainer :fullHeight="false">
    <div class="flex flex-wrap">
      <Chart
        :bonding-curve="bondingCurve"
        :emerging-curves="emergingCurves"
        :unload-keys="unloadKeys"
        class="w-full lg:w-3/4 px-6 py-4"
      />
      <div
        class="
          w-full
          lg:w-1/4
          px-6
          py-4
          text-white
          bg-radial-glass
          rounded-r-3xl
        "
        style=""
      >
        <CurveFormula></CurveFormula>
        <div class="px-3 my-5 font-semibold text-sm">
          Set the following parameters and define your curve.
          <Tooltip
            class="ml-half-char mb-half-char inline-block"
            icon-weight="bold"
            message="a = Scale
            b = End Point
            c = Convexity
            d = Offset"
          />
        </div>
        <CardContainer :fullHeight="false">
          <div
            class="p-3 flex items-center space-x-2"
            v-for="({ description, key }, index) in sortedParameters"
            :key="index"
            :class="{ 'border-t border-white border-opacity-10': index > 0 }"
          >
            <div
              class="
                flex
                items-center
                px-2
                py-1
                rounded-md
                bg-white bg-opacity-10
              "
            >
              <span class="text-xs text-white leading-none">{{
                description
              }}</span>
            </div>
            <input
              type="number"
              :min="min"
              :max="max"
              :step="step"
              class="
                w-full
                leading-none
                bg-transparent
                text-lg
                font-semibold
                block
                border-none
                arrowless
                text-right
                p-0
                outline-none
                focus:outline-none focus:border-none focus:ring-0
              "
              v-model="parameters[key]"
              @input="checkBounds(key)"
            />
            <MinusPlusButton @click="decrease(key)" direction="decrease" />
            <MinusPlusButton @click="increase(key)" direction="increase" />
          </div>
        </CardContainer>
      </div>
    </div>
  </CardContainer>
</template>

<script>
import { debounce as _debounce } from "lodash-es";
import CardContainer from "../ui/CardContainer.vue";
import CurveFormula from "@/components/ui/CurveFormula.vue";
import Tooltip from "@/components/ui/Tooltip.vue";
import Chart from "@/components/charts/BondingCurve.vue";
import MinusPlusButton from "@/components/ui/MinusPlusButton.vue";
import { curveParamsToHyperbolic } from "@/helpers/pools";
import { pick as _pick } from "lodash-es";
import { cloneDeep as _cloneDeep } from "lodash-es";

const min = 0;
const max = 100;
const step = 0.1;

const addToValue = (a, b) => (parseFloat(a) + b).toFixed(1);
const checkBounds = (a, min, max) => {
  const n = parseFloat(a);
  const value = n > max ? max : n < min ? min : n;
  return value.toString();
};
const increase = (a) => checkBounds(addToValue(a, step), min, max);
const decrease = (a) => checkBounds(addToValue(a, -step), min, max);

export default {
  components: {
    Chart,
    CardContainer,
    Tooltip,
    MinusPlusButton,
    CurveFormula,
  },
  props: {
    curve: {
      type: Object,
      required: true,
    },
    unloadKeys: {
      type: Array,
      default: () => [],
    },
    emergingCurves: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      min,
      max,
      step,
      bondingCurveFactor: "0.5",
      parameters: {},
    };
  },

  mounted() {
    this.$set(
      this,
      "parameters",
      _cloneDeep(_pick(this.curve, ["a", "b", "c", "d", "maxUtil"]))
    );
    this.$nextTick(() => {
      this.updateCurveSettings();
    });
  },
  computed: {
    bondingCurve() {
      return curveParamsToHyperbolic(this.parameters);
    },
    sortedParameters() {
      return Object.entries(this.parameters)
        .sort(([a], [b]) => a - b)
        .map(([key, value]) => {
          return {
            value,
            key,
            description: key,
          };
        });
    },
  },
  methods: {
    updateCurveSettings() {
      this.$emit("curve-settings-updated", {
        parameters: this.parameters,
        curve: this.bondingCurve,
      });
    },
    increase(key) {
      this.parameters[key] = increase(this.parameters[key]);
      this.updateCurveSettings();
    },
    decrease(key) {
      this.parameters[key] = decrease(this.parameters[key]);
      this.updateCurveSettings();
    },
    checkBounds: _debounce(function (key) {
      this.parameters[key] = checkBounds(this.parameters[key], min, max);
      this.updateCurveSettings();
    }, 2000),
  },
};
</script>

<style scoped>
.arrowless,
.arrowless::-webkit-outer-spin-button,
.arrowless::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
  -moz-appearance: textfield;
}

.bg-radial-glass {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(67, 60, 104, 0.3) 0%,
    rgba(67, 60, 104, 0.05) 100%
  );
}
</style>
