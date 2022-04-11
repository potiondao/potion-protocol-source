<template>
  <CardContainer :fullHeight="false">
    <div class="flex w-full text-xs uppercase tracking-wide">
      <div
        class="w-1/2 py-4 text-center border-b-2 cursor-pointer"
        @click="tab = false"
        :class="
          tab === false
            ? 'border-primary-500'
            : 'border-dirty-white-300 border-opacity-20'
        "
      >
        Your Liquidity
      </div>
      <div
        class="w-1/2 py-4 text-center border-b-2 cursor-pointer"
        @click="tab = true"
        :class="
          tab === false
            ? 'border-white border-opacity-20'
            : 'border-primary-500'
        "
      >
        Add More
      </div>
    </div>

    <template v-if="tab === false">
      <CardBody class="flex-grow p-5">
        <div
          class="border box-border border-white border-opacity-10 rounded-2xl"
        >
          <div
            class="flex justify-between flex-wrap px-3 pt-5 pb-6 font-medium"
          >
            <span class="text-white">Total liquidity</span>
            <span class="text-white font-bitter"
              >{{ formattedProvided }} {{ stableCoinCollateral }}</span
            >
            <div class="w-full h-5"></div>
            <span class="text-secondary-500">Utilized Capital</span>
            <span class="text-secondary-500 font-bitter"
              >{{ formattedUtilized }} {{ stableCoinCollateral }}</span
            >
          </div>
          <WithdrawCapitalInput
            class=""
            title="Withdraw Capital"
            :value="withdraw"
            :unlocked-capital="unlocked"
            :currency="stableCoinCollateral"
            :error="
              parseFloat(withdraw) <= 0 ||
              parseFloat(withdraw) > parseFloat(unlocked)
            "
            :disable-external-border="true"
            :onlyTopBorder="true"
            @value-updated="updateWithdrawValue"
          />
        </div>
      </CardBody>
      <div class="p-5">
        <GasEstimationCard :gasUnits="withdrawEstimate" />
      </div>

      <CardFooter>
        <div class="flex justify-center w-full space-x-5">
          <Btn
            label="withdraw"
            color="secondary"
            size="sm"
            :disabled="disableWithdraw"
            @click="$emit('withdrawCollateral', withdraw)"
          >
            <template v-slot:pre-icon>
              <DownloadSimple class="mr-2 h-4" weight="bold"></DownloadSimple>
            </template>
          </Btn>
        </div>
      </CardFooter>
    </template>
    <template v-else>
      <CardBody class="flex-grow p-5">
        <BalanceInput
          title="Add more liquidity"
          :value="provide"
          @value-updated="updateProvidedValue"
          :error="disableAddMore"
        />
        <div
          class="
            flex flex-wrap
            justify-between
            pt-3
            mt-10
            border-t border-deep-black-600
          "
        >
          <GasEstimationCard :gasUnits="provideEstimate" />
        </div>
      </CardBody>
      <CardFooter>
        <div class="flex justify-center w-full">
          <Btn
            label="provide"
            color="secondary"
            size="sm"
            @click="$emit('addCollateral', provide)"
            :disabled="disableAddMore"
          >
            <template v-slot:pre-icon>
              <UploadSimple class="mr-2 h-4" weight="bold"></UploadSimple>
            </template>
          </Btn>
        </div>
      </CardFooter>
    </template>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import CardFooter from "../ui/CardFooter.vue";
import Btn from "../ui/Button.vue";
import BalanceInput from "@/components/blocks/BalanceInput.vue";
import WithdrawCapitalInput from "@/components/blocks/WithdrawCapitalInput.vue";
import GasEstimationCard from "@/components/cards/GasEstimationCard.vue";
import { mapGetters } from "vuex";
import DownloadSimple from "@/components/icons/DownloadSimple.vue";
import UploadSimple from "@/components/icons/UploadSimple.vue";
import {
  estimateDepositCollateral,
  estimateWithdrawCollateral,
} from "@/services/contracts/pools";
import { formatNumber } from "@/helpers/index";

export default {
  components: {
    CardContainer,
    CardBody,
    CardFooter,
    Btn,
    BalanceInput,
    WithdrawCapitalInput,
    GasEstimationCard,
    DownloadSimple,
    UploadSimple,
  },
  props: {
    provided: {
      type: Number,
      default: 0,
    },
    unlocked: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      tab: false,
      provide: "100",
      withdraw: "100",
      provideEstimate: "21700",
      withdrawEstimate: "21700",
    };
  },
  async mounted() {
    this.provideEstimate = await estimateDepositCollateral(
      parseFloat(this.$store.state.pools.focusedPool.poolId),
      parseFloat(this.provide)
    );
    this.withdrawEstimate = await estimateWithdrawCollateral(
      parseFloat(this.$store.state.pools.focusedPool.poolId),
      parseFloat(this.withdraw)
    );
  },
  computed: {
    ...mapGetters("wallet", [
      "stableCoinCollateral",
      "stableCoinCollateralBalance",
    ]),
    formattedProvided() {
      return formatNumber(this.provided);
    },
    formattedUtilized() {
      return formatNumber(this.provided - this.unlocked);
    },
    disableWithdraw() {
      return (
        this.unlocked === 0 ||
        parseFloat(this.withdraw) > this.unlocked ||
        parseFloat(this.withdraw) === 0
      );
    },
    disableAddMore() {
      return (
        parseFloat(this.provide) === 0 ||
        parseFloat(this.provide) > parseFloat(this.stableCoinCollateralBalance)
      );
    },
  },
  methods: {
    async updateProvidedValue(value) {
      this.provide = value;
      this.provideEstimate = await estimateDepositCollateral(
        parseFloat(this.$store.state.pools.focusedPool.poolId),
        parseFloat(value)
      );
    },
    async updateWithdrawValue(value) {
      this.withdraw = value;
      this.withdrawEstimate = await estimateWithdrawCollateral(
        parseFloat(this.$store.state.pools.focusedPool.poolId),
        parseFloat(value)
      );
    },
    changeTab() {
      this.tab = !this.tab;
    },
  },
};
</script>
