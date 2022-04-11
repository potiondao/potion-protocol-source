<template>
  <div class="font-extrabold" :class="textSize">{{ label }}</div>
</template>

<script>
const sizeToClass = {
  xxs: "text-xs",
  xs: "text-sm",
  sm: "text-base",
  md: "text-lg",
  default: "text-xl",
  lg: "text-2xl",
};
export default {
  props: {
    label: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: "default",
      validator: (value) => value in sizeToClass,
    },
  },
  computed: {
    textSize() {
      return sizeToClass[this.size];
    },
  },
};
</script>
