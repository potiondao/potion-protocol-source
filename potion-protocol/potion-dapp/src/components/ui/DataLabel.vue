<template>
  <div class="capitalize font-medium" :class="[sizeClass, alignmentClass]">
    {{ label }}
  </div>
</template>

<script>
const sizeToClass = {
  sm: "text-xs",
  md: "text-sm",
  lg: "text-base",
};

const alignmentToClass = {
  center: "text-center",
  left: "text-left",
  right: "text-right",
};

export default {
  props: {
    label: {
      type: String,
      required: true,
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
  },
  computed: {
    sizeClass() {
      return sizeToClass[this.size];
    },
    alignmentClass() {
      return alignmentToClass[this.alignment];
    },
  },
};
</script>
