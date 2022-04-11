<template>
  <Title
    class="
      inline-block
      bg-gradient-to-r
      from-secondary-600
      to-secondary-400
      text-transparent
      bg-clip-text
    "
    :size="size"
    :label="label"
  ></Title>
</template>

<script>
import Title from "@/components/ui/Title.vue";

export default {
  components: {
    Title,
  },
  props: {
    label: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: "default",
    },
  },
};
</script>
