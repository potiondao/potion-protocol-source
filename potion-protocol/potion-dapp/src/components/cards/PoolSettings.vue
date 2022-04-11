<template>
  <CardContainer :fullHeight="false">
    <CardBody class="flex-grow p-6">
      <Title label="My Pool #6" size="xxs" class="uppercase tracking-wide" />
      <div class="my-8 text-sm leading-loose">
        Amount of stable coin you want to deposit in the pool.
      </div>
      <BalanceInput
        :value="value"
        title="You're providing"
        @value-updated="$emit('input', $event)"
        :error="liquidityError"
      />
    </CardBody>
    <CardFooter>
      <div class="flex w-full justify-center space-x-5">
        <Btn
          label="cancel"
          color="transparent"
          size="sm"
          class="min-w-[8em]"
          @click="$emit('back')"
        >
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
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import Btn from "@/components/ui/Button.vue";
import Title from "@/components/ui/Title.vue";
import BalanceInput from "@/components/blocks/BalanceInput.vue";
import CaretRight from "@/components/icons/CaretRight.vue";

export default {
  props: {
    value: {
      type: String,
    },
    nextDisabled: {
      type: Boolean,
    },
    liquidityError: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    CardContainer,
    CardBody,
    Title,
    CardFooter,
    Btn,
    BalanceInput,
    CaretRight,
  },
};
</script>
