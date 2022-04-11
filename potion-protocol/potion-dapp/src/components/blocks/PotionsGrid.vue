<template>
  <CardsGrid
    :title="title"
    :description="description"
    :show-heading="showHeading"
    :color="color"
    :size="size"
  >
    <template #cards>
      <PotionCard
        v-for="(potion, index) in potions"
        :key="index"
        :underlying="potion.underlyingAsset"
        :currency="stableCoinCollateral"
        @potion-selected="potionSelected"
        :oToken="{
          id: potion.id,
          address: potion.tokenAddress,
          strikePrice: potion.strikePrice,
          expirationUnix: potion.expiry,
          orderHistory: [],
        }"
      />
    </template>
    <template #loadmore>
      <div class="flex justify-center col-span-3 mt-6" v-if="loadMore">
        <Btn
          label="load more"
          color="secondary-o"
          @click="$emit('load-more')"
        ></Btn>
      </div>
    </template>
  </CardsGrid>
</template>

<script>
import PotionCard from "@/components/cards/PotionCard.vue";
import CardsGrid from "@/components/blocks/CardsGrid.vue";
import Btn from "@/components/ui/Button.vue";

export default {
  components: {
    PotionCard,
    CardsGrid,
    Btn,
  },
  props: {
    loadMore: {
      type: Boolean,
      default: false,
    },
    showHeading: {
      type: Boolean,
      default: true,
    },
    color: {
      type: String,
      default: "glass",
    },
    size: {
      type: String,
      default: "default",
    },
    title: {
      type: String,
      default: "",
    },
    description: {
      type: String,
      default: "",
    },
    potions: {
      type: Array,
      default: () => {
        return [];
      },
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  methods: {
    potionSelected(payload) {
      this.$emit("potion-selected", payload);
    },
  },
};
</script>
