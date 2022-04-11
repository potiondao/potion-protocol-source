<template>
  <div class="overflow-x-auto">
    <table class="table-fixed w-full font-medium">
      <thead
        class="text-sm"
        :class="
          dataset.length > 0 ? 'border-b-2 border-white border-opacity-10' : ''
        "
      >
        <th
          class="
            font-medium
            py-3
            text-right
            first:pl-4
            px-2
            last:pr-4
            w-[120px]
            last:w-[150px]
          "
          v-for="(label, index) in headings"
          :key="`heading-${index}`"
        >
          {{ label }}
        </th>
      </thead>
      <tbody class="font-bitter font-bold text-md" v-if="dataset.length > 0">
        <tr v-for="(row, index) in dataset" :key="`row-${index}`">
          <td
            class="px-2 py-4 first:pl-4 last:pr-4 text-right"
            v-for="(cell, cellIndex) in row"
            :key="`cell-${index}-${cellIndex}`"
          >
            <Btn
              :color="cell.color"
              :label="cell.label"
              :disabled="!cell.claimable"
              :inline="true"
              size="sm"
              v-if="cell.button"
              @click="buttonPressed(index, cellIndex)"
            />
            <span :class="cell.class" v-else>{{ cell.value }}</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div
      v-if="dataset.length === 0"
      class="
        border-t-2 border-white border-opacity-10
        min-h-[100px]
        flex
        items-center
        justify-center
        w-full
        text-white text-opacity-20 text-xl
      "
    >
      <span>No options to show</span>
    </div>
  </div>
</template>

<script>
import Btn from "@/components/ui/Button.vue";

export default {
  components: {
    Btn,
  },
  props: {
    headings: {
      type: Array,
      default: () => [],
    },
    dataset: {
      type: Array,
      default: () => [[]],
    },
  },
  methods: {
    buttonPressed(index, cellIndex) {
      this.$emit("button-pressed", { index, cellIndex });
    },
  },
};
</script>
