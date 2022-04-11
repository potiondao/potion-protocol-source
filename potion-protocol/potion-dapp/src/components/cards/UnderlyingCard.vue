<template>
  <CardContainer
    rounded="internal"
    class="items-center"
    @click="$emit('underlying-selected', address)"
    :color="color"
  >
    <TokenIcon
      size="lg"
      :name="name"
      :image="image"
      :address="address"
      class="mb-4"
    />
    <span class="text-sm leading-none">{{ symbol }}</span>
  </CardContainer>
</template>

<script>
import TokenIcon from "@/components/icons/TokenIcon.vue";
import CardContainer from "@/components/ui/CardContainer.vue";

export default {
  components: {
    CardContainer,
    TokenIcon,
  },
  props: {
    address: {
      type: String,
      required: true,
    },
    symbol: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    image: {
      type: String,
    },
    active: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    color() {
      return this.active ? "primary-radial" : "primary-radial-inactive";
    },
  },
};
</script>
