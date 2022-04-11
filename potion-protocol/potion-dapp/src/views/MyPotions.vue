<template>
  <div v-if="activePotions.length > 0 || expiredPotions.length > 0">
    <MyPotions
      v-if="activePotions.length > 0"
      class="mb-10"
      title="Active Potions"
      description="Purchased Potions not expired."
      :potions="activePotions"
      :withdrawable="false"
      :stable-coin-collateral="stableCoinCollateral"
      :payouts="payouts"
      :redeemed="redeemed"
      @load-more="getMoreActivePotions(walletAddress)"
      :loadMore="activeCanLoadMore"
    />
    <MyPotions
      v-if="expiredPotions.length > 0"
      title="Expired Potions"
      description="Expired Potions ready to be withdrawn."
      :potions="expiredPotions"
      :withdrawable="true"
      :stable-coin-collateral="stableCoinCollateral"
      :payouts="payouts"
      :redeemed="redeemed"
      @load-more="getMoreExpiredPotions(walletAddress)"
      :loadMore="expiredCanLoadMore"
      @redeem="handleRedeem"
    />
  </div>
</template>

<script>
import MyPotions from "@/components/blocks/MyPotions.vue";
import { mapGetters, mapActions } from "vuex";

export default {
  components: {
    MyPotions,
  },
  methods: {
    ...mapActions("potions/user", ["redeemOToken"]),
    ...mapActions("potions/user", [
      "getMoreActivePotions",
      "getMoreExpiredPotions",
    ]),
    async handleRedeem(payload) {
      await this.redeemOToken({
        address: payload.address,
        quantity: payload.quantity,
      });
    },
  },
  computed: {
    ...mapGetters("wallet", ["walletAddress", "stableCoinCollateral"]),
    ...mapGetters("potions/user", [
      "expiredPotions",
      "activePotions",
      "activeCanLoadMore",
      "expiredCanLoadMore",
      "redeemed",
      "payouts",
    ]),
  },
};
</script>
