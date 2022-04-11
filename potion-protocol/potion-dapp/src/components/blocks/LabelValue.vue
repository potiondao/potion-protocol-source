<template>
  <div>
    <DataLabel
      class="mb-2.5"
      :label="title"
      :size="size"
      :alignment="alignment"
    />
    <Value
      :valueColor="valueColor"
      :size="size"
      :grow="grow"
      :value="value"
      :value-type="valueType"
      :symbol="symbol"
      :alignment="alignment"
    />
  </div>
</template>

<script>
import DataLabel from "../ui/DataLabel.vue";
import Value from "../ui/Value.vue";
export default {
  components: {
    DataLabel,
    Value,
  },
  props: {
    alignment: {
      type: String,
      default: "left",
    },
    valueColor: {
      type: String,
      default: "",
    },
    title: {
      type: String,
      required: true,
    },
    value: {
      type: String,
      required: true,
    },
    valueType: {
      type: String,
      default: "number",
    },
    size: {
      type: String,
    },
    symbol: {
      type: String,
      default: "",
    },
    grow: {
      type: String,
      required: false,
      validator: function (value) {
        return ["up", "down"].indexOf(value) !== -1;
      },
    },
  },
};
</script>
