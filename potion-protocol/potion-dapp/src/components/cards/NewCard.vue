<template>
  <CardContainer color="secondary-radial" class="w-full relative min-h-[330px]">
    <div
      class="
        cursor-pointer
        absolute
        w-full
        h-full
        flex
        items-center
        justify-center
        z-10
      "
      @click="$emit('click')"
    >
      <Plus class="h-20" />
    </div>
    <div class="flex items-end justify-center w-full h-full">
      <div class="py-8 font-semibold uppercase">
        {{ label }}
      </div>
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from "@/components/ui/CardContainer.vue";
import Plus from "@/components/icons/Plus.vue";

export default {
  props: {
    label: {
      type: String,
      default: "",
    },
  },
  components: {
    CardContainer,
    Plus,
  },
};
</script>
