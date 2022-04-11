<template>
  <CardContainer :fullHeight="false">
    <CardBody class="px-6 py-4">
      <div class="text-sm">Choosen Assets</div>
      <div class="mt-5">
        <div class="flex justify-between w-full mb-3">
          <span class="w-1/3 text-sm text-left">Assets</span>
          <span class="w-1/3 text-sm text-left">Strike</span>
          <span class="w-1/3 text-sm text-left">Duration</span>
        </div>
        <div
          class="flex justify-start w-full mb-6 font-extrabold font-bl"
          v-for="(asset, index) in assets"
          :key="index"
        >
          <span class="flex items-center justify-start w-1/3 space-x-1 text-sm">
            <TokenIcon :name="asset.symbol" :address="asset.address" />
            <span>{{ asset.symbol }}</span>
          </span>

          <span class="w-1/3 text-left">{{ asset.strike }}%</span>
          <span class="w-1/3 text-left">{{ asset.duration }}dd</span>
        </div>
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";
import TokenIcon from "../icons/TokenIcon.vue";
export default {
  props: {
    assets: {
      type: Array,
      default: () => [],
    },
  },
  components: {
    CardContainer,
    CardBody,
    TokenIcon,
  },
};
</script>
