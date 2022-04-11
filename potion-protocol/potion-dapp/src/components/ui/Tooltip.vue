<template>
  <Question class="h-4 hover:cursor-help" :weight="iconWeight"></Question>
</template>

<script>
import { weightValidator } from "@/helpers/PhosphorIcons";
import Question from "@/components/icons/Question.vue";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/translucent.css";

export default {
  components: {
    Question,
  },
  props: {
    iconWeight: {
      type: String,
      default: "regular",
      validator: weightValidator,
    },
    message: {
      type: String,
      default: "Lorem Ipsum",
    },
  },
  mounted() {
    this.$nextTick(() => {
      tippy(this.$el, {
        allowHTML: true,
        content: this.message,
        theme: "translucent",
      });
    });
  },
};
</script>
