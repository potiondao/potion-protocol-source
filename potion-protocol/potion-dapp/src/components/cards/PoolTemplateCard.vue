<template>
  <CardContainer class="relative">
    <CardBody class="group">
      <div
        class="
          grid grid-flow-row grid-cols-1
          gap-6
          p-6
          transition-all
          group-hover:opacity-0
          rounded-3xl
        "
      >
        <div class="flex justify-between items-center">
          <Tag size="sm" :label="tagText" class="place-self-start" />
          <CreatorTag
            :etherscanLink="etherscanLink"
            :creatorName="creatorName"
          />
        </div>

        <div class="grid grid-flow-row grid-cols-2 gap-2">
          <LabelTokens labelSize="md" title="Assets" :tokens="tokensFlat" />
          <LabelValue
            size="md"
            title="Tot. Size"
            :value="size"
            :symbol="currency"
          />
        </div>

        <div class="grid grid-flow-row grid-cols-2 gap-2">
          <LabelValue size="md" title="Cloned" :value="cloned" symbol="Times" />
          <LabelValue
            size="md"
            title="Pnl"
            :value="pnl"
            symbol="%"
            :valueColor="pnlColor"
          />
        </div>
      </div>
      <div
        class="
          absolute
          inset-0
          w-full
          h-full
          overflow-hidden
          transition-all
          opacity-0
          rounded-3xl
          group-hover:opacity-100
          bg-primary-radial
        "
      >
        <div
          class="
            absolute
            inset-0
            flex flex-col
            justify-between
            w-full
            h-full
            p-6
            rounded-3xl
          "
        >
          <div class="flex justify-between items-center">
            <Tag size="sm" :label="tagText" class="place-self-start" />
            <CreatorTag
              :etherscanLink="etherscanLink"
              :creatorName="creatorName"
            />
          </div>
          <div class="text-dirty-white-300 font-medium text-center">
            By providing liquidity you’re creating your pool cloning this
            template.
          </div>
          <router-link
            class="flex w-full justify-center"
            :to="{
              name: 'PoolTemplate',
              params: { hash: templateId },
            }"
          >
            <Btn
              class="self-center"
              size="sm"
              label="view pool recipe"
              color="white"
            />
          </router-link>
        </div>
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import LabelTokens from "@/components/blocks/LabelTokens.vue";
import Tag from "@/components/ui/Tag.vue";
import Btn from "@/components/ui/Button.vue";
import { mapActions } from "vuex";
import { getPnlColor } from "@/helpers";
import { lookupAddress } from "@/services/ethers";
import { getEtherscanLink } from "@/helpers";
import CreatorTag from "@/components/ui/CreatorTag.vue";

export default {
  props: {
    templateId: {
      type: String,
      required: true,
    },
    cloned: {
      type: String,
      default: "",
    },
    size: {
      type: String,
      default: "",
    },
    currency: {
      type: String,
      default: "",
    },
    pnl: {
      type: String,
      default: "",
    },
    curve: {
      type: Object,
      default: () => {
        return { a: "2.5", b: "2.5", c: "2.5", d: "2.5", max: "1" };
      },
    },
    creator: {
      type: String,
      default: "",
    },
    criteriaSet: {
      type: Array,
      required: true,
    },
  },
  components: {
    CardContainer,
    CardBody,
    LabelTokens,
    LabelValue,
    Btn,
    Tag,
    CreatorTag,
  },
  data() {
    return {
      creatorName: "",
    };
  },
  async mounted() {
    this.creatorName = await this.getENS();
  },
  computed: {
    etherscanLink() {
      return getEtherscanLink(this.creator, "address");
    },
    pnlColor() {
      return getPnlColor(parseFloat(this.pnl));
    },
    tokensFlat() {
      return this.criteriaSet.map((x) => {
        return {
          address: x.criteria.underlyingAsset.address,
          decimals: x.criteria.underlyingAsset.decimals,
          name: x.criteria.underlyingAsset.name,
          symbol: x.criteria.underlyingAsset.symbol,
          strike: x.criteria.maxStrikePercent,
          duration: x.criteria.maxDurationInDays,
        };
      });
    },
    tagText() {
      let text = "";
      this.tokensFlat.forEach((x, index) => {
        if (index > 0) {
          text += `+${x.symbol}`;
        } else {
          text += `${x.symbol}`;
        }
      });
      return text;
    },
  },
  methods: {
    ...mapActions("pools", ["selectTemplate"]),
    async getENS() {
      const ens = await lookupAddress(this.creator);
      if (ens.includes(".eth")) {
        return ens;
      } else {
        return `${this.creator.substr(0, 7)}...`;
      }
    },
    openModal() {
      this.selectTemplate({
        address: this.templateId,
        assets: this.tokensFlat,
        pnl: this.pnl,
        cooked: this.cooked,
        size: this.size,
        curve: this.curve,
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
