<template>
  <component
    @click="$emit('click')"
    :type="type"
    :disabled="disabled"
    :is="componentTag"
    class="btn whitespace-nowrap"
    :class="[
      colorClass,
      sizeClass,
      weightClass,
      inline ? 'inline-flex' : 'flex',
    ]"
  >
    <slot name="pre-icon"></slot>
    <span class="leading-none">
      {{ label }}
    </span>
    <slot name="post-icon"></slot>
  </component>
</template>

<script>
const colorToClass = {
  filter: "btn-filter",
  primary: "btn-primary",
  "primary-o": "btn-primary-o",
  secondary: "btn-secondary",
  "secondary-o": "btn-secondary-o",
  accent: "btn-accent",
  "accent-o": "btn-accent-o",
  tertiary: "btn-tertiary",
  white: "btn-white",
  "white-o": "btn-white-o",
  warning: "bg-warning text-white ring-error",
  error: "bg-error text-white ring-warning",
  transparent: "btn-transparent",
};

const sizeToClass = {
  icon: "p-2",
  xs: "px-4 py-2 text-xs",
  sm: "px-4 py-3 text-xs tracking-widest",
  md: "px-6 py-4 text-sm tracking-wider ",
  lg: "px-8 py-5 text-lg tracking-wide ",
};

const weightToClass = {
  medium: "font-medium",
  bold: "font-bold",
};

const modeToTag = {
  button: "button",
  link: "a",
};

export default {
  props: {
    label: {
      type: String,
      required: true,
      default: "Button",
    },
    mode: {
      type: String,
      default: "button",
      validator: (value) => value in modeToTag,
    },
    size: {
      type: String,
      required: false,
      default: "md",
      validator: (value) => Object.keys(sizeToClass).includes(value),
    },
    weight: {
      type: String,
      default: "medium",
      validator: (value) => Object.keys(weightToClass).includes(value),
    },
    color: {
      type: String,
      default: "primary",
      validator: (value) => Object.keys(colorToClass).includes(value),
    },
    type: {
      type: String,
      default: "button",
      validator: function (value) {
        return ["submit", "button"].indexOf(value) !== -1;
      },
    },
    icon: {
      type: String,
      required: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    inline: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    sizeClass() {
      return sizeToClass[this.size];
    },
    colorClass() {
      return colorToClass[this.color];
    },
    weightClass() {
      return weightToClass[this.weight];
    },
    componentTag() {
      return modeToTag[this.mode];
    },
  },
};
</script>

<style scoped>
.btn {
  @apply justify-center items-center relative z-10 overflow-hidden font-poppins uppercase transition-shadow duration-300 rounded-full shadow-none  focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn:hover::before {
  transform: translateX(-50%);
}
.btn-filter {
  @apply text-dirty-white-300 bg-transparent ring-1 ring-white ring-opacity-10 transition;
  &:hover {
    @apply bg-white bg-opacity-10;
  }
}
.btn-primary {
  @apply text-dirty-white-300;
  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-full transition-transform duration-300 -z-1 bg-gradient-to-r from-primary-500 via-primary-400 to-primary-600;
  }

  &:hover {
    @apply shadow-primary;
  }
}

.btn-secondary {
  @apply text-dirty-white-300;

  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-full transition-transform duration-300 -z-1 bg-gradient-to-r from-secondary-500 via-secondary-400 to-secondary-600;
  }

  &:hover {
    @apply shadow-secondary;
  }
}

.btn-accent {
  @apply text-dirty-white-300;

  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-full transition-transform duration-300 -z-1 bg-gradient-to-r from-accent-500 via-accent-400 to-accent-600;
  }

  &:hover {
    @apply shadow-accent;
  }
}

.btn-tertiary {
  @apply text-dirty-white-300;

  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-full transition-transform duration-300 -z-1 bg-gradient-to-r from-tertiary-500 via-tertiary-400 to-tertiary-600;
  }

  &:hover {
    @apply shadow-tertiary;
  }
}
.btn-white {
  @apply text-deep-black-900;

  &::before {
    content: "";

    @apply absolute top-0 left-0 w-double h-full transition-transform duration-300 -z-1 bg-dirty-white-300;
  }

  &:hover {
    @apply shadow-deep-black-800;
  }
}
.btn-white-o {
  @apply ring-2 ring-dirty-white-300 transition-all text-dirty-white-300;

  &:hover {
    @apply shadow-primary ring-4;
  }
}
.btn-primary-o {
  @apply ring-2 ring-primary-500 transition-all text-dirty-white-300;

  &:hover {
    @apply shadow-primary ring-4;
  }
}

.btn-secondary-o {
  @apply ring-secondary-500 ring-2 transition-all text-dirty-white-300;

  &:hover {
    @apply shadow-secondary from-secondary-400 to-secondary-500 ring-4;
  }
}

.btn-accent-o {
  @apply ring-accent-500 ring-2 transition-all text-dirty-white-300;

  &:hover {
    @apply shadow-accent from-accent-400 to-accent-500 ring-4;
  }
}

.btn-transparent {
  @apply transition-all text-dirty-white-300;
  &:hover {
    @apply shadow-sm bg-dirty-white-300 bg-opacity-10;
  }
}
</style>
