<template>
  <DiscoverHeader
    label="Protection power in your hands!"
    title="Create protective potions by selecting asset, strike and duration."
    button-label="Create Potion"
    :getIconPath="getIconPath"
    @button-clicked="startPotionCreation"
    :border="false"
  ></DiscoverHeader>
</template>

<script>
import DiscoverHeader from "@/components/blocks/DiscoverHeader.vue";

export default {
  components: {
    DiscoverHeader,
  },
  methods: {
    startPotionCreation() {
      this.$emit("start-potion-creation");
    },
    getIconPath(extenstion) {
      return `/icons/potion-big.${extenstion}`;
    },
  },
};
</script>
