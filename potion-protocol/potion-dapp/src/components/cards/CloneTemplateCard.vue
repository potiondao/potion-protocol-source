<template>
  <CardContainer :fullHeight="false">
    <CardBody class="flex-grow px-5 py-4">
      <DataLabel label="Add liquidity" class="mb-5" />
      <BalanceInput
        class="mt-10"
        :value="liquidity"
        title="You're providing"
        @value-updated="updateLiquidity"
        :error="disableClone"
      />
      <div class="text-secondary-500 mt-4">
        By providing liquidity you’re creating your pool cloning this template.
      </div>
      <div
        class="
          flex flex-wrap
          justify-between
          pt-3
          mt-10
          border-t border-deep-black-600
        "
      >
        <div class="flex flex-col w-full py-6">
          <GasEstimationCard :gasUnits="gasUnits" />
        </div>
      </div>
    </CardBody>
    <CardFooter>
      <div class="flex justify-center w-full">
        <Btn
          label="add liquidity"
          color="secondary"
          size="sm"
          @click="$emit('cloneTemplate', liquidity)"
          :disabled="disableClone"
        >
          <template v-slot:pre-icon>
            <UploadSimple class="mr-2 h-4" weight="bold"></UploadSimple>
          </template>
        </Btn>
      </div>
    </CardFooter>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Btn from "@/components/ui/Button.vue";
import DataLabel from "@/components/ui/DataLabel.vue";
import BalanceInput from "@/components/blocks/BalanceInput.vue";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";
import UploadSimple from "@/components/icons/UploadSimple.vue";
import { mapGetters } from "vuex";

export default {
  components: {
    CardContainer,
    CardBody,
    CardFooter,
    Btn,
    DataLabel,
    BalanceInput,
    GasEstimationCard,
    UploadSimple,
  },
  props: {
    gasUnits: {
      type: String,
      default: "21000",
    },
  },
  data() {
    return {
      liquidity: "100",
    };
  },
  methods: {
    updateLiquidity(value) {
      this.liquidity = value;
    },
  },
  computed: {
    ...mapGetters("wallet", ["stableCoinCollateralBalance"]),
    disableClone() {
      return parseFloat(this.liquidity) >
        parseFloat(this.stableCoinCollateralBalance) ||
        parseFloat(this.liquidity) < 0
        ? true
        : false;
    },
  },
};
</script>
