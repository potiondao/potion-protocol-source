<template>
  <div class="w-full">
    <div class="mb-4">
      <router-link :to="{ name: 'MyPools' }">
        <Btn color="transparent" label="Back" size="sm">
          <template v-slot:pre-icon>
            <CaretLeft class="mr-1 h-3"></CaretLeft>
          </template>
        </Btn>
      </router-link>
    </div>
    <CardContainer>
      <CardBody class="grid grid-flow-row grid-cols-3 lg:grid-cols-6 gap-5 p-6">
        <div
          class="grid grid-flow-row grid-cols-1 col-span-2 lg:col-span-1 gap-3"
        >
          <DataLabel label="Status" />
          <Tag :label="activeStatusLabel" class="place-self-start uppercase" />
        </div>
        <LabelTokens title="Assets" :tokens="tokens" />
        <LabelValue title="Total Liquidity" :value="size" :symbol="currency" />
        <LabelValue title="Utilization" :value="utilization" symbol="%" />
        <LabelValue title="PnL" :value="pnl" symbol="%" />
        <div class="flex justify-start lg:justify-center items-center">
          <Btn
            size="sm"
            label="edit"
            @click="$emit('open-edit')"
            color="secondary-o"
            class="min-w-[8em]"
            weight="bold"
          />
        </div>
      </CardBody>
    </CardContainer>
  </div>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import Btn from "@/components/ui/Button.vue";
import Tag from "@/components/ui/Tag.vue";
import DataLabel from "@/components/ui/DataLabel.vue";
import LabelTokens from "@/components/blocks/LabelTokens.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import CaretLeft from "@/components/icons/CaretLeft.vue";

export default {
  props: {
    active: {
      type: Boolean,
      default: true,
    },
    name: {
      type: String,
    },
    category: {
      type: String,
    },
    tokens: {
      type: Array,
    },
    pnl: {
      type: String,
      default: "0",
    },
    utilization: {
      type: String,
      default: "0",
    },
    size: {
      type: String,
      default: "0",
    },
    currency: {
      type: String,
      default: "",
    },
    poolHash: {
      type: String,
      default: "",
    },
  },
  components: {
    CardContainer,
    CardBody,
    Btn,
    Tag,
    LabelTokens,
    LabelValue,
    DataLabel,
    CaretLeft,
  },
  computed: {
    activeStatusLabel() {
      return this.active ? "Active" : "Expired";
    },
  },
  methods: {
    alert(message) {
      alert(message);
    },
  },
};
</script>
