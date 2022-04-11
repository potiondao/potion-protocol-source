<template>
  <CardContainer>
    <CardBody class="group relative">
      <div
        class="
          absolute
          top-0
          left-0
          w-full
          h-full
          opacity-0
          transition-opacity
          rounded-3xl
          group-hover:opacity-100
          bg-primary-radial
        "
      ></div>
      <div class="flex flex-col space-y-8 px-6 py-4 rounded-3xl relative">
        <Tag
          class="justify-between"
          direction="horizzontal"
          :address="oToken.address"
        />
        <LabelToken
          size="md"
          :name="underlying.symbol"
          :image="underlying.image"
          :address="underlying.address"
        />
        <div class="flex justify-between group-hover:opacity-0">
          <LabelValue
            size="md"
            title="Strike Price"
            :value="oToken.strikePrice"
            :symbol="currency"
          />
          <LabelValue
            size="md"
            title="Expiration"
            :value="oToken.expirationUnix"
            value-type="timestamp"
          />
        </div>
        <div
          class="
            absolute
            z-10
            bottom-4
            left-0
            w-full
            justify-center
            hidden
            group-hover:flex
          "
        >
          <Btn
            class="opacity-0 group-hover:opacity-100 transition-opacity"
            weight="bold"
            color="white"
            size="sm"
            label="BUY POTION"
            @click="potionSelected"
          />
        </div>
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import Tag from "@/components/blocks/OptionAdressTag.vue";
import LabelToken from "@/components/blocks/LabelToken.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import Btn from "@/components/ui/Button.vue";

export default {
  components: {
    CardContainer,
    CardBody,
    Tag,
    LabelToken,
    LabelValue,
    Btn,
  },
  props: {
    underlying: {
      type: Object,
      default: () => {
        return {
          name: "",
          symbol: "",
          address: "",
          image: "",
          price: "",
        };
      },
    },
    oToken: {
      type: Object,
      default: () => {
        return {
          address: "",
          strikePrice: "",
          expirationUnix: "",
          orderHistory: [],
        };
      },
    },
    currency: {
      type: String,
      default: "",
    },
  },
  methods: {
    potionSelected() {
      this.$emit("potion-selected", {
        underlying: {
          name: this.underlying.name,
          symbol: this.underlying.symbol,
          address: this.underlying.address,
          image: this.underlying.image,
          price: null,
        },
        oToken: {
          id: this.oToken.id,
          address: this.oToken.address,
          strikePrice: this.oToken.strikePrice,
          expirationUnix: this.oToken.expirationUnix,
          orderHistory: this.oToken.orderHistory,
        },
      });
    },
  },
};
</script>
<style scoped>
.bg-primary-radial {
  background: linear-gradient(113.69deg, #724cf9 23.72%, #8e6efd 81.45%);
}
</style>
