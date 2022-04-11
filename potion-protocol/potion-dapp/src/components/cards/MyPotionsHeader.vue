<template>
  <CardContainer>
    <CardBody class="grid grid-flow-row grid-cols-3 gap-5 p-6 lg:grid-cols-4">
      <Title class="col-span-3 lg:col-span-1" label="My Summary" />

      <LabelValue
        class="self-end"
        size="lg"
        title="Active Potions"
        :value="activePotions.length.toString()"
      />
      <LabelValue
        class="self-end"
        size="lg"
        title="Expired Potions"
        :value="expiredPotions.length.toString()"
      />
      <LabelValue
        class="self-end"
        size="lg"
        title="Available Payout"
        :value="availablePayout"
        :symbol="stableCoinCollateral"
        data-test="display-available-payout"
      />
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import Title from "@/components/ui/Title.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";

export default {
  props: {
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    availablePayout: {
      type: String,
      default: "",
    },
    activePotions: {
      type: Array,
      default: () => [],
    },
    expiredPotions: {
      type: Array,
      default: () => [],
    },
  },
  components: {
    CardContainer,
    CardBody,
    Title,
    LabelValue,
  },
};
</script>
