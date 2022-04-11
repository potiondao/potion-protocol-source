<template>
  <CardContainer color="no-bg" class="p-6">
    <div class="flex justify-between items-center mb-6">
      <span class="inline-flex items-center">
        <TokenIcon
          size="lg"
          :name="underlying.name"
          :image="underlying.image"
          :address="underlying.address"
          class="mr-2"
        />
        <Title :label="underlying.symbol" />
      </span>
      <Btn color="transparent" label="" size="icon" @click="close">
        <template v-slot:pre-icon>
          <XIcon class="h-4" />
        </template>
      </Btn>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <CardContainer color="clean" class="flex flex-col p-6">
        <h2 class="mb-4 inline-flex items-center">
          Max Strike
          <Tooltip
            class="ml-half-char"
            message="The highest price that a buyer can exercise the Option"
          />
        </h2>
        <div class="mb-8 flex flex-col">
          <span class="mb-2">Choose the maximum insurance cover.</span>
          <span class="text-secondary-500 text-sm inline-flex items-center"
            ><AttentionIcon class="mr-2" /> Current Price {{ formattedPrice }}
          </span>
        </div>
        <div class="mt-auto mb-4 py-5">
          <InputSlider
            v-model="strike"
            min="0"
            max="200"
            step="1"
            symbol="%"
            @input="underlyingChanged"
          />
        </div>
      </CardContainer>
      <CardContainer class="flex flex-col p-6" color="clean">
        <h2 class="mb-4 inline-flex items-center">
          Max Duration
          <Tooltip
            class="ml-half-char"
            message="The max duration that you are willing sell an Option"
          />
        </h2>
        <div class="mb-8">
          How long the insurance you are selling will be valid for.
        </div>
        <div class="mt-auto mb-4 py-5">
          <InputSlider
            v-model="duration"
            min="1"
            max="365"
            step="1"
            symbol="dd"
            @input="underlyingChanged"
          />
        </div>
      </CardContainer>
    </div>
  </CardContainer>
</template>

<script>
import Btn from "@/components/ui/Button.vue";
import TokenIcon from "@/components/icons/TokenIcon.vue";
import Tooltip from "@/components/ui/Tooltip.vue";
import AttentionIcon from "@/components/icons/AttentionIcon.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import Title from "@/components/ui/Title.vue";
import XIcon from "@/components/icons/XIcon.vue";
import InputSlider from "@/components/ui/InputSlider.vue";
import { debounce as _debounce } from "lodash-es";

export default {
  components: {
    Btn,
    CardContainer,
    TokenIcon,
    Tooltip,
    AttentionIcon,
    Title,
    XIcon,
    InputSlider,
  },
  props: {
    underlying: {
      type: Object,
      required: true,
    },
    currentPrice: {
      type: String,
      default: "0",
    },
  },
  data() {
    return {
      strike: this.underlying.strike,
      duration: this.underlying.duration,
    };
  },
  computed: {
    formattedPrice() {
      return new Intl.NumberFormat(navigator.language, {
        style: "currency",
        currency: "USD",
      }).format(this.currentPrice);
    },
  },
  methods: {
    close() {
      this.$emit("close-underlying-selected", this.underlying.address);
    },
    underlyingChanged: _debounce(function () {
      this.$emit("underlying-updated", {
        address: this.underlying.address,
        duration: this.duration,
        strike: this.strike,
      });
    }, 500),
  },
};
</script>
