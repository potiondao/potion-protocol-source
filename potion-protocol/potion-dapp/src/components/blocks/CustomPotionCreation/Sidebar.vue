<template>
  <div class="grid lg:grid-cols-4 xl:grid-cols-1 gap-y-2 gap-x-8 leading-none">
    <button
      @click="changeStep(index + 1)"
      v-for="(item, index) in nav"
      :key="`pot-sidebar-item${index}`"
      class="
        relative
        flex
        items-center
        px-4
        py-2
        transition
        duration-200
        border border-white
        outline-none
        cursor-pointer
        focus:outline-none
        disabled:cursor-not-allowed
        border-box
        rounded-xl
        border-opacity-10
        hover:border-opacity-0
        group
        disabled:opacity-60
        hover:!opacity-100
        text-xs
        xl:text-sm
      "
      :class="{
        'bg-radial-glass bg-opacity-10': dataIsSet[index],
      }"
      :disabled="!stepsEnabled[index]"
    >
      <div
        class="
          absolute
          inset-0
          w-full
          h-full
          transition
          duration-200
          transform
          opacity-0
          bg-gradient-to-br
          from-primary-500
          to-primary-400
          rounded-xl
        "
        :class="{ 'opacity-100': potionNew.step === index + 1 }"
      ></div>
      <div
        class="
          absolute
          inset-0
          w-full
          h-full
          transition
          duration-200
          transform
          opacity-0
          radial-bg-glass
          border border-white border-opacity-10
          rounded-xl
          group-hover:opacity-100
        "
        v-if="potionNew.step !== index + 1"
      ></div>
      <div class="relative h-[24px] w-[24px] xl:h-[32px] xl:w-[32px] mr-3">
        <PictureSet
          class="absolute top-0 left-0 w-full h-full z-50"
          :class="potionNew.step === index + 1 ? 'opacity-0' : 'opacity-100'"
          :path-builder="getIconPath(item.icon, false)"
          :srcset-builder="getIconSrcset(item.icon, false)"
          sizes="(max-width: 1024px) 24px, 32px"
        />
        <PictureSet
          class="absolute top-0 left-0 w-full h-full z-50"
          :class="potionNew.step === index + 1 ? 'opacity-100' : 'opacity-0'"
          :path-builder="getIconPath(item.icon, true)"
          :srcset-builder="getIconSrcset(item.icon, true)"
        />
      </div>
      <div class="z-50 flex items-center justify-between flex-1">
        <span>{{ item.description }}</span>
        <div
          class="flex space-x-1 items-center align-middle"
          v-if="
            item.description === 'Asset' && potionNew.underlyingSelected.image
          "
        >
          <TokenIcon
            size="base"
            :name="potionNew.underlyingSelected.name"
            :image="potionNew.underlyingSelected.image"
            :address="potionNew.underlyingSelected.address"
          />
          <span class="mt-[1px]">{{
            potionNew.underlyingSelected.symbol
          }}</span>
        </div>

        <span class="text-xs" v-if="item.description === 'Strike Price'">{{
          priceSelected
        }}</span>
        <span class="text-xs" v-if="item.description === 'Duration'">{{
          daysSelected
        }}</span>
      </div>
    </button>
  </div>
</template>

<script>
import TokenIcon from "@/components/icons/TokenIcon.vue";
import PictureSet from "@/components/ui/PictureSet.vue";
import dayjs from "dayjs";
import { mapGetters } from "vuex";
import { formatNumber } from "@/helpers";

export default {
  props: {
    stepsEnabled: {
      type: Array,
      default: () => [],
    },
    stableCoinCollateral: {
      type: String,
      default: "",
    },
  },
  components: {
    TokenIcon,
    PictureSet,
  },
  data() {
    return {
      nav: [
        {
          icon: "asset",
          description: "Asset",
        },
        {
          icon: "strike",
          description: "Strike Price",
        },
        {
          icon: "duration",
          description: "Duration",
        },
        {
          icon: "review",
          description: "Review and Create",
        },
      ],
    };
  },
  computed: {
    ...mapGetters(["blockEpoch"]),
    potionNew() {
      return this.$store.state.potions.custom;
    },
    dataIsSet() {
      return [
        this.potionNew.underlyingSelected.name !== null,
        this.potionNew.strike.priceSelected !== null &&
          this.potionNew.strike.priceSelected !== "",
        this.potionNew.duration.daysSelected !== null &&
          this.potionNew.duration.daysSelected !== "",
      ];
    },
    priceSelected() {
      if (
        this.potionNew.strike.priceSelected &&
        this.potionNew.strike.priceSelected !== ""
      ) {
        return `${formatNumber(this.potionNew.strike.priceSelected)} ${
          this.stableCoinCollateral
        }`;
      } else {
        return "";
      }
    },
    daysSelected() {
      if (
        this.potionNew.duration.daysSelected &&
        this.potionNew.duration.daysSelected !== ""
      ) {
        return dayjs
          .unix(this.blockEpoch)
          .add(this.potionNew.duration.daysSelected, "day")
          .format("ll");
      } else {
        return "";
      }
    },
  },
  methods: {
    getIconPath(icon, active) {
      const name = active ? `${icon}-active` : `${icon}-default`;
      return (format) => `/icons/${name}-32x32.${format}`;
    },
    getIconSrcset(icon, active) {
      const name = active ? `${icon}-active` : `${icon}-default`;
      return (format) =>
        `/icons/${name}-24x24.${format} 24w, /icons/${name}-32x32.${format} 32w`;
    },
    changeStep(step) {
      this.$emit("stepSelected", step);
    },
  },
};
</script>

<style scoped>
.radial-bg-glass {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(67, 60, 104, 0.3) 0%,
    rgba(67, 60, 104, 0.05) 100%
  );
}
</style>
