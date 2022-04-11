<template>
  <button
    class="
      flex
      items-center
      p-1
      rounded-md
      bg-white bg-opacity-10
      hover:bg-primary-500
      transition-colors
      text-xs text-white
      leading-none
      cursor-pointer
      outline-none
      focus:outline-none
    "
    @click="$emit('click')"
  >
    <Plus class="h-3" v-if="direction === 'increase'" />
    <Minus class="h-3" v-else />
  </button>
</template>

<script>
import Minus from "@/components/icons/Minus.vue";
import Plus from "@/components/icons/Plus.vue";
export default {
  components: {
    Plus,
    Minus,
  },
  props: {
    direction: {
      type: String,
      default: "increase",
    },
  },
};
</script>
