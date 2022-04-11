<template>
  <CardContainer fullHeight>
    <CardBody class="grid grid-flow-row grid-cols-1 gap-4 px-6 py-4">
      <Tag
        class="justify-between"
        direction="horizzontal"
        :clickable="true"
        :address="address"
        @click="addTokenToMetamask('ERC20', address, oTokenName, 8)"
      />

      <LabelToken
        size="md"
        :name="asset.name"
        :image="asset.image"
        :address="underlyingAddress"
      />
      <div class="grid grid-flow-row grid-cols-2 gap-2">
        <LabelValue
          size="md"
          title="Strike Price"
          :value="strike"
          :symbol="currency"
        />
        <LabelValue
          size="md"
          title="Expiration"
          :value="expiration"
          value-type="timestamp"
        />
      </div>
      <div class="grid grid-flow-row grid-cols-2 gap-2">
        <LabelValue size="md" title="Quantity" :value="quantity" symbol="" />
        <LabelValue
          valueColor="text-secondary-500"
          size="md"
          :title="redeemed ? 'Withdrawn Payout' : 'Current Payout'"
          :value="payout"
          :symbol="currency"
        />
      </div>
    </CardBody>
    <CardFooter>
      <Btn
        size="sm"
        color="secondary"
        :label="buttonLabel"
        :disabled="!withdrawable"
        @click="redeemOToken(address, quantity)"
      />
    </CardFooter>
  </CardContainer>
</template>

<script>
import LabelValue from "../blocks/LabelValue.vue";
import LabelToken from "@/components/blocks/LabelToken.vue";
import CardBody from "../ui/CardBody.vue";
import CardContainer from "../ui/CardContainer.vue";
import CardFooter from "../ui/CardFooter.vue";
import Tag from "@/components/blocks/OptionAdressTag.vue";
import Btn from "../ui/Button.vue";
import { mapGetters } from "vuex";
import { watchAsset } from "@/services/metamask";
import dayjs from "dayjs";
export default {
  components: {
    CardContainer,
    CardBody,
    Tag,
    LabelToken,
    LabelValue,
    CardFooter,
    Btn,
  },
  props: {
    redeemed: {
      type: Boolean,
      default: false,
    },
    withdrawable: {
      type: Boolean,
      default: false,
    },
    address: {
      type: String,
      default: "",
    },
    asset: {
      type: Object,
      default: () => {},
    },
    strike: {
      type: String,
      default: "",
    },
    expiration: {
      type: String,
      default: "",
    },
    quantity: {
      type: String,
      default: "",
    },
    payout: {
      type: String,
      default: "",
    },
    underlyingAddress: {
      type: String,
      default: "",
    },
    currency: {
      type: String,
      default: "",
    },
  },
  computed: {
    ...mapGetters("wallet", ["walletAddress"]),
    oTokenName() {
      return `P${this.asset.name.substring(3)}${dayjs
        .unix(this.expiration)
        .format("DMMMYY")}`;
    },
    buttonLabel() {
      if (this.redeemed) {
        return "Already Withdrawn";
      } else if (this.withdrawable) {
        return "Withdraw";
      }
      return "Not Withdrawable";
    },
  },
  methods: {
    redeemOToken(address, quantity) {
      this.$emit("redeem", { address, quantity });
    },
    async addTokenToMetamask(type, address, symbol, decimal) {
      await watchAsset(type, address, symbol, decimal);
    },
  },
};
</script>

<style lang="scss" scoped></style>
