<template>
  <picture>
    <source type="image/avif" :srcset="getSrcSet('avif')" />
    <source type="image/webp" :srcset="getSrcSet('webp')" />
    <source type="image/png" :srcset="getSrcSet('png')" />
    <img class="h-full" :src="pathBuilder('png')" />
  </picture>
</template>

<script>
export default {
  props: {
    srcsetBuilder: {
      type: Function,
      default: null,
    },
    pathBuilder: {
      type: Function,
      default: (value) => value,
    },
  },
  methods: {
    getSrcSet(format) {
      if (this.srcsetBuilder) {
        return this.srcsetBuilder(format);
      }
      return this.pathBuilder(format);
    },
  },
};
</script>
