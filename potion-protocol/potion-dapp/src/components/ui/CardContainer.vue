<template>
  <div
    class="flex"
    :class="[
      directionClass,
      colorClass,
      roundedClass,
      fullHeight ? 'h-full' : '',
    ]"
    @click="$emit('click')"
  >
    <slot />
  </div>
</template>

<script>
const directionToClass = {
  column: "flex-col",
  row: "flex-row",
};

const roundedToClass = {
  none: "",
  internal: "rounded-xl",
  default: "rounded-3xl",
};

const colorToClass = {
  glass: "radial-bg-glass blurred border-white border-opacity-10 border",
  neutral: "radial-bg-neutral",
  "no-bg": "border-white border-opacity-10 border",
  "secondary-radial": "radial-bg-secondary",
  "primary-radial-inactive": "radial-bg-primary-inactive",
  "primary-radial": "radial-bg-primary",
  clean: "",
};

export default {
  props: {
    direction: {
      type: String,
      default: "column",
      validator: (direction) =>
        Object.keys(directionToClass).includes(direction),
    },
    color: {
      type: String,
      default: "glass",
      validator: (value) => Object.keys(colorToClass).includes(value),
    },
    fullHeight: {
      type: Boolean,
      default: true,
    },
    rounded: {
      type: String,
      default: "default",
      validator: (value) => value in roundedToClass,
    },
  },
  computed: {
    directionClass() {
      return directionToClass[this.direction];
    },
    colorClass() {
      return colorToClass[this.color];
    },
    roundedClass() {
      return roundedToClass[this.rounded];
    },
  },
};
</script>

<style scoped>
.clean {
  @apply bg-transparent;
}
.radial-bg-neutral {
  @apply bg-white bg-opacity-5;
}

.radial-bg-glass {
  background: radial-gradient(
    77.23% 77.23% at 13.57% 18.81%,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0) 100%
  );
}

.radial-bg-secondary {
  @apply relative z-10 overflow-hidden hover:shadow-secondary transition-shadow duration-300;
  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-double transition-transform duration-300 -z-1 bg-gradient-to-br from-secondary-500 via-secondary-400 to-secondary-600;
  }
}

.radial-bg-secondary:hover::before {
  transform: translateX(-50%);
  transform: translateY(-50%);
}

.radial-bg-primary-inactive {
  @apply relative z-10 overflow-hidden border-white border-opacity-10 border;
  &::before {
    content: "";

    @apply absolute top-0 left-0 w-full h-full transition-opacity duration-300 opacity-0 -z-1 bg-gradient-to-br from-primary-500 via-primary-400 to-primary-600;
  }
}

.radial-bg-primary-inactive:hover::before {
  @apply opacity-100;
}

.radial-bg-primary {
  @apply relative z-10 overflow-hidden hover:shadow-primary transition-shadow duration-300;
  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-double transition-transform duration-300 -z-1 bg-gradient-to-br from-primary-500 via-primary-400 to-primary-600;
  }
}

.radial-bg-primary:hover::before {
  transform: translateX(-50%);
  transform: translateY(-50%);
}
</style>
