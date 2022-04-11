<template>
  <div
    class="leading-none rounded-md"
    :class="[sizeClass, colorClasses]"
    @click="$emit('click')"
  >
    {{ label }}
  </div>
</template>

<script>
const sizeToClasses = {
  md: "text-base px-2 pt-2.5 pb-1.5",
  xs: "text-xs px-1 pt-1.5 pb-1",
  sm: "text-sm p-2",
};
const colorToClasses = {
  glass: "bg-white bg-opacity-10 text-white",
  white: "bg-white text-deep-black-600",
};

export default {
  props: {
    label: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: "sm",
      validator: (value) => value in sizeToClasses,
    },
    color: {
      type: String,
      default: "glass",
      validator: (value) => value in colorToClasses,
    },
  },
  computed: {
    sizeClass() {
      return sizeToClasses[this.size];
    },
    colorClasses() {
      return colorToClasses[this.color];
    },
  },
};
</script>
