<template>
  <DiscoverHeader
    label="Great power, Great responsability!"
    title="Create custom pool from scratch"
    buttonLabel="Create Pool"
    :link="{ url: '#', title: 'Learn More', label: 'Learn More' }"
    :getIconPath="getIconPath"
    @button-clicked="startPoolCreation"
  ></DiscoverHeader>
</template>

<script>
import DiscoverHeader from "@/components/blocks/DiscoverHeader.vue";

export default {
  components: {
    DiscoverHeader,
  },
  methods: {
    startPoolCreation() {
      this.$emit("start-pool-creation");
    },
    getIconPath(extenstion) {
      return `/icons/cauldron-big.${extenstion}`;
    },
  },
};
</script>
