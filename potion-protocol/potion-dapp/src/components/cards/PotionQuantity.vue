<template>
  <CardContainer>
    <CardBody class="px-6 py-4">
      <div class="text-sm mb-7">Choose Quantity</div>
      <div class="flex justify-between w-full text-base mb-7">
        <span>Price per Potion</span>
        <span>{{ formattedPrice }}</span>
      </div>
      <div class="px-4 py-3 border border-white border-opacity-10 rounded-3xl">
        <span class="mb-3 text-base">Choose Quantity</span>
        <input
          type="number"
          ref="potionQuantity"
          @focus="inputFocus = true"
          @blur="inputFocus = false"
          :value="quantity"
          min="0"
          @input="updateQuantity($event.target.value)"
          class="
            block
            w-full
            p-1
            text-2xl
            bg-transparent
            border-none
            rounded-lg
            arrowless
            focus:ring-2 focus:ring-primary-500
          "
        />
      </div>
    </CardBody>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardBody from "../ui/CardBody.vue";

export default {
  components: {
    CardContainer,
    CardBody,
  },
  props: {
    price: {
      type: [Number, String],
      default: 0,
    },
    quantity: {
      type: String,
      default: "0",
    },
  },
  data() {
    return {
      inputFocus: false,
    };
  },
  async mounted() {
    this.setInputFocus();
  },
  computed: {
    formattedPrice() {
      if (typeof this.price === "number") {
        return new Intl.NumberFormat(navigator.language, {
          style: "currency",
          currency: "USD",
        }).format(this.price.toString());
      }
      return "Select a quantity";
    },
  },
  methods: {
    setInputFocus() {
      this.$refs.potionQuantity.focus();
    },
    updateQuantity(quantity) {
      this.$emit("input", quantity);
    },
  },
};
</script>

<style scoped>
.arrowless::-webkit-outer-spin-button,
.arrowless::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
  -moz-appearance: textfield;
}
</style>
