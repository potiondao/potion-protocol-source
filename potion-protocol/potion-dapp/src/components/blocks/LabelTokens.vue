<template>
  <div>
    <DataLabel class="mb-2.5" :size="labelSize" :label="title" />
    <StackedTokens :size="tokenSize" :tokens="tokens" />
  </div>
</template>

<script>
import DataLabel from "../ui/DataLabel.vue";
import StackedTokens from "./StackedTokens.vue";
export default {
  components: {
    DataLabel,
    StackedTokens,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    tokens: {
      type: Array,
      required: true,
    },
    tokenSize: {
      type: String,
      default: "md",
    },
    labelSize: {
      type: String,
      default: "lg",
    },
  },
};
</script>
