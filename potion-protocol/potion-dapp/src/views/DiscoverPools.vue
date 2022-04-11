<template>
  <div class="grid grid-flow-row grid-cols-1 gap-6">
    <TemplatePoolCategory
      v-if="mostCookedTemplates && mostCookedTemplates.length > 0"
      name="Most Cloned"
      description="Pools that have been cloned the most times."
      :can-load-more="mostCookedTemplatesCanLoadMore"
      :templates="mostCookedTemplates"
      :stableCoinCollateral="stableCoinCollateral"
      @load-more="loadMoreTemplates('byNumber')"
    />
    <TemplatePoolCategory
      v-if="biggestTemplates && biggestTemplates.length > 0"
      name="Largest"
      description="Pools that have the most total liquidity."
      :can-load-more="biggestTemplatesCanLoadMore"
      :templates="biggestTemplates"
      :stableCoinCollateral="stableCoinCollateral"
      @load-more="loadMoreTemplates('bySize')"
    />
    <TemplatePoolCategory
      v-if="highestPnlTemplates && highestPnlTemplates.length > 0"
      name="Top Gainers"
      description="Top PnL since creation."
      :can-load-more="highestPnlTemplatesCanLoadMore"
      :templates="highestPnlTemplates"
      :stableCoinCollateral="stableCoinCollateral"
      @load-more="loadMoreTemplates('byPnl')"
    />
  </div>
</template>

<script>
import TemplatePoolCategory from "@/components/blocks/TemplatePoolCategory.vue";
import { mapActions, mapGetters } from "vuex";

const isEmpty = (arr) => arr.length === 0;

export default {
  components: {
    TemplatePoolCategory,
  },
  computed: {
    ...mapGetters("pools", [
      "mostCookedTemplates",
      "biggestTemplates",
      "highestPnlTemplates",
      "mostCookedTemplatesCanLoadMore",
      "biggestTemplatesCanLoadMore",
      "highestPnlTemplatesCanLoadMore",
    ]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
  },
  async mounted() {
    const loadRequired = [
      this.mostCookedTemplates,
      this.biggestTemplates,
      this.highestPnlTemplates,
    ].every(isEmpty);
    if (loadRequired) {
      await this.getPopularTemplates();
    }
  },
  methods: {
    ...mapActions("pools", ["getPopularTemplates", "loadMoreTemplates"]),
  },
};
</script>
