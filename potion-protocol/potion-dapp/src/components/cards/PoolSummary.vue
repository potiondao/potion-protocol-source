<template>
  <CardContainer :fullHeight="false">
    <CardBody class="p-6">
      <Title label="My Pool #6" size="xxs" class="uppercase tracking-wide" />
      <div class="divide-y divide-white divide-opacity-10">
        <div class="w-full py-6 flex justify-between text-sm">
          <span>You're Providing</span>
          <span class="font-bold">{{ liquidityFormatted }} {{ currency }}</span>
        </div>
        <div class="w-full py-6 border-top flex-flex-col border-white">
          <span>You're Selling insurance for</span>
          <UnderlyingRecapCard :underlyings="underlyings" class="mt-6" />
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
          @click="$emit('back')"
        >
          <template v-slot:pre-icon>
            <CaretLeft class="mr-2 h-4"></CaretLeft>
          </template>
        </Btn>
        <Btn
          label="next"
          color="secondary"
          size="sm"
          class="min-w-[8em]"
          @click="$emit('next')"
          :disabled="nextDisabled"
        >
          <template v-slot:post-icon>
            <CaretRight class="ml-2 h-4"></CaretRight>
          </template>
        </Btn>
      </div>
    </CardFooter>
  </CardContainer>
</template>
<script>
import Title from "@/components/ui/Title.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Btn from "@/components/ui/Button.vue";
import UnderlyingRecapCard from "@/components/cards/UnderlyingRecapCard.vue";
import CaretRight from "@/components/icons/CaretRight.vue";
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
    nextDisabled: {
      type: Boolean,
      default: false,
    },
    currency: {
      type: String,
      default: "",
    },
  },
  components: {
    CardContainer,
    CardBody,
    Title,
    CardFooter,
    Btn,
    UnderlyingRecapCard,
    CaretRight,
    CaretLeft,
  },
  computed: {
    liquidityFormatted() {
      return formatNumber(this.liquidity);
    },
  },
};
</script>
