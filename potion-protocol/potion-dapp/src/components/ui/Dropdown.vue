<template>
  <div class="relative">
    <div
      class="
        inline-flex
        items-center
        px-4
        p-1.5
        bg-deep-black-700
        rounded-full
        cursor-pointer
        hover:bg-gradient-to-r hover:from-primary-500 hover:to-primary-400
      "
      @click="toggle"
      v-click-outside="close"
    >
      <div class="pr-3 text-xs">{{ title }}</div>
      <CaretUp class="h-3" v-if="open"></CaretUp>
      <CaretDown class="h-3" v-else></CaretDown>
    </div>
    <div
      class="
        absolute
        w-full
        top-full
        left-0
        flex flex-col
        bg-deep-black-800
        z-50
        mt-1
        rounded-lg
        overflow-hidden
      "
      v-if="open"
    >
      <span
        class="
          modal-item
          flex
          text-xs
          py-1
          px-4
          text-white
          cursor-pointer
          hover:bg-primary-500
          bg-opacity-10
        "
        :class="{
          'text-opacity-30':
            hasStatus(item.name) && !itemsSelectedStatus[item.name],
        }"
        v-for="item in items"
        :key="item.name"
        @click="dropdownItemSelected(item.name)"
      >
        {{ item.label }}
      </span>
    </div>
  </div>
</template>

<script>
import CaretDown from "@/components/icons/CaretDown.vue";
import CaretUp from "@/components/icons/CaretUp.vue";
export default {
  components: { CaretDown, CaretUp },
  props: {
    title: {
      type: String,
      required: true,
    },
    items: {
      type: Array,
      default: () => [],
    },
    itemsSelectedStatus: {
      type: Object,
      default: () => {
        return {};
      },
    },
  },
  data() {
    return {
      open: false,
    };
  },
  methods: {
    hasStatus(name) {
      return name in this.itemsSelectedStatus;
    },
    dropdownItemSelected(name) {
      this.$emit("dropdown-item-selected", name);
    },
    toggle() {
      this.open = !this.open;
    },
    close(event) {
      if (!event.target.classList.contains("modal-item")) {
        this.open = false;
      }
    },
  },
};
</script>
