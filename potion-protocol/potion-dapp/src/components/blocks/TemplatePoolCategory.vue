<template>
  <CardsGrid :title="name" :description="description">
    <template #cards>
      <PoolTemplateCard
        v-for="template in filteredTemplates"
        :key="`cloned-${template.id}`"
        :templateId="template.id"
        :criteriaSet="template.criteriaSet.criterias"
        :cloned="template.numPools"
        :size="template.size"
        :curve="template.curve"
        :pnl="template.pnlPercentage"
        :currency="stableCoinCollateral"
        :creator="template.creator"
      />
    </template>
    <template #loadmore>
      <div class="flex col-span-3 justify-center mt-6" v-if="canLoadMore">
        <Btn label="Show More" color="secondary-o" @click="loadMore"></Btn>
      </div>
    </template>
  </CardsGrid>
</template>

<script>
import PoolTemplateCard from "@/components/cards/PoolTemplateCard.vue";
import CardsGrid from "@/components/blocks/CardsGrid.vue";
import Btn from "@/components/ui/Button.vue";

export default {
  props: {
    name: {
      type: String,
      default: "",
    },
    templates: {
      type: Array,
    },
    description: {
      type: String,
      default: "",
    },
    pnl: {
      type: String,
      default: "0",
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
    canLoadMore: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    PoolTemplateCard,
    CardsGrid,
    Btn,
  },
  methods: {
    loadMore() {
      this.$emit("load-more");
    },
  },
  computed: {
    filteredTemplates() {
      return this.templates.filter((template) => template.criteriaSet !== null);
    },
  },
};
</script>
