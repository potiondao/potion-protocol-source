<template>
  <CardsGrid :title="title" :description="description">
    <template #cards>
      <MyPotionCard
        v-for="(potion, index) in potions"
        :key="`my-potion-${index}-${potion.otoken.id}`"
        :address="potion.otoken.id"
        :underlyingAddress="potion.otoken.underlyingAsset.id"
        :asset="assembleAsset(potion.otoken.underlyingAsset)"
        :strike="potion.otoken.strikePrice"
        :expiration="potion.otoken.expiry"
        :quantity="potion.numberOfOTokens"
        :payout="formattedPayout(potion.otoken.id)"
        :withdrawable="canRedeem(potion.otoken.id)"
        :currency="stableCoinCollateral"
        :redeemed="isRedeemed(potion.otoken.id)"
        @redeem="redeemOToken"
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
import MyPotionCard from "@/components/cards/MyPotion.vue";
import CardsGrid from "@/components/blocks/CardsGrid.vue";
import Btn from "@/components/ui/Button.vue";
export default {
  components: {
    MyPotionCard,
    CardsGrid,
    Btn,
  },
  props: {
    title: {
      type: String,
      default: "",
    },
    potions: {
      type: Array,
      default: () => [],
    },
    withdrawable: {
      type: Boolean,
      default: false,
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    payouts: {
      type: Object,
      default: () => {
        return {};
      },
    },
    redeemed: {
      type: Object,
      default: () => {
        return {};
      },
    },
    description: {
      type: String,
      default: "",
    },
    loadMore: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    redeemOToken(payload) {
      this.$emit("redeem", payload);
    },
    assembleAsset(underlying) {
      return {
        name: underlying.symbol,
        image: `https://s.gravatar.com/avatar/da32ff79613d46d206a45e5a3018acf3?size=496&default=retro`,
      };
    },
    formattedPayout(oTokenAddress) {
      try {
        return this.payouts[oTokenAddress];
      } catch (error) {
        return "N/A";
      }
    },
    isRedeemed(oTokenAddress) {
      return this.redeemed[oTokenAddress];
    },
    canRedeem(oTokenAddress) {
      try {
        const previouslyRedeemed = this.isRedeemed(oTokenAddress);
        // withdrawable (prop) is only set to true with expired potions.
        // Redeemed is set in the store, and is true if the wallet owns
        // more than 0 oTokens.
        return (
          this.withdrawable &&
          !previouslyRedeemed &&
          parseFloat(this.formattedPayout(oTokenAddress)) > 0
        );
      } catch (error) {
        return false;
      }
    },
  },
};
</script>

<style scoped></style>
