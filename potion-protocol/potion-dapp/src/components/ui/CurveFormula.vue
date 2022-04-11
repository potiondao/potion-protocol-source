<template>
  <CardContainer
    class="p-3 text-sm"
    color="neutral"
    rounded="internal"
    :fullHeight="false"
  >
    <span class="text-white inline-flex items-center"
      >Equation
      <Tooltip
        class="ml-half-char"
        message="a = Scale
            b = End Point
            c = Convexity
            d = Offset"
    /></span>
    <span class="text-deep-black-500 mt-2"
      >P = a ⋅ U ⋅ cosh(b ⋅ U<sup>c</sup>) +d</span
    >
  </CardContainer>
</template>

<script>
import Tooltip from "@/components/ui/Tooltip.vue";
import CardContainer from "@/components/ui/CardContainer.vue";

export default {
  components: {
    CardContainer,
    Tooltip,
  },
};
</script>
