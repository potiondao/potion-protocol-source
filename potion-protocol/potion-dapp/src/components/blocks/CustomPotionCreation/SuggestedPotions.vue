<template>
  <CardContainer color="glass" class="mt-5">
    <div
      class="
        flex
        items-center
        justify-between
        w-full
        px-6
        py-4
        text-sm
        cursor-pointer
      "
      @click="showGasSaving = !showGasSaving"
    >
      <div class="flex flex-col">
        <GradientTitle label="Similar Potions" size="xs" class="uppercase" />
        <div class="flex items-center">
          <span v-if="gas"
            >You are saving
            {{ formattedPrice }}
            in gas by buying an existing Potion.</span
          >
          <Tooltip
            class="ml-half-char"
            message="Gas is saved when buying Potions that already exist on-chain"
          />
        </div>
      </div>

      <Btn color="transparent" label="" size="icon">
        <template v-slot:pre-icon>
          <CloseIcon class="w-4" weight="bold" v-if="showGasSaving" />
          <OpenIcon class="w-4" weight="bold" v-else />
        </template>
      </Btn>
    </div>
    <CardBody
      class="accordion-transition"
      :class="{
        'max-h-0 overflow-hidden px-6': !showGasSaving,
        'max-h-[600px] overflow-y-auto px-6': showGasSaving,
      }"
    >
      <PotionsGrid
        color="clean"
        size="compact"
        v-if="potions.length > 0"
        :potions="potions"
        :show-heading="false"
        :stable-coin-collateral="stableCoinCollateral"
        @potion-selected="potionSelected"
      />
      <div v-else class="h-[300px] flex items-center justify-center">
        <Title
          size="lg"
          label="No Results found yet."
          class="text-deep-black-600"
        />
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import PotionsGrid from "@/components/blocks/PotionsGrid.vue";
import Title from "@/components/ui/Title.vue";
import GradientTitle from "@/components/ui/GradientTitle.vue";
import OpenIcon from "@/components/icons/CaretDown.vue";
import CloseIcon from "@/components/icons/CaretUp.vue";
import Tooltip from "@/components/ui/Tooltip.vue";
import Btn from "@/components/ui/Button.vue";
import { CurrencyService } from "@/services/api/currency";
import { mapGetters } from "vuex";
import { getGas } from "@/services/api/gas";

export default {
  components: {
    CardContainer,
    CardBody,
    GradientTitle,
    Title,
    OpenIcon,
    CloseIcon,
    Tooltip,
    PotionsGrid,
    Btn,
  },
  props: {
    potions: {
      type: Array,
      default: () => [],
    },
    fiatCurrency: {
      type: String,
      default: "$",
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    gasUnits: { type: String, default: "840000" },
  },
  data() {
    return {
      showGasSaving: false,
      ethPrice: null,
      gas: null,
      webSocketConnection: null,
    };
  },
  watch: {
    "underlyingSelected.address": function () {
      if (this.underlyingSelected.address !== null) {
        this.showGasSaving = true;
      }
    },
  },
  computed: {
    ...mapGetters("potions/custom", ["underlyingSelected"]),
    formattedPrice() {
      return new Intl.NumberFormat(navigator.language, {
        style: "currency",
        currency: "USD",
      }).format(
        ((this.gas.ProposeGasPrice * 10e8 * parseFloat(this.gasUnits)) / 1e18) *
          this.ethPrice
      );
    },
  },
  methods: {
    potionSelected(payload) {
      this.$emit("potion-selected", payload);
    },
  },

  async mounted() {
    this.ethPrice = await CurrencyService.getEthToUsd();

    this.gas = this.gas = await getGas();
  },
};
</script>

<style scoped>
.accordion-transition {
  transition: max-height 0.2s;
}
::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
  border-radius: 15px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
}
::-webkit-scrollbar-track {
  @apply bg-white bg-opacity-0 rounded-full;
  backdrop-filter: blur(30px);
}
</style>
