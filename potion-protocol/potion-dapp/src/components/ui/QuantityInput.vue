<template>
  <div>
    <div
      class="
        px-3
        pt-3
        border-t border-l border-r
        rounded-t-3xl
        transition-colors
      "
      :class="{
        'border-white border-opacity-10': !inputFocus,
        'border-primary-500 border-opacity-100': inputFocus,
        'border-secondary-500 border-opacity-100': error,
        'border-tertiary-500 border-opacity-100': transactionsNumber > 1,
      }"
      @click="setInputFocus()"
    >
      <span class="mb-3 text-base">{{ title }}</span>
      <div class="flex py-1 items-center">
        <input
          type="number"
          ref="input"
          @focus="inputFocus = true"
          @blur="inputFocus = false"
          :value="value"
          :min="min"
          :max="max"
          @input="bubbleInput($event.target.value)"
          class="
            block
            w-full
            pl-0
            text-2xl
            bg-transparent
            border-none
            rounded-lg
            outline-none
            textfield
            focus:outline-none focus:border-none focus:ring-0
          "
        />
        <div class="flex items-center">
          <MinusPlusButton
            @click="decrease"
            direction="decrease"
            class="mx-2"
          />
          <MinusPlusButton @click="increase" direction="increase" />
        </div>
      </div>
    </div>
    <div
      class="
        w-full
        px-3
        pb-3
        pt-2
        rounded-b-3xl
        transition-colors
        border-white border-opacity-10 border-b border-l border-r
      "
      :class="{
        'bg-radial-glass': !inputFocus && !error && transactionsNumber === 1,
        'bg-gradient-to-r from-primary-500 to-primary-400': inputFocus,
        'bg-gradient-to-r from-secondary-500 to-secondary-400':
          error || (!inputFocus && error),
        'bg-gradient-to-r from-tertiary-600 to-tertiary-500':
          transactionsNumber > 1 || (!inputFocus && transactionsNumber > 1),
      }"
    >
      <span class="text-sm font-medium text-dirty-white-300">
        <span v-if="transactionsNumber === 1"
          >{{ footerDescription }} {{ maxFormatted }}</span
        >
        <span v-else
          >Num. of transactions required: {{ transactionsNumber }}
        </span>
      </span>
    </div>
  </div>
</template>

<script>
import MinusPlusButton from "@/components/ui/MinusPlusButton.vue";
import { formatNumber } from "@/helpers";

export default {
  components: {
    MinusPlusButton,
  },
  props: {
    title: {
      type: String,
      default: "",
    },
    value: {
      type: String,
      default: "",
    },
    min: {
      type: String,
      default: "0",
    },
    max: {
      type: String,
      default: "0",
    },
    footerDescription: {
      type: String,
      default: "",
    },
    error: {
      type: Boolean,
      default: false,
    },
    transactionsNumber: {
      type: Number,
      default: 1,
    },
    focusEnabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      inputFocus: false,
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.setInputFocus();
    });
  },
  computed: {
    maxFormatted() {
      return formatNumber(this.max);
    },
  },
  watch: {
    focusEnabled: function () {
      if (this.focusEnabled) {
        this.$refs.input.focus();
      } else {
        this.$refs.input.blur();
      }
    },
  },
  methods: {
    setInputFocus() {
      this.$refs.input.focus();
    },
    bubbleInput(value) {
      this.$emit("input", value);
    },
    increase() {
      this.$emit("increase");
    },
    decrease() {
      this.$emit("decrease");
    },
  },
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
