<template>
  <header class="w-full">
    <div class="container flex flex-wrap items-center justify-between mx-auto">
      <router-link :to="{ name: 'DiscoverPotions' }">
        <img
          src="../assets/logo-dark.svg"
          alt="Potion Logo"
          class="w-auto h-5"
        />
      </router-link>
      <div class="flex space-x-6">
        <router-link
          active-class="header-link-active"
          v-for="route in routes"
          :key="route.name"
          :to="{ name: route.name }"
          class="p-2 transition uppercase text-sm"
          >{{ route.label }}</router-link
        >
      </div>
      <div>
        <Btn
          size="sm"
          color="secondary"
          :label="address"
          @click="connect"
          v-if="metamaskInstalled"
        />

        <Btn
          href="https://metamask.io/download"
          size="sm"
          mode="link"
          target="_blank"
          color="secondary"
          label="Install Metamask"
          v-else
        />
      </div>
    </div>
  </header>
</template>

<script>
import Btn from "./ui/Button.vue";
import { mapActions, mapGetters } from "vuex";

export default {
  components: {
    Btn,
  },
  data() {
    return {
      routes: [
        {
          name: "DiscoverPotions",
          label: "Buy Potion",
        },
        {
          name: "DiscoverPools",
          label: "Pool Liquidity",
        },
      ],
    };
  },
  computed: {
    address() {
      if (this.metamaskInstalled && this.ens) {
        if (!this.ens.includes(".eth")) {
          return `${this.ens.substr(0, 7)}...`;
        } else {
          return this.ens;
        }
      }
      return "connect";
    },
    ...mapGetters("wallet", [
      "connectedToMetamask",
      "metamaskInstalled",
      "walletAddress",
      "ens",
    ]),
  },
  methods: {
    ...mapActions("wallet", [
      "checkProvider",
      "requestAccounts",
      "getCollateralBalance",
      "connectToMetamask",
    ]),
    ...mapActions("pools", ["getMyPools"]),
    ...mapActions("potions/user", ["getPotions", "getPrices"]),
    async connect() {
      await this.connectToMetamask();
      await this.getCollateralBalance(this.walletAddress);
    },
  },
};
</script>
<style scoped>
.header-link-active {
  @apply shadow-md rounded-md bg-gradient-to-r from-primary-500 to-primary-400 text-dirty-white-400;
}
</style>
