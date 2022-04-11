<template>
  <div
    class="min-h-screen pt-5 px-6 pb-36 basic font-poppins text-dirty-white-300"
  >
    <MainHeader></MainHeader>
    <div class="container pt-8 mx-auto">
      <MyPoolsHeader
        :pools="myPoolsNumber"
        :liquidity="myPoolsLiquidityProvided"
        :pnl="myPoolsAveragePnl"
        :stableCoinCollateral="stableCoinCollateral"
        v-if="$route.path.includes('/pools/my-pools')"
      />
      <DiscoverPoolsHeader
        @start-pool-creation="startPoolCreation"
        v-else-if="$route.path.includes('/pools')"
      />
      <PoolsNav
        class="py-10"
        v-if="$route.path.includes('/pools')"
        :enable-user-route="connectedToMetamask"
        :routes="routes"
        :route-name="routeName"
      />
    </div>
    <transition
      enter-active-class="transition-all "
      leave-active-class="transition-all"
      enter-class="opacity-0 "
      enter-to-class="opacity-100"
      leave-class="opacity-100"
      leave-to-class="opacity-0 "
    >
      <router-view class="container mx-auto mb-10" />
    </transition>
  </div>
</template>

<script>
import DiscoverPoolsHeader from "@/components/cards/DiscoverPoolsHeader.vue";
import MainHeader from "@/components/Header.vue";
import MyPoolsHeader from "@/components/cards/MyPoolsHeader.vue";
import PoolsNav from "@/components/blocks/SecondLevelRouteNav.vue";
import { mapGetters } from "vuex";

export default {
  components: {
    DiscoverPoolsHeader,
    MainHeader,
    MyPoolsHeader,
    PoolsNav,
  },
  data() {
    return {
      routes: [
        {
          name: "DiscoverPools",
          label: "Discover Pools",
          alwaysVisible: true,
        },
        {
          name: "MyPools",
          label: "My Pools",
          alwaysVisible: false,
        },
      ],
    };
  },
  computed: {
    ...mapGetters("pools", [
      "myPools",
      "myPoolsNumber",
      "myPoolsLiquidityProvided",
      "myPoolsAveragePnl",
    ]),
    ...mapGetters("wallet", ["connectedToMetamask", "stableCoinCollateral"]),
    routeName() {
      return this.$route.name;
    },
  },
  methods: {
    startPoolCreation() {
      this.$router.push({ name: "PoolSetup" });
    },
  },
};
</script>

<style scoped>
.basic {
  background: linear-gradient(
    113.69deg,
    var(--deep-blue) 23.72%,
    var(--deep-black-900) 81.45%
  );
}
</style>
