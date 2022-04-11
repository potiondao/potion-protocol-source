<template>
  <a
    :href="etherscanLink"
    target="_blank"
    class="
      inline-block
      focus:outline-none
      font-poppins font-semibold
      bg-white bg-opacity-10
      rounded-full
      uppercase
      leading-none
      text-xs
      px-2
      pt-1.5
      pb-1
    "
  >
    <span class="flex gap-1">
      <UserIcon />
      <span>
        {{ creatorName }}
      </span></span
    >
  </a>
</template>
<script>
import UserIcon from "@/components/icons/UserIcon.vue";

export default {
  props: {
    etherscanLink: {
      type: String,
      default: "",
    },
    creatorName: {
      type: String,
      default: "",
    },
  },
  components: {
    UserIcon,
  },
};
</script>
