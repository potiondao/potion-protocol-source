<template>
  <div class="relative w-full h-[4px]">
    <input
      class="input-slider cursor-pointer"
      type="range"
      :step="step"
      @input="$emit('input', $event.target.value)"
      :value="value"
      :min="min"
      :max="max"
    />
    <!-- :style="`left: calc(${thumbPosition}% - 16px)` -->
    <span
      class="select-none slider-thumb shadow-md"
      :style="`left: calc(${thumbPosition}% - 16px)`"
      >{{ value }}{{ symbol }}</span
    >
    <div class="slider-rail">
      <div
        class="range-rail shadow-md"
        :style="`width: ${thumbPosition}%`"
      ></div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    symbol: {
      type: String,
    },
    value: {
      type: String,
      required: true,
    },
    min: {
      type: String,
      required: true,
    },
    max: {
      type: String,
      required: true,
    },
    step: {
      type: String,
      required: true,
    },
  },
  computed: {
    thumbPosition() {
      return ((this.value - this.min) / (this.max - this.min)) * 100;
    },
  },
};
</script>
<style scoped>
.input-slider {
  height: 4px;

  @apply focus:outline-none appearance-none w-full bg-transparent z-30 absolute;
}

.input-slider::-webkit-slider-thumb {
  width: 48px;
  height: 32px;
  border: none;
  padding: 0 8px;

  @apply bg-transparent appearance-none;
  /* @apply bg-transparent appearance-none; */
  /* @apply bg-secondary-500 bg-opacity-20 appearance-none; */
}

.input-slider::-moz-range-thumb {
  width: 48px;
  height: 32px;
  border: none;
  padding: 0 8px;

  @apply bg-transparent appearance-none;
  /* @apply bg-transparent appearance-none; */
  /* @apply bg-secondary-500 bg-opacity-20 appearance-none; */
}

.slider-thumb {
  min-width: 48px;
  height: 32px;
  line-height: 32px;
  top: -16px;
  font-size: 12px;
  padding: 0 8px;

  @apply absolute z-20 text-center rounded-lg cursor-pointer bg-gradient-to-r from-primary-500 to-primary-400;
}

.slider-rail {
  height: 4px;

  @apply absolute w-full bg-white bg-opacity-10;
}
.range-rail {
  height: 4px;
  @apply absolute bg-primary-500;
}
</style>
