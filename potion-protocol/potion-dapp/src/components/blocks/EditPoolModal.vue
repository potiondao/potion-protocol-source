<template>
  <div
    class="fixed z-30 w-screen h-screen top-0 left-0 pt-8 pb-16 basic blurred"
  >
    <div class="flex justify-between items-center container pb-8 px-6 mx-auto">
      <Title size="xs" class="uppercase tracking-wide" label="Edit Pool" />
      <Btn
        color="transparent"
        label=""
        size="icon"
        @click="$emit('close-edit')"
      >
        <template v-slot:pre-icon>
          <CloseIcon class="h-4" weight="bold" />
        </template>
      </Btn>
    </div>
    <EditPool
      class="overflow-y-scroll xl:overflow-y-hidden py-0 h-full"
      :initial-emerging-curves="emergingCurves"
      :underlyings-price-map="underlyingsPriceMap"
      :inModal="true"
      @close-edit="$emit('close-edit')"
    />
  </div>
</template>

<script>
import Title from "@/components/ui/Title.vue";
import Btn from "@/components/ui/Button.vue";
import CloseIcon from "@/components/icons/XIcon.vue";
import EditPool from "@/views/custom-pool/EditPool.vue";
import { disablePageScroll, enablePageScroll } from "scroll-lock";

export default {
  props: {
    emergingCurves: {
      type: Array,
      default: () => [],
    },
    underlyingsPriceMap: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
  components: {
    Title,
    Btn,
    EditPool,
    CloseIcon,
  },
  mounted() {
    this.$nextTick(disablePageScroll);
  },
  beforeDestroy() {
    enablePageScroll();
  },
};
</script>

<style scoped>
.basic {
  @apply bg-opacity-100;
  background: linear-gradient(
    113.69deg,
    rgba(var(--deep-blue-rgb), var(--tw-bg-opacity)) 23.72%,
    rgba(var(--deep-black-900-rgb), var(--tw-bg-opacity)) 81.45%
  );
}
.blurred {
  backdrop-filter: blur(20px);
}

@supports (backdrop-filter: blur(1px)) {
  .basic {
    @apply bg-opacity-80;
  }
}
</style>
