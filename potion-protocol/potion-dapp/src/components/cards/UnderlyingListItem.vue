<template>
  <CardContainer :fullHeight="false">
    <CardBody class="p-6">
      <div class="flex items-center">
        <div class="grid grid-flow-row grid-cols-2 md:grid-cols-4 gap-4 flex-1">
          <LabelToken
            size="md"
            token-size="md"
            title="Underlying"
            :name="underlying"
            :image="image"
            :address="address"
          />
          <LabelValue
            title="Current Price"
            :value="currentPrice"
            :symbol="collateral"
            alignment="center"
          />
          <LabelValue
            alignment="center"
            title="Strike"
            :value="strike"
            symbol="%"
          />
          <LabelValue
            alignment="right"
            title="Duration"
            :value="duration"
            symbol="dd"
          />
        </div>
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import LabelValue from "../blocks/LabelValue.vue";
import LabelToken from "@/components/blocks/LabelToken.vue";

export default {
  components: {
    CardContainer,
    CardBody,
    LabelValue,
    LabelToken,
  },
  props: {
    underlying: {
      type: String,
      required: true,
    },
    address: {
      type: String,
      default: "",
    },
    image: {
      type: String,
      default:
        "https://s.gravatar.com/avatar/da32ff79613d46d206a45e5a3018acf3?size=496&default=retro",
    },
    strike: {
      type: String,
      required: true,
    },
    duration: {
      type: String,
      required: true,
    },
    currentPrice: {
      type: String,
      required: true,
    },
    collateral: {
      type: String,
      required: true,
    },
    expiredOTokens: {
      type: Array,
      default: () => [],
    },
    activeOTokens: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      open: false,
    };
  },
  computed: {
    showToggle() {
      return this.activeOTokens.length > 0 || this.expiredOTokens.length > 0;
    },
  },
  methods: {
    clipboard(text) {
      navigator.clipboard.writeText(text);
    },
    claimOtoken(oToken) {
      this.$emit("claim-otoken", oToken);
    },
  },
};
</script>
