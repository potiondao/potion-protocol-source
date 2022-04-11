<template>
  <CardContainer :fullHeight="false">
    <CardBody class="flex-grow p-6">
      <Title label="My Pool #6" size="xxs" class="uppercase tracking-wide" />
      <div
        class="
          flex
          items-center
          justify-between
          border-b border-white border-opacity-10
          p-3
          mt-6
        "
      >
        <span class="font-medium">Total liquidity</span>
        <span class="font-bold">{{ liquidity }}</span>
      </div>
      <BalanceInput
        class="mt-10"
        :value="value"
        title="Add more funds"
        @value-updated="$emit('input', $event)"
        :error="inputError"
      />
      <div class="flex flex-col w-full py-6">
        <GasEstimationCard :gasUnits="gasUnits" />
      </div>
    </CardBody>
    <CardFooter>
      <div class="flex space-x-5 justify-items-center">
        <Btn
          label="Cancel edit"
          color="transparent"
          size="sm"
          @click="$emit('cancel-edit')"
        />
        <Btn
          label="Edit Pool"
          color="secondary"
          size="sm"
          @click="$emit('pool-edit')"
          :disabled="!enabled"
        />
      </div>
    </CardFooter>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Btn from "@/components/ui/Button.vue";
import Title from "@/components/ui/Title.vue";
import BalanceInput from "@/components/blocks/BalanceInput.vue";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";

export default {
  props: {
    liquidity: {
      type: String,
    },
    value: {
      type: String,
    },
    enabled: {
      type: Boolean,
      default: false,
    },
    gasUnits: {
      type: String,
      default: "21700",
    },
    inputError: { type: Boolean, default: false },
  },
  components: {
    CardContainer,
    CardBody,
    Title,
    CardFooter,
    Btn,
    BalanceInput,
    GasEstimationCard,
  },
  computed: {},
};
</script>
