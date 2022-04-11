<template>
  <CardContainer class="relative p-6" :class="!border ? 'border-none' : ''">
    <div class="relative z-10">
      <GradientTitle size="xs" :label="label" class="uppercase"></GradientTitle>
      <Title :label="title" class="my-3 w-3/4 lg:w-full"></Title>
      <a
        class="uppercase text-sm text-primary-500 hover:text-primary-600"
        v-if="link"
        :href="link.url"
        :title="link.title"
        >{{ link.label }}</a
      >
      <Btn
        color="secondary"
        class="mt-4"
        size="sm"
        :label="buttonLabel"
        @click="buttonClicked"
      ></Btn>
    </div>
    <div
      class="
        absolute
        w-full
        h-full
        top-0
        left-0
        flex
        justify-end
        overflow-hidden
      "
    >
      <PictureSet
        class="h-full flex justify-end"
        :path-builder="getIconPath"
      ></PictureSet>
    </div>
  </CardContainer>
</template>

<script>
import Btn from "@/components/ui/Button.vue";
import CardContainer from "@/components/ui/CardContainer.vue";
import GradientTitle from "@/components/ui/GradientTitle.vue";
import PictureSet from "@/components/ui/PictureSet.vue";
import Title from "@/components/ui/Title.vue";

export default {
  components: {
    Btn,
    CardContainer,
    GradientTitle,
    PictureSet,
    Title,
  },
  props: {
    label: {
      type: String,
      default: "Gradient text",
    },
    title: {
      type: String,
      default: "Main title",
    },
    link: {
      type: Object,
      default: () => null,
    },
    buttonLabel: {
      type: String,
      default: "Button label",
    },
    getIconPath: {
      type: Function,
      required: true,
    },
    border: {
      type: Boolean,
      default: true,
    },
  },
  methods: {
    buttonClicked() {
      this.$emit("button-clicked");
    },
  },
};
</script>
