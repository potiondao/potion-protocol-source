<template>
  <div class="flex flex-wrap items-center space-x-1" :class="alignmentClass">
    <GainIcon v-if="grow" :grow="grow"></GainIcon>
    <div class="font-bold font-bitter" :class="[sizeClass, valueColor]">
      <span :class="color">{{ formattedValue }}</span>
      <span v-if="symbol"> {{ symbol }}</span>
    </div>
  </div>
</template>

<script>
import dayjs from "dayjs";
import GainIcon from "../icons/GainIcon.vue";
import { formatNumber } from "@/helpers";

const sizeToClass = {
  sm: "text-sm",
  md: "text-base",
  lg: "text-lg",
};

const alignmentToClass = {
  center: "justify-center",
  left: "justify-start",
  right: "justify-end",
};

const formatter = {
  raw: (value) => value,
  number: (value) => {
    return formatNumber(parseFloat(value));
  },
  timestamp: (value) => {
    return dayjs.unix(value).format("ll");
  },
  date: (value) => {
    return dayjs(value).format("ll");
  },
};

export default {
  components: {
    GainIcon,
  },
  props: {
    valueColor: {
      type: String,
      default: "",
    },
    size: {
      type: String,
      default: "lg",
      validator: (value) => value in sizeToClass,
    },
    alignment: {
      type: String,
      default: "left",
      validator: (value) => value in alignmentToClass,
    },
    color: {
      type: String,
      default: "dirty-white-300",
    },
    value: {
      type: String,
      required: true,
    },
    valueType: {
      type: String,
      default: "number",
      validator(value) {
        return Object.keys(formatter).includes(value);
      },
    },
    symbol: {
      type: String,
    },
    grow: {
      type: String,
      required: false,
      validator: function (value) {
        return ["up", "down"].indexOf(value) !== -1;
      },
    },
  },
  computed: {
    formattedValue() {
      return formatter[this.valueType](this.value);
    },
    sizeClass() {
      return sizeToClass[this.size];
    },
    alignmentClass() {
      return alignmentToClass[this.alignment];
    },
  },
};
</script>
