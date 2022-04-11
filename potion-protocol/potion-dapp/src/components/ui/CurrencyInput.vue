<template>
  <div
    class="rounded-2xl"
    :class="[containerBorderSize, containerStateClasses]"
  >
    <div class="w-full p-3 transition-colors" @click="setInputFocus">
      <div class="w-full font-medium text-sm mb-4">{{ title }}</div>
      <div class="flex items-center justify-between">
        <span
          class="
            flex
            items-center
            p-1.5
            rounded
            bg-white bg-opacity-10
            text-xs text-white
            font-semibold
            leading-none
          "
          >{{ currency }}</span
        >
        <div class="w-full px-3">
          <input
            class="
              block
              w-full
              p-0
              text-xl
              bg-transparent
              border-none
              rounded-lg
              outline-none
              textfield
              focus:outline-none focus:border-none focus:ring-0
              font-bitter font-bold
            "
            ref="inputBalance"
            type="number"
            @focus="inputFocus = true"
            @blur="inputFocus = false"
            min="1"
            :value="value"
            @click.stop
            @input="updateValueDebounced($event.target.value)"
          />
        </div>

        <button
          class="
            flex
            items-center
            p-1.5
            rounded
            outline-none
            focus:outline-none
            transition-colors
            bg-transparent
            border border-white border-opacity-10
            hover:bg-white hover:bg-opacity-10
            text-white text-opacity-100 text-xs
            font-semibold
            leading-none
          "
          @click="setToMax"
        >
          MAX
        </button>
      </div>
    </div>
    <div
      class="w-full p-3 rounded-b-2xl text-sm font-semibold transition-colors"
      :class="footerStateClasses"
    >
      <span v-if="error">Error</span>
      <template v-else>
        <span>{{ description }} </span>
        <span class="font-bold font-bitter">{{ balanceFormatted }}</span>
      </template>
    </div>
  </div>
</template>

<script>
import { debounce as _debounce } from "lodash-es";
import { formatNumber } from "@/helpers";

export default {
  props: {
    value: {
      type: String,
      default: "0",
    },
    title: {
      type: String,
      default: "",
    },
    description: {
      type: String,
      default: "",
    },
    currency: {
      type: String,
      default: "",
    },
    maxAvailableBalance: {
      type: String,
      default: "0",
    },
    disableExternalBorder: {
      type: Boolean,
      default: false,
    },
    onlyTopBorder: {
      type: Boolean,
      default: false,
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
  methods: {
    updateValue(value) {
      this.$emit("input", value);
    },
    updateValueDebounced: _debounce(function (value) {
      if (parseFloat(value) > 0) {
        this.updateValue(value);
      } else {
        this.updateValue("0");
      }
    }, 2000),
    setToMax() {
      this.updateValue(this.maxAvailableBalance);
    },
    setInputFocus() {
      this.$refs.inputBalance.focus();
    },
  },
  computed: {
    balanceFormatted() {
      const maxAvailableBalanceFormatted = formatNumber(
        this.maxAvailableBalance
      );
      return `${maxAvailableBalanceFormatted} ${this.currency}`;
    },
    // containerYBorders() {
    //   return this.onlyYborders
    //     ? "border border-t border-b border-l-transparent border-r-transparent"
    //     : "";
    // },

    containerBorderSize() {
      if (this.disableExternalBorder && this.onlyTopBorder) {
        return "border-opacity-10 border-t border-b";
      }
      if (this.disableExternalBorder) {
        return "border-transparent border-0";
      }
      return "border-opacity-10 border";
      // return this.disableExternalBorder
      //   ? "border-transparent border-0"
      //   : "border-opacity-10 border";
    },
    containerStateClasses() {
      if (this.error) {
        return "border-secondary-500 border-opacity-100";
      }
      if (this.inputFocus) {
        return "border-primary-500 border-opacity-100";
      }
      return "border-white";
    },
    footerStateClasses() {
      if (this.error) {
        return "bg-gradient-to-r from-secondary-500 to-secondary-400";
      }
      if (this.inputFocus) {
        return "bg-gradient-to-r from-primary-500 to-primary-400";
      }
      return "bg-radial-glass";
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

.bg-radial-glass {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(67, 60, 104, 0.3) 0%,
    rgba(67, 60, 104, 0.05) 100%
  );
  backdrop-filter: blur(20px);
}
</style>
