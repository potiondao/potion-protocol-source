<template>
  <div class="border border-white border-opacity-10 rounded-3xl">
    <PutOptionsTable
      :headings="headings"
      :dataset="dataset"
      @button-pressed="buttonPressed"
    />
  </div>
</template>

<script>
import dayjs from "dayjs";
import PutOptionsTable from "@/components/ui/PutOptionsTable.vue";
import { getPnlColor, formatNumber } from "@/helpers";
import { mapGetters } from "vuex";

const formatFloat = (value) => {
  return parseFloat(value) >= 0 ? formatNumber(parseFloat(value)) : "0";
};

const formatPl = (value) => {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(2)}%`;
};

const formatDate = (timestamp) => {
  return { value: dayjs.unix(timestamp).format("D MMM YY") };
};

const calcProfitAndLoss = (premium, collateral, reclaimable) => {
  const pl = (premium + collateral - reclaimable) / collateral;
  return {
    class: getPnlColor(pl),
    value: formatPl(pl * 100),
  };
};

export default {
  props: {
    oTokens: {
      type: Array,
      default: () => [],
    },
  },
  components: {
    PutOptionsTable,
  },
  data() {
    return {
      headings: [
        "Asset",
        "Exp. Date",
        "Premium",
        "Strike Price",
        "Reclaimable",
        "P&L",
        "Action",
      ],
    };
  },
  computed: {
    ...mapGetters("wallet", ["stableCoinCollateral"]),

    dataset() {
      return this.oTokens.map((item) => {
        const reclaimableAmount =
          typeof item.reclaimable === "number" && item.reclaimable !== 0
            ? item.reclaimable
            : item.returned;
        const claimable = item.reclaimable > 0;
        return [
          { value: item.symbol },
          formatDate(item.otoken.expiry),
          {
            value: `${formatFloat(item.premiumReceived)} ${
              this.stableCoinCollateral
            } `,
          },
          {
            value: `${formatFloat(item.otoken.strikePrice)} ${
              this.stableCoinCollateral
            } `,
          },
          {
            value: `${formatFloat(reclaimableAmount)} ${
              this.stableCoinCollateral
            } `,
          },
          calcProfitAndLoss(
            parseFloat(item.premiumReceived),
            parseFloat(item.collateral),
            reclaimableAmount
          ),
          {
            button: true,
            claimable,
            label: claimable ? "Claim" : "Claimed",
            color: claimable ? "secondary-o" : "secondary",
          },
        ];
      });
    },
  },

  methods: {
    buttonPressed({ index, cellIndex }) {
      const row = this.dataset[index];
      if (row[cellIndex].claimable) {
        this.$emit("claim-otoken", this.oTokens[index]);
      }
    },
  },
};
</script>
