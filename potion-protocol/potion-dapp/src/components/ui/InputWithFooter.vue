<template>
  <div>
    <div
      class="
        w-full
        p-3
        mt-10
        rounded-t-3xl
        border-t border-r border-l
        transition-colors
      "
      @click="setInputFocus()"
      :class="{
        'border-white border-opacity-10': !inputFocus,
        'border-primary-500 border-opacity-100': inputFocus,
        'border-secondary-500 border-opacity-100': error,
      }"
    >
      <div class="w-full mb-3 text-sm font-medium">{{ title }}</div>
      <div class="flex items-center justify-between">
        <div class="flex items-center p-2 rounded-md bg-white bg-opacity-10">
          <span
            class="text-xs text-white text-opacity-50 leading-none font-medium"
            >{{ tagLabel }}</span
          >
        </div>
        <div class="w-full px-3">
          <input
            class="
              block
              w-full
              p-1
              text-xl
              bg-transparent
              border-none
              rounded-3xl
              outline-none
              textfield
              focus:outline-none focus:border-none focus:ring-0
              leading-none
            "
            ref="inputTag"
            type="number"
            @focus="inputFocus = true"
            @blur="inputFocus = false"
            min="1"
            :step="step"
            :value="value"
            @click.stop
            @input="updateValueDebounced($event.target.value)"
          />
        </div>
      </div>
    </div>
    <div
      class="w-full px-3 pb-3 pt-2 rounded-b-3xl transition-colors"
      :class="{
        'radial-bg-glass': !inputFocus && !error,
        'bg-gradient-to-r from-primary-500 to-primary-400': inputFocus,
        'bg-gradient-to-r from-secondary-500 to-secondary-400':
          error || (!inputFocus && error),
      }"
    >
      <span class="text-sm font-medium"
        >{{ footerDescription }}
        <span class="text-white">{{ footerValue }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import { debounce as _debounce } from "lodash-es";

export default {
  props: {
    focus: {
      type: Boolean,
      default: false,
    },
    value: {
      type: String,
      default: "0",
    },
    title: {
      type: String,
      default: "",
    },
    tagLabel: {
      type: String,
      default: "",
    },
    footerDescription: {
      type: String,
      default: "",
    },
    footerValue: {
      type: String,
      default: "",
    },
    step: {
      type: String,
      default: "1",
    },
    error: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      inputFocus: false,
    };
  },
  watch: {
    focus() {
      this.inputFocus = this.focus;
      this.$refs.inputTag.focus();
    },
  },
  methods: {
    updateValue(value) {
      this.$emit("input", value);
    },
    updateValueDebounced: _debounce(function (value) {
      this.updateValue(value);
    }, 200),
    setInputFocus() {
      this.$refs.inputTag.focus();
    },
  },
  computed: {},
};
</script>

<style scoped>
.textfield {
  appearance: textfield;
  -webkit-appearance: textfield;
  margin: 0;
}
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.radial-bg-glass {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(67, 60, 104, 0.3) 0%,
    rgba(67, 60, 104, 0.05) 100%
  );
}
</style>
