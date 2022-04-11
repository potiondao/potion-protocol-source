<template>
  <div class="flex justify-center w-full">
    <div
      class="w-full border border-white lg:w-1/2 border-opacity-10 rounded-3xl"
    >
      <div class="flex justify-between w-full p-4 mb-6 text-sm">
        <div>Max Duration</div>
        <div>
          <p class="font-medium text-sm">
            {{ this.potionNew.duration.daysMax }} Days
          </p>
          <p class="text-xs">
            {{ this.durationDaysMaxDate }}
          </p>
        </div>
      </div>
      <div class="relative z-50 w-full">
        <Input
          tagLabel="DAYS"
          title="Your Potion expires in"
          footerDescription="Expiry Date:"
          :value="durationSelected"
          :error="!validDurationInDays"
          :footerValue="durationDaysSelectedDate"
          :focus="inputFocus"
          @input="setDurationSelected"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { debounce as _debounce } from "lodash-es";
import Input from "@/components/ui/InputWithFooter.vue";

export default {
  components: {
    Input,
  },
  data() {
    return {
      inputFocus: false,
      durationSelected: "",
      showChoices: false,
    };
  },
  async mounted() {
    this.durationSelected = "1";
    this.selectDuration(this.durationSelected);
    await this.getMaxDurationFromStrike({
      underlying: this.potionNew.underlyingSelected.address,
      strike: this.strikePriceRelativeSelected,
    });
    this.setInputFocus();
  },
  watch: {
    durationSelected: {
      handler: _debounce(async function () {
        this.selectDuration(this.durationSelected);
        if (this.validDurationInDays) {
          await this.getSimilarPotions("duration");
        }
      }, 300),
    },
  },
  methods: {
    ...mapActions("potions/custom", [
      "getMaxDurationFromStrike",
      "selectDuration",
      "getSimilarPotions",
    ]),
    setInputFocus() {
      this.inputFocus = !this.inputFocus;
    },
    setDurationSelected(value) {
      this.durationSelected = parseInt(value).toString();
    },
  },
  computed: {
    ...mapGetters("potions/custom", [
      "strikePriceRelativeSelected",
      "durationDaysMaxDate",
      "durationDaysSelectedDate",
      "validDurationInDays",
    ]),
    potionNew() {
      return this.$store.state.potions.custom;
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
.blurred {
  backdrop-filter: blur(50px);
}
::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}
::-webkit-scrollbar-thumb {
  /* background: linear-gradient(0deg, #e373ac 0%, #fa198b 100%); */
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
  border-radius: 15px;
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(0deg, #8e6efd 0%, #724cf9 100%);
}
::-webkit-scrollbar-track {
  /* background: #d1d1d1;
  border-radius: 15px;
  box-shadow: inset -9px 0px 15px #ffffff; */
  @apply bg-white bg-opacity-0 rounded-full;
  backdrop-filter: blur(30px);
}
</style>
