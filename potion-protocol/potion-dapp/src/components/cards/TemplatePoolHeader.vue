<template>
  <div class="w-full">
    <div class="mb-4">
      <router-link :to="{ name: 'DiscoverPools' }">
        <Btn color="transparent" label="Back" size="sm">
          <template v-slot:pre-icon>
            <CaretLeft class="mr-1 h-3"></CaretLeft>
          </template>
        </Btn>
      </router-link>
    </div>
    <CardContainer>
      <CardBody class="p-6">
        <!-- <div class="w-full flex items-center gap-4">
          <span>Creator</span>
          <CreatorTag
            :etherscanLink="etherscanLink"
            :creatorName="creatorName"
          />
        </div> -->
        <div class="flex items-start justify-between w-full flex-wrap gap-3">
          <LabelTokens title="assets" :tokens="tokens" />
          <LabelValue title="tot. size" :value="size" :symbol="currency" />
          <LabelValue title="cloned" :value="cloned" symbol="Times" />
          <LabelValue title="pnl" :value="pnl" symbol="%" />
          <div class="">
            <div class="mb-2.5 text-base">Creator</div>
            <CreatorTag
              :etherscanLink="etherscanLink"
              :creatorName="creatorName"
            />
          </div>
        </div>
      </CardBody>
    </CardContainer>
  </div>
</template>

<script>
import LabelTokens from "@/components/blocks/LabelTokens.vue";
import LabelValue from "@/components/blocks/LabelValue.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import CardBody from "@/components/ui/CardBody.vue";
import Btn from "@/components/ui/Button.vue";
import CaretLeft from "@/components/icons/CaretLeft.vue";
import CreatorTag from "@/components/ui/CreatorTag.vue";

export default {
  components: {
    LabelTokens,
    LabelValue,
    CardContainer,
    CardBody,
    Btn,
    CaretLeft,
    CreatorTag,
  },
  props: {
    creatorName: {
      type: String,
      default: "",
    },
    etherscanLink: {
      type: String,
      default: "",
    },
    cloned: {
      type: String,
      default: "",
    },
    size: {
      type: String,
      default: "0",
    },
    currency: {
      type: String,
      default: "",
    },
    pnl: {
      type: String,
    },
    status: {
      type: String,
    },
    assets: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    tokens() {
      return this.assets.map((asset) => {
        return {
          name: asset.name,
          address: asset.address,
        };
      });
    },
  },
};
</script>
