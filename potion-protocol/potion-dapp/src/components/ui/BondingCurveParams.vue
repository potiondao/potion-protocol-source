<template>
  <div class="text-white bg-radial-glass rounded-r-3xl">
    <div class="font-medium text-sm">Parameters defining your curve.</div>
    <CurveFormula class="my-6"></CurveFormula>
    <CardContainer :fullHeight="false">
      <div
        class="p-3 flex items-center space-x-2"
        :class="{ 'border-t border-white border-opacity-10': index > 0 }"
        v-for="({ description, value }, index) in sortedParameters"
        :key="index"
      >
        <div
          class="flex items-center px-2 py-1 rounded-md bg-white bg-opacity-10"
        >
          <span class="text-xs text-white leading-none">{{ description }}</span>
        </div>
        <span
          class="
            w-full
            leading-none
            bg-transparent
            text-lg
            font-semibold
            block
            border-none
            text-right
            p-0
            font-bitter
          "
        >
          {{ value }}
        </span>
      </div>
    </CardContainer>
  </div>
</template>

<script>
import { pick as _pick } from "lodash-es";
import CardContainer from "@/components/ui/CardContainer.vue";
import CurveFormula from "@/components/ui/CurveFormula.vue";

export default {
  components: {
    CardContainer,
    CurveFormula,
  },
  props: {
    parameters: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
  computed: {
    curveParameters() {
      return _pick(this.parameters, ["a", "b", "c", "d", "maxUtil"]);
    },
    sortedParameters() {
      return Object.entries(this.curveParameters)
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
};
</script>
