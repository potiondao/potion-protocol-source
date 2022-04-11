<template>
  <CardContainer :fullHeight="false">
    <template v-if="step > 0">
      <StepTemplate
        :step="step"
        :steps-enabled="stepsEnabled"
        :stable-coin-collateral="stableCoinCollateral"
        @step-selected="stepSelected"
        @create-potion="createPotion"
        @reset-potion="resetPotion"
      ></StepTemplate>
      <SuggestedPotions
        v-if="step > 0"
        @potion-selected="potionSelected"
        :potions="suggestedPotions"
        :stable-coin-collateral="stableCoinCollateral"
      />
    </template>
    <WelcomeState
      @start-potion-creation="startPotionCreation"
      v-else
    ></WelcomeState>
  </CardContainer>
</template>

<script>
import WelcomeState from "@/components/blocks/CustomPotionCreation/WelcomeState.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import StepTemplate from "@/components/blocks/CustomPotionCreation/StepTemplate.vue";
import SuggestedPotions from "@/components/blocks/CustomPotionCreation/SuggestedPotions.vue";

export default {
  components: {
    CardContainer,
    SuggestedPotions,
    WelcomeState,
    StepTemplate,
  },
  props: {
    step: {
      type: Number,
      default: 0,
    },
    stepsEnabled: {
      type: Array,
      default: () => [],
    },
    suggestedPotions: {
      type: Array,
      default: () => [],
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  methods: {
    startPotionCreation() {
      this.$emit("start-potion-creation");
    },
    stepSelected(step) {
      this.$emit("step-selected", step);
    },
    createPotion() {
      this.$emit("create-potion");
    },
    resetPotion() {
      this.$emit("reset-potion");
    },
    potionSelected(payload) {
      this.$emit("potion-selected", payload);
    },
  },
};
</script>
