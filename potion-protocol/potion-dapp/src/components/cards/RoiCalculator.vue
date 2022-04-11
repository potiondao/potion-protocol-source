<template>
  <CardContainer :full-height="false">
    <CardBody class="p-6">
      <Title class="mb-6" label="ROI Calculator" />
      <div class="flex items-center mb-6 bg-white rounded-lg bg-opacity-10">
        <div
          class="
            text-center
            w-1/3
            h-full
            py-1.5
            text-xs
            rounded-lg
            bg-gradient-to-r
            from-primary-500
            to-primary-400
            text-dirty-white-300
          "
        >
          Current ROI
        </div>
        <div class="w-1/3 h-full py-1.5 text-center text-xs">Past Week</div>
        <div class="w-1/3 h-full py-1.5 text-center text-xs">Past Month</div>
      </div>
      <div class="w-full p-3 border border-white rounded-2xl border-opacity-10">
        <div class="w-full mb-4">Withdraw</div>
        <div class="flex items-center justify-between">
          <div class="w-full">
            <input
              class="
                block
                w-full
                px-0
                py-1
                text-2xl
                bg-transparent
                border-none
                rounded-lg
                focus:ring-2 focus:ring-primary-500
              "
              type="number"
              min="1"
              value="9999"
            />
          </div>

          <div
            class="
              flex
              items-center
              px-2
              py-1
              rounded-md
              bg-gradient-to-r
              from-primary-500
              to-primary-400
            "
          >
            <span
              class="
                block
                h-full
                mr-1
                text-sm
                font-semibold
                leading-none
                text-white
              "
              >CALCULATE</span
            >

            <svg
              width="7"
              height="12"
              viewBox="0 0 7 12"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              class="block h-full stroke-current text-dirty-white-300"
            >
              <path
                d="M1 11L6 6L1 1"
                stroke=""
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
        </div>
      </div>
    </CardBody>
    <CardFooter>
      <div
        class="grid w-full grid-cols-1 divide-y divide-white divide-opacity-20"
      >
        <div class="flex justify-between py-3">
          <div>Per Day</div>
          <div>$70</div>
        </div>
        <div class="flex justify-between py-3">
          <div>Per Week</div>
          <div>$490</div>
        </div>
        <div class="flex justify-between py-3">
          <div>Per Year</div>
          <div>$20,593</div>
        </div>
      </div>
    </CardFooter>
  </CardContainer>
</template>

<script>
import CardContainer from "../ui/CardContainer.vue";
import CardFooter from "../ui/CardFooter.vue";
import CardBody from "../ui/CardBody.vue";
import Title from "../ui/Title.vue";
export default {
  components: {
    CardContainer,
    CardFooter,
    CardBody,
    Title,
  },
};
</script>
