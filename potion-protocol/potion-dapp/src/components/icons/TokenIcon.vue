<template>
  <img
    class="object-cover rounded-full"
    :src="tokenImage"
    :alt="name"
    :class="sizeClasses"
  />
</template>

<script>
import { tokenList } from "@/services/contracts/index";
const sizeToClasses = {
  sm: "w-4 h-4",
  base: "w-5 h-5",
  md: "w-6 h-6",
  lg: "w-7 h-7",
  xl: "w-8 h-8",
  "2xl": "w-10 h-10",
};

export default {
  props: {
    address: {
      type: String,
      default: "",
    },
    symbol: {
      type: String,
      default: "",
    },
    image: {
      type: String,
      default:
        "https://s.gravatar.com/avatar/da32ff79613d46d206a45e5a3018acf3?size=496&default=retro",
    },
    name: {
      type: String,
      required: true,
    },
    size: {
      type: String,
      default: "md",
      validator: (value) => value in sizeToClasses,
    },
  },
  computed: {
    sizeClasses() {
      return sizeToClasses[this.size];
    },
    tokenImage() {
      if (tokenList) {
        const token = tokenList.tokens.filter(
          (token) => token.address.toLowerCase() === this.address
        );

        if (token.length > 0) {
          return token[0].logoURI;
        }
      }
      return this.image;
    },
  },
};
</script>
