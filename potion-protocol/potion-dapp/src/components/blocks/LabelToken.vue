<template>
  <div class="grid grid-flow-row grid-cols-1 gap-3">
    <DataLabel :label="title" v-if="title !== ''" />
    <div class="flex items-center mb-2">
      <TokenIcon
        :address="address"
        :size="tokenSize"
        :image="image"
        :name="name"
        class="mr-1.5"
      />
      <Title :label="name" :size="size" />
    </div>
  </div>
</template>

<script>
import DataLabel from "@/components/ui/DataLabel.vue";
import Title from "@/components/ui/Title.vue";
import TokenIcon from "@/components/icons/TokenIcon.vue";
export default {
  components: {
    DataLabel,
    Title,
    TokenIcon,
  },
  props: {
    title: {
      type: String,
      default: "",
    },
    name: {
      type: String,
      required: true,
    },
    image: {
      type: String,
      default:
        "https://s.gravatar.com/avatar/da32ff79613d46d206a45e5a3018acf3?size=496&default=retro",
    },
    size: {
      type: String,
      default: "default",
    },
    tokenSize: {
      type: String,
      default: "lg",
    },
    address: {
      type: String,
      default: "",
    },
  },
};
</script>
