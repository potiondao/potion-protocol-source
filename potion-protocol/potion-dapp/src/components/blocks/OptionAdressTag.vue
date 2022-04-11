<template>
  <div class="flex" :class="directionClass">
    <Tag
      label="PUT OPTION"
      size="sm"
      :color="color"
      class="font-bold"
      :class="{ 'cursor-pointer': clickable }"
      @click="$emit('click')"
    />
    <a
      class="text-sm font-medium inline-flex items-center"
      target="_blank"
      :class="paddingClass"
      :href="etherscanLink"
    >
      <ArrowSquareIn class="h-4 mr-1" />
      {{ formattedAddress }}
    </a>
  </div>
</template>

<script>
import Tag from "@/components/ui/Tag.vue";
import ArrowSquareIn from "@/components/icons/ArrowSquareIn.vue";
import { getEtherscanLink } from "@/helpers";

const directionToClass = {
  vertical: "flex-col",
  horizzontal: "flex-col items-start md:flex-row md:items-center",
};

const directionToPaddingClass = {
  vertical: "py-2",
  horizzontal: "py-2 md:px-2",
};

export default {
  components: {
    Tag,
    ArrowSquareIn,
  },
  props: {
    clickable: {
      type: Boolean,
      default: false,
    },
    address: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      default: "glass",
    },
    direction: {
      type: String,
      default: "vertical",
      validator: (value) => value in directionToClass,
    },
  },
  computed: {
    etherscanLink() {
      return getEtherscanLink(this.address, "token");
    },
    formattedAddress() {
      return `${this.address.substr(0, 7)}...`;
    },
    directionClass() {
      return directionToClass[this.direction];
    },
    paddingClass() {
      return directionToPaddingClass[this.direction];
    },
  },
};
</script>
