<template>
  <div id="app" class="font-medium">
    <transition
      enter-active-class="transition-all"
      leave-active-class="transition-all"
      enter-class="opacity-0"
      enter-to-class="opacity-100"
      leave-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <Spinner v-if="isLoading" />
    </transition>
    <router-view />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { initProvider } from "@/services/ethers";
import Spinner from "@/components/ui/Spinner.vue";

export default {
  components: {
    Spinner,
  },
  computed: {
    ...mapGetters(["isLoading"]),
    ...mapGetters("wallet", ["connectedToMetamask"]),
  },
  methods: {
    ...mapActions([
      "getBlockEpoch",
      "getBlockEpochBackground",
      "getBlockGasLimit",
    ]),
    ...mapActions("wallet", ["setChangedAccount"]),
  },
  async mounted() {
    await this.getBlockEpoch();
    await this.getBlockGasLimit();
    const provider = await initProvider();
    provider.on("block", () => {
      this.getBlockEpochBackground();
    });
    window.ethereum.on("accountsChanged", (accounts) => {
      console.log("New account detected: ", accounts);
      window.location.reload();
    });
    //@ts-expect-error any
    window.ethereum.on("chainChanged", (chainId) => {
      // Handle the new chain.
      // Correctly handling chain changes can be complicated.
      // We recommend reloading the page unless you have good reason not to.
      console.log("New chain detected: ", chainId);
      window.location.reload();
    });
  },
};
</script>
<style>
.caret-down {
  height: 11px;
  width: 11px;
  border-bottom: 1px solid #fcfafa;
  border-right: 1px solid #fcfafa;
  margin-top: -6px;
}
.toast-gradient-background {
  background: linear-gradient(116.18deg, #262140 26.75%, #2e284f 75.87%);
}
.Vue-Toastification__progress-bar {
  opacity: 0 !important;
}
.Vue-Toastification__toast {
  padding: 0;
}

.capitalize {
  text-transform: capitalize;
}
</style>
