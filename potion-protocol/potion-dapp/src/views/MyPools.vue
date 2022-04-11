<template>
  <div
    class="
      grid
      w-full
      gap-6
      grid-cols-1
      md:grid-cols-2
      lg:grid-cols-3
      grid-flow-row
    "
  >
    <router-link :to="{ name: 'PoolSetup' }">
      <NewPool label="Create pool from scratch"></NewPool>
    </router-link>
    <MyPool
      v-for="pool in myPools"
      :key="pool.id"
      :pnl="formatPercentage(pool.pnlPercentage)"
      :utilization="formatUtilization(pool.utilization)"
      :poolHash="pool.id"
      :tokens="getTokens(pool)"
      :liquidity="pool.size"
      :currency="stableCoinCollateral"
    />
    <div class="flex justify-center col-span-3" v-if="myPoolsCanLoadMore">
      <Btn label="Show More" color="secondary-o" @click="getMyPools"></Btn>
    </div>
  </div>
</template>

<script>
import MyPool from "@/components/cards/MyPool.vue";
import NewPool from "@/components/cards/NewCard.vue";
import Btn from "@/components/ui/Button.vue";
import { mapGetters, mapActions } from "vuex";
import { get as _get } from "lodash-es";

export default {
  components: {
    MyPool,
    NewPool,
    Btn,
  },
  methods: {
    ...mapActions("pools", ["getMyPools"]),
    formatPercentage(value) {
      return parseFloat(value).toFixed(2);
    },
    formatUtilization(value) {
      return (parseFloat(value) * 100).toFixed(2);
    },
    getTokens(pool) {
      return _get(pool, ["template", "criteriaSet", "criterias"], []);
    },
  },
  computed: {
    ...mapGetters("pools", ["myPools", "myPoolsCanLoadMore"]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
  },
};
</script>
