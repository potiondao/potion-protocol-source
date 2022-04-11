<template>
  <UnderlyingSelection
    :underlyings="underlyings"
    @underlying-selected="setUnderlying"
  ></UnderlyingSelection>
</template>

<script>
import UnderlyingSelection from "@/components/blocks/CustomPoolCreation/UnderlyingsSelection.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  components: {
    UnderlyingSelection,
  },
  data() {
    return {
      categories: [
        {
          name: "All",
        },
        {
          name: "Lending Protocol",
        },
        {
          name: "AMM Dex",
        },
        {
          name: "Oracles",
        },
        {
          name: "Traditional Finance",
        },
      ],
    };
  },
  computed: {
    ...mapGetters("potions", ["underlyingsAvailable"]),
    ...mapGetters("potions/custom", ["underlyingSelected"]),
    underlyings() {
      return this.underlyingsAvailable.map((underlying) => {
        return {
          ...underlying,
          selected: underlying.address === this.underlyingSelected.address,
        };
      });
    },
  },
  async mounted() {
    await this.getAvailableUniqueUnderlyings();
  },
  methods: {
    ...mapActions("potions", ["getAvailableUniqueUnderlyings"]),
    ...mapActions("potions/custom", [
      "selectUnderlying",
      "selectDuration",
      "selectStrike",
      "getSimilarPotions",
      "getMaxStrikeFromUnderlying",
      "getPriceFromOracle",
    ]),
    async setUnderlying(address) {
      const underlying = this.underlyingsAvailable.find(
        (u) => u.address === address
      );
      this.selectUnderlying({
        address: underlying.address,
        symbol: underlying.symbol,
        name: underlying.name,
        image: underlying.image,
        price: "0",
      });
      this.selectDuration(null);
      this.selectStrike(null);
      await this.getMaxStrikeFromUnderlying(address);
      await this.getPriceFromOracle(address);
      this.getSimilarPotions("asset");
    },
  },
};
</script>
