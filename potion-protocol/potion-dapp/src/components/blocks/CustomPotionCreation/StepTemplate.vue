<template>
  <CardBody class="pt-4 px-6">
    <div class="flex justify-between mb-4">
      <Title label="Your put recipe" class="uppercase" size="xs" />
      <Title :label="stepTitle" class="uppercase hidden xl:block" size="xs" />
      <Btn color="transparent" label="" size="icon" @click="resetPotion">
        <template v-slot:pre-icon>
          <XIcon class="h-4" weight="bold" />
        </template>
      </Btn>
    </div>
    <div class="flex flex-col xl:flex-row">
      <div class="w-full xl:w-1/4">
        <Sidebar
          @stepSelected="changeStep"
          :steps-enabled="stepsEnabled"
          :stable-coin-collateral="stableCoinCollateral"
        />
      </div>
      <div class="w-full xl:w-3/4 px-4">
        <Title
          :label="stepTitle"
          class="uppercase xl:hidden text-center my-4"
          size="xs"
        />
        <component
          :is="stepComponent"
          :stable-coin-collateral="stableCoinCollateral"
        ></component>
        <div class="flex justify-end w-full mt-10 space-x-6">
          <Btn
            size="sm"
            color="transparent"
            class="uppercase"
            @click="backButton"
            :label="backButtonText"
          >
            <template v-slot:pre-icon v-if="step > 1">
              <CaretLeft class="mr-2 h-4"></CaretLeft>
            </template>
          </Btn>
          <Btn
            :disabled="!stepsEnabled[step]"
            @click="nextStep()"
            size="sm"
            color="secondary"
            :label="step === 4 ? 'create potion' : 'next'"
          >
            <template v-slot:post-icon v-if="step < 4">
              <CaretRight class="ml-2 h-4"></CaretRight>
            </template>
          </Btn>
        </div>
      </div>
    </div>
  </CardBody>
</template>

<script>
import CaretRight from "@/components/icons/CaretRight.vue";
import CaretLeft from "@/components/icons/CaretLeft.vue";
import CardBody from "@/components/ui/CardBody.vue";
import Sidebar from "@/components/blocks/CustomPotionCreation/Sidebar.vue";
import StepAsset from "@/components/blocks/CustomPotionCreation/StepAsset.vue";
import StepStrike from "@/components/blocks/CustomPotionCreation/StepStrike.vue";
import StepDuration from "@/components/blocks/CustomPotionCreation/StepDuration.vue";
import StepReview from "@/components/blocks/CustomPotionCreation/StepReview.vue";
import XIcon from "@/components/icons/XIcon.vue";
import Btn from "@/components/ui/Button.vue";
import Title from "@/components/ui/Title.vue";

const stepData = {
  1: {
    component: StepAsset,
    title: "Choose Asset",
  },
  2: {
    component: StepStrike,
    title: "Strike Price",
  },
  3: {
    component: StepDuration,
    title: "Duration",
  },
  4: {
    component: StepReview,
    title: "Review and Create",
  },
};

export default {
  props: {
    step: {
      type: Number,
      default: 0,
    },
    stepsEnabled: {
      type: Array,
      default: () => [],
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  components: {
    CardBody,
    Sidebar,
    XIcon,
    Btn,
    CaretRight,
    CaretLeft,
    Title,
  },
  computed: {
    selectStep() {
      const index = this.step.toString();
      return index in stepData ? stepData[index] : {};
    },
    stepComponent() {
      return this.selectStep.component;
    },
    stepTitle() {
      return this.selectStep.title;
    },
    backButtonText() {
      return this.step > 1 ? "Back" : "Cancel";
    },
  },
  methods: {
    changeStep(step) {
      this.$emit("step-selected", step);
    },
    resetPotion() {
      this.$emit("reset-potion");
    },
    createPotion() {
      this.$emit("create-potion");
    },
    backButton() {
      if (this.step > 1) {
        this.changeStep(this.step - 1);
      } else {
        this.resetPotion();
      }
    },
    nextStep() {
      if (this.step < 4) {
        this.changeStep(this.step + 1);
      } else {
        this.createPotion();
      }
    },
  },
};
</script>
