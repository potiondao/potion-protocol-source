<template>
  <CardContainer :fullHeight="false">
    <CardBody class="p-6">
      <Title label="My Pool #6" size="xxs" class="uppercase tracking-wide" />
      <div class="divide-y divide-white divide-opacity-10">
        <div class="w-full py-6 flex justify-between text-sm">
          <span>You're Providing</span>
          <span class="font-bold">{{ liquidityFormatted }} {{ currency }}</span>
        </div>
        <div class="py-6 flex flex-col">
          <span class="mb-4">You're selling insurance for</span>
          <UnderlyingRecapCard :underlyings="underlyings" />
        </div>

        <div class="flex flex-col w-full py-6">
          <GasEstimationCard :gasUnits="gasUnits" />
        </div>
      </div>
    </CardBody>
    <CardFooter>
      <div class="flex w-full justify-center space-x-5">
        <Btn
          label="back"
          color="transparent"
          size="sm"
          class="min-w-[8em]"
          @click="$emit('navigationBack')"
        >
          <template v-slot:pre-icon>
            <CaretLeft class="mr-2 h-4"></CaretLeft>
          </template>
        </Btn>
        <Btn
          label="create pool"
          color="secondary"
          size="sm"
          class="min-w-[8em]"
          @click="$emit('createPool')"
        />
      </div>
    </CardFooter>
  </CardContainer>
</template>
<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Title from "@/components/ui/Title.vue";
import UnderlyingRecapCard from "@/components/cards/UnderlyingRecapCard.vue";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";
import Btn from "@/components/ui/Button.vue";
import CaretLeft from "@/components/icons/CaretLeft.vue";
import { formatNumber } from "@/helpers";

export default {
  props: {
    liquidity: {
      type: String,
    },
    underlyings: {
      type: Array,
    },
    currency: {
      type: String,
      default: "",
    },
    gasUnits: {
      type: String,
      default: "21700",
    },
  },
  components: {
    CardContainer,
    CardBody,
    CardFooter,
    Btn,
    Title,
    UnderlyingRecapCard,
    GasEstimationCard,
    CaretLeft,
  },
  computed: {
    liquidityFormatted() {
      return formatNumber(this.liquidity);
    },
  },
};
</script>
