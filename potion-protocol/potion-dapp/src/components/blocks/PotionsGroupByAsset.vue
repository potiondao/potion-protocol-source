<template>
  <CardContainer class="py-4 px-6 w-full">
    <div class="flex items-center space-x-1.5 pb-8">
      <TokenIcon :name="asset.name" :address="asset.address" size="2xl" />
      <div class="text-3xl font-extrabold uppercase">{{ asset.name }}</div>
    </div>
    <div
      class="
        grid
        w-full
        grid-cols-1
        gap-5
        md:grid-cols-2
        lg:grid-cols-3
        xl:grid-cols-4
        grid-flow-row
      "
    >
      <PotionCard
        v-for="(potion, index) in potions"
        :key="index"
        :underlying="potion.underlyingAsset"
        :oToken="{
          address: potion.tokenAddress,
          strikePrice: potion.strikePrice,
          expirationUnix: potion.expiry,
          orderHistory: [],
        }"
      />
    </div>
  </CardContainer>
</template>

<script>
import dayjs from "dayjs";
import { get as _get } from "lodash-es";
import CardContainer from "../ui/CardContainer.vue";
import PotionCard from "../cards/PotionCard.vue";
import TokenIcon from "../icons/TokenIcon.vue";

export default {
  components: {
    CardContainer,
    PotionCard,
    TokenIcon,
  },
  props: {
    underlyingAsset: {
      type: Object,
      default: () => {
        return {
          symbol: "",
          image: "",
          id: "",
        };
      },
    },
    potions: {
      type: Array,
      default: () => {
        return [];
      },
    },
  },
  methods: {
    getStrikeInfo(potion) {
      return {
        value: potion.strikePrice,
        expiration: dayjs.unix(potion.expiry).toString(),
      };
    },
  },
  computed: {
    asset() {
      return {
        name: _get(this, ["underlyingAsset", "symbol"], ""),
        address: _get(this, ["underlyingAsset", "id"], ""),
      };
    },
  },
};
</script>
