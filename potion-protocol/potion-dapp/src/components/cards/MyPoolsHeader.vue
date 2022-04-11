<template>
  <CardContainer>
    <CardBody
      class="sm:grid grid-flow-row gap-5 grid-cols-3 lg:grid-cols-4 p-6"
    >
      <div class="col-span-4 lg:col-span-1">
        <Title label="My Summary" />
      </div>
      <LabelValue
        class="self-end"
        size="lg"
        title="Total Pools"
        :value="pools"
      />
      <LabelValue
        class="self-end"
        size="lg"
        title="Average PnL"
        :value="pnl"
        symbol="%"
      />
      <LabelValue
        class="self-end"
        size="lg"
        title="Total Liquidity"
        :value="liquidity"
        :symbol="stableCoinCollateral"
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
    pools: {
      type: String,
      default: "0",
    },
    liquidity: {
      type: String,
      default: "0",
    },
    pnl: {
      type: String,
      default: "0",
    },
    stableCoinCollateral: {
      type: String,
      default: "",
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
