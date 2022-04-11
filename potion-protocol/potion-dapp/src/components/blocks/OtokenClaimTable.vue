<template>
  <CardContainer
    :fullHeight="false"
    color="clean"
    class="border border-white border-opacity-10"
  >
    <div class="">
      <div
        class="
          flex flex-wrap
          radial-bg-glass
          font-poppins font-semibold
          text-xs
          rounded-t-2xl
        "
      >
        <div
          @click="activeTab = 'PoolExpiredOTokens'"
          class="
            cursor-pointer
            w-1/2
            py-4
            text-center
            border-b-2
            uppercase
            transition
          "
          :class="
            activeTab === 'PoolExpiredOTokens'
              ? 'border-primary-500'
              : 'border-white border-opacity-10'
          "
        >
          Expired Put Options
        </div>

        <div
          @click="activeTab = 'PoolActiveOTokens'"
          class="
            cursor-pointer
            w-1/2
            py-4
            border-b-2
            text-center
            uppercase
            transition
          "
          :class="
            activeTab === 'PoolActiveOTokens'
              ? 'border-primary-500'
              : 'border-white border-opacity-10'
          "
        >
          Active Put Options
        </div>
      </div>
      <div class="py-4 px-5 radial-bg-glass">
        <div class="font-poppins font-medium text-md">
          Underlying Pool Assets
        </div>

        <div class="flex space-x-3 mt-4">
          <Btn
            label="All"
            size="xs"
            class="!capitalize"
            v-if="uniqueUnderlyings.length > 1"
            @click="toggleAllUnderlyings()"
            :color="
              underlyingsAddressSelected.length === 0 ? 'filter' : 'primary'
            "
          />
          <Btn
            v-for="(underlying, index) in uniqueUnderlyings"
            :key="`underlying-filter-${index}`"
            :color="underlyingIsActive(underlying.address)"
            :label="underlying.symbol"
            size="xs"
            class="!capitalize"
            @click="toggleUnderlying(underlying.address)"
          />
        </div>
        <component
          class="mt-6"
          :is="activeTab"
          v-bind="dynamicProps"
          @claim-otoken="claimOtoken"
        />
      </div>
    </div>
  </CardContainer>
</template>
<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import PoolExpiredOTokens from "@/components/blocks/PoolExpiredOTokens.vue";
import { uniqBy as _uniqBy } from "lodash-es";
import Btn from "@/components/ui/Button.vue";
import PoolActiveOTokens from "@/components/blocks/PoolActiveOTokens.vue";

export default {
  components: {
    CardContainer,
    Btn,
    PoolExpiredOTokens,
    PoolActiveOTokens,
  },
  props: {
    underlyings: {
      type: Array,
      default: () => [],
    },
    priceMap: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      activeTab: "PoolExpiredOTokens",
      underlyingsAddressSelected: [],
    };
  },
  mounted() {
    this.selectAllUnderlyings();
  },
  computed: {
    uniqueUnderlyings() {
      return _uniqBy(this.underlyings, "address");
    },
    dynamicProps() {
      if (this.activeTab === "PoolActiveOTokens") {
        return { oTokens: this.otokens.active };
      } else {
        return { oTokens: this.otokens.expired };
      }
    },
    underlyingsSelected() {
      return this.uniqueUnderlyings.filter((und) =>
        this.underlyingsAddressSelected.includes(und.address)
      );
    },
    otokens() {
      const result = {
        active: [],
        expired: [],
      };
      this.underlyingsSelected.forEach((underlying) => {
        underlying.activeOTokens.forEach((otoken) =>
          result.active.push({
            ...otoken,
            symbol: underlying.symbol,
            currentPrice: this.priceMap[underlying.address],
          })
        );
        underlying.expiredOTokens.forEach((otoken) =>
          result.expired.push({ ...otoken, symbol: underlying.symbol })
        );
      });
      return result;
    },
  },
  methods: {
    underlyingIsActive(address) {
      if (this.underlyingsAddressSelected.includes(address)) {
        return "primary";
      }
      return "filter";
    },
    toggleAllUnderlyings() {
      if (this.underlyingsAddressSelected.length === 0) {
        this.selectAllUnderlyings();
      } else {
        this.deselectAllUnderlyings();
      }
    },
    selectAllUnderlyings() {
      this.underlyingsAddressSelected = this.uniqueUnderlyings.map(
        (x) => x.address
      );
    },
    deselectAllUnderlyings() {
      this.underlyingsAddressSelected = [];
    },
    toggleUnderlying(address) {
      if (!this.underlyingsAddressSelected.includes(address)) {
        this.underlyingsAddressSelected.push(address);
      } else {
        this.underlyingsAddressSelected.splice(
          this.underlyingsAddressSelected.indexOf(address),
          1
        );
      }
    },
    clipboard(text) {
      navigator.clipboard.writeText(text);
    },
    claimOtoken(oToken) {
      this.$emit("claim-otoken", oToken);
    },
  },
};
</script>
