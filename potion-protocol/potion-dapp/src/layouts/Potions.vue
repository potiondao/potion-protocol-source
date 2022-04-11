<template>
  <div
    class="min-h-screen pt-5 px-6 pb-36 basic font-poppins text-dirty-white-300"
    :class="{
      'overflow-hidden h-screen w-screen absolute inset-0': statusBarOpened,
    }"
  >
    <MainHeader></MainHeader>
    <div class="container pt-8 mx-auto">
      <CustomPotionCreation
        class="z-50"
        v-if="$route.name === 'DiscoverPotions'"
        :step="currentStep"
        :steps-enabled="stepsEnabled"
        :suggested-potions="suggestedPotions"
        :stable-coin-collateral="stableCoinCollateral"
        @start-potion-creation="startPotionCreation"
        @step-selected="selectStep"
        @create-potion="createPotion"
        @reset-potion="resetCustomPotion"
        @potion-selected="openPurchaseModal"
      />
      <MyPotionsHeader
        v-if="$route.name === 'MyPotions'"
        :stable-coin-collateral="stableCoinCollateral"
        :active-potions="activePotions"
        :expired-potions="expiredPotions"
        :available-payout="availablePayout"
      />
      <PotionsNav
        class="py-10"
        :enable-user-route="connectedToMetamask"
        :routes="routes"
        :route-name="routeName"
      />
    </div>
    <transition
      enter-active-class="transition-all"
      leave-active-class="transition-all"
      enter-class="opacity-0 "
      enter-to-class="opacity-100"
      leave-class="opacity-100"
      leave-to-class="opacity-0 "
    >
      <router-view class="container mx-auto mb-10" />
    </transition>
    <div
      class="transition"
      :class="{
        'absolute inset-0 z-50 w-screen h-screen bg-deep-black-900 blurred':
          statusBarOpened,
      }"
    ></div>
    <transition
      enter-active-class="transition-all ease-out"
      leave-active-class="transition-all ease-in"
      enter-class="transform translate-y-full"
      enter-to-class="transform translate-y-0"
      leave-class="transform translate-y-0"
      leave-to-class="transform translate-y-full"
    >
      <PotionStatusBar
        v-if="$route.name === 'DiscoverPotions' && statusBarOpened"
        class="z-[100]"
        v-model="modelQuantity"
        :focusEnabled="focusEnabled"
        :transactionsNumber="transactionsNumber"
        :maxNumberOfOtokens="maxNumberOfOtokens"
        :oToken="selectedPotion.oToken"
        :underlying="selectedPotion.underlying"
        :current-slippage="currentSlippage"
        :order-size="orderSize"
        :premium="premium"
        :premium-per-potion="premiumPerPotion"
        :stable-coin-collateral="stableCoinCollateral"
        :gasUnits="gasUnits"
        @slippage-selected="selectSlippage"
        @buy-and-close-modal="buyAndCloseModal"
        @close="toggleStatusBar"
        :disableBuy="
          selectedPotion.quantity >= 0.00000001 &&
          selectedPotion.quantity <= maxNumberOfOtokens &&
          typeof premium === 'number'
            ? false
            : true
        "
      />
    </transition>
  </div>
</template>

<script>
import PotionStatusBar from "@/components/blocks/PotionStatusBar.vue";
import MainHeader from "@/components/Header.vue";
import PotionsNav from "@/components/blocks/SecondLevelRouteNav.vue";
import CustomPotionCreation from "@/components/blocks/CustomPotionCreation.vue";
import MyPotionsHeader from "@/components/cards/MyPotionsHeader.vue";
import { mapGetters, mapActions } from "vuex";
import { CurrencyService } from "@/services/api/currency";
import { getGas } from "@/services/api/gas";
import { debounce as _debounce } from "lodash-es";

export default {
  components: {
    MainHeader,
    PotionsNav,
    PotionStatusBar,
    CustomPotionCreation,
    MyPotionsHeader,
  },
  data() {
    return {
      ethPrice: 0,
      gasInGwei: 0,
      focusEnabled: true,
      modelQuantity: "0.001",
      routes: [
        {
          name: "DiscoverPotions",
          label: "Discover Potions",
          alwaysVisible: true,
        },
        {
          name: "MyPotions",
          label: "My Potions",
          alwaysVisible: false,
        },
      ],
    };
  },
  async mounted() {
    await this.updateEthPrice();
    await this.updateGasPrice();
  },
  watch: {
    statusBarOpened: {
      handler: _debounce(async function () {
        if (this.statusBarOpened === true) {
          this.modelQuantity = "0.001";
          this.updateQuantity(this.modelQuantity);
          await this.updateEthPrice();
          await this.updateGasPrice();
          if (parseFloat(this.modelQuantity) > 0) {
            this.focusEnabled = false;
            await this.runRouter({
              orderSize: this.orderSize,
              gasInWei: this.gasInWei,
              ethPrice: this.ethPrice,
            });
            this.focusEnabled = true;
          }
        }
      }, 500),
    },
    modelQuantity: {
      handler: _debounce(async function () {
        this.updateQuantity(this.modelQuantity);
        await this.updateEthPrice();
        await this.updateGasPrice();
        this.focusEnabled = false;
        if (parseFloat(this.modelQuantity) > 0) {
          await this.runRouter({
            orderSize: this.orderSize,
            gasInWei: this.gasInWei,
            ethPrice: this.ethPrice,
          });
          this.focusEnabled = true;
        }
      }, 500),
    },
  },
  methods: {
    async updateEthPrice() {
      this.ethPrice = await CurrencyService.getEthToUsd();
    },
    async updateGasPrice() {
      this.gasInGwei = await getGas();
    },
    ...mapActions("potions/custom", [
      "selectStep",
      "resetCustomPotion",
      "createPotion",
    ]),

    ...mapActions("potions/existing", [
      "toggleStatusBar",
      "updateQuantity",
      "buyPotions",
      "runRouter",
      "openPurchaseModal",
    ]),
    ...mapActions("potions", ["selectSlippage"]),
    startPotionCreation() {
      this.resetCustomPotion();
      this.selectStep(1);
    },
    async buyAndCloseModal() {
      await this.buyPotions();
      this.toggleStatusBar();
    },
  },
  computed: {
    ...mapGetters("wallet", ["connectedToMetamask", "stableCoinCollateral"]),
    ...mapGetters("potions/custom", [
      "currentStep",
      "stepsEnabled",
      "suggestedPotions",
    ]),
    gasInWei() {
      return this.gasInGwei.ProposeGasPrice * 10e8;
    },
    ...mapGetters("potions/existing", [
      "orderSize",
      "premiumPerPotion",
      "premium",
      "statusBarOpened",
      "selectedPotion",
      "maxNumberOfOtokens",
      "transactionsNumber",
      "gasUnits",
    ]),
    ...mapGetters("potions", ["currentSlippage"]),
    ...mapGetters("potions/user", [
      "activePotions",
      "expiredPotions",
      "availablePayout",
    ]),

    routeName() {
      return this.$route.name;
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

.blurred {
  @apply bg-opacity-100;
}

@supports (backdrop-filter: blur(1px)) {
  .blurred {
    @apply bg-opacity-50;
    backdrop-filter: blur(20px);
  }
}
</style>
