<template>
  <div class="grid grid-flow-row grid-cols-1 gap-6">
    <PotionsGrid
      class="py-4 px-6"
      title="Most Purchased"
      description="Potions that have been purchased the most times."
      v-if="mostPurchased.length > 0"
      :potions="mostPurchased"
      :load-more="mostPurchasedCanLoadMore"
      :stable-coin-collateral="stableCoinCollateral"
      @potion-selected="openPurchaseModal"
      @load-more="loadMorePotions('mostPurchased')"
    />
    <PotionsGrid
      class="py-4 px-6"
      title="Most Collateralized"
      description="Top Potions by Locked Collateral."
      v-if="mostCollateralized.length > 0"
      :potions="mostCollateralized"
      :load-more="mostCollateralizedCanLoadMore"
      :stable-coin-collateral="stableCoinCollateral"
      @potion-selected="openPurchaseModal"
      @load-more="loadMorePotions('mostCollateralized')"
    />
  </div>
</template>

<script>
import PotionsGrid from "@/components/blocks/PotionsGrid.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  components: {
    PotionsGrid,
  },
  computed: {
    ...mapGetters("wallet", ["stableCoinCollateral"]),
    ...mapGetters("potions/existing", [
      "mostPurchased",
      "mostCollateralized",
      "mostPurchasedCanLoadMore",
      "mostCollateralizedCanLoadMore",
    ]),
  },
  methods: {
    ...mapActions("potions/existing", ["openPurchaseModal", "loadMorePotions"]),
  },
};
</script>
