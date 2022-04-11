<template>
  <CardContainer
    class="relative discover-pool-category"
    :class="sizeClasses"
    :color="color"
  >
    <div class="w-full mb-6" v-if="showHeading">
      <GradientTitle
        class="uppercase mb-2.5"
        :label="title"
        size="xxs"
      ></GradientTitle>
      <Title :label="description" size="sm" />
    </div>
    <div class="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <slot name="cards"></slot>
    </div>
    <slot name="loadmore"></slot>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import GradientTitle from "@/components/ui/GradientTitle.vue";
import Title from "@/components/ui/Title.vue";

const sizeToClasses = {
  compact: "p-4",
  default: "px-4 md:px-8 py-6",
};

export default {
  props: {
    showHeading: {
      type: Boolean,
      default: true,
    },
    color: {
      type: String,
      default: "glass",
    },
    title: {
      type: String,
      default: "",
    },
    description: {
      type: String,
      default: "",
    },
    size: {
      type: String,
      default: "default",
      validator: (value) => value in sizeToClasses,
    },
  },
  components: {
    CardContainer,
    GradientTitle,
    Title,
  },
  computed: {
    sizeClasses() {
      return sizeToClasses[this.size];
    },
  },
};
</script>
