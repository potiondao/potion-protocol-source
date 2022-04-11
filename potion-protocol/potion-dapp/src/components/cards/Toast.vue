<template>
  <div class="flex py-3 pl-4 px-10 sm:w-[350px]">
    <PictureSet
      class="max-w-[70px] max-h-[70px] mr-1"
      :path-builder="getIconPath"
    />
    <div
      class="
        bg-white bg-opacity-10
        self-stretch
        w-[2px]
        mr-3
        justify-self-center
      "
    ></div>
    <div
      class="
        font-medium
        leading-none
        text-white
        self-stretch
        flex flex-col
        gap-2
        justify-around
        break-words
      "
    >
      <p class="">{{ title }}</p>
      <p class="text-[10px]">{{ subtitle }}</p>
      <a
        v-if="etherscanLink !== null"
        class="
          inline-flex
          items-center
          self-start
          bg-white bg-opacity-10
          font-normal
          text-xs
          uppercase
          py-0.5
          px-1
          rounded
          text-[8px]
        "
        target="_blank"
        :href="etherscanLink"
        >view on etherscan <ArrowSquareIn class="h-2 ml-1"
      /></a>
    </div>
    <button class="absolute outline-none focus:outline-none right-4 top-4">
      <CloseModal />
    </button>
  </div>
</template>

<script>
import ArrowSquareIn from "@/components/icons/ArrowSquareIn.vue";
import CloseModal from "@/components/icons/CloseModal.vue";
import PictureSet from "@/components/ui/PictureSet.vue";

export default {
  components: {
    ArrowSquareIn,
    CloseModal,
    PictureSet,
  },
  props: {
    title: {
      type: String,
      default: "",
    },
    subtitle: {
      type: String,
      default: "",
    },
    etherscanLink: {
      type: String,
      default: null,
    },
    icon: {
      type: String,
      default: "atom",
    },
  },
  methods: {
    getIconPath(extenstion) {
      return `/icons/${this.icon}.${extenstion}`;
    },
  },
};
</script>
