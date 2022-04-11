<template>
  <CardContainer class="justify-between" fullHeight>
    <CardBody class="p-4">
      <div class="grid grid-flow-row grid-cols-2 gap-6">
        <div class="flex col-span-2">
          <Tag :label="activeStatusLabel" class="place-self-start uppercase" />
        </div>
        <LabelTokens
          class="capitalize"
          labelSize="md"
          title="Assets"
          :tokens="tokensFlat"
        />
        <LabelValue
          size="md"
          title="Total Size"
          :value="liquidity"
          :symbol="currency"
        />
        <LabelValue
          size="md"
          title="Utilization"
          :value="utilization"
          symbol="%"
        />
        <LabelValue
          size="md"
          title="PnL"
          :value="pnl"
          symbol="%"
          :valueColor="pnlColor"
        />
      </div>
    </CardBody>
    <CardFooter>
      <router-link :to="{ name: 'Pool', params: { hash: poolHash } }">
        <Btn size="sm" color="secondary" label="Check pool" />
      </router-link>
    </CardFooter>
  </CardContainer>
</template>

<script>
import Btn from "@/components/ui/Button.vue";
import CardBody from "@/components/ui/CardBody.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import CardFooter from "@/components/ui/CardFooter.vue";
import LabelTokens from "@/components/blocks/LabelTokens.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import Tag from "@/components/ui/Tag.vue";
import { getPnlColor } from "@/helpers";

export default {
  components: {
    Btn,
    CardBody,
    CardContainer,
    CardFooter,
    LabelTokens,
    LabelValue,
    Tag,
  },
  props: {
    tag: {
      type: String,
      default: "",
    },
    title: {
      type: String,
      default: "",
    },
    tokens: {
      type: Array,
      default: () => [],
    },
    pnl: {
      type: String,
      default: "",
    },
    utilization: {
      type: String,
      default: "",
    },
    liquidity: {
      type: String,
      default: "",
    },
    poolHash: {
      type: String,
      default: "",
    },
    active: {
      type: Boolean,
      default: true,
    },
    currency: {
      type: String,
      default: "",
    },
  },
  computed: {
    activeStatusLabel() {
      return this.active ? "Active" : "Expired";
    },
    pnlColor() {
      return getPnlColor(parseFloat(this.pnl));
    },
    tokensFlat() {
      return this.tokens.map((x) => {
        return {
          address: x.criteria.underlyingAsset.address,
          decimals: x.criteria.underlyingAsset.decimals,
          name: x.criteria.underlyingAsset.name,
          symbol: x.criteria.underlyingAsset.symbol,
        };
      });
    },
  },
};
</script>
