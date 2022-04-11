<template>
  <div class="border border-white border-opacity-10 rounded-3xl">
    <PutOptionsTable :headings="headings" :dataset="dataset" />
  </div>
</template>

<script>
import dayjs from "dayjs";
import PutOptionsTable from "@/components/ui/PutOptionsTable.vue";
import { getPnlColor, formatNumber } from "@/helpers";
import { mapGetters } from "vuex";

const formatPl = (value) => {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(2)}%`;
};
const formatFloat = (value) => {
  return parseFloat(value) >= 0 ? formatNumber(parseFloat(value)) : "0";
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
        "Collateral",
        "Projected P&L",
      ],
    };
  },
  computed: {
    ...mapGetters("wallet", ["stableCoinCollateral"]),
    dataset() {
      return this.oTokens.map((item) => {
        return [
          { value: item.symbol },
          this.formatDate(item.otoken.expiry),
          {
            value: ` ${formatFloat(item.premiumReceived)}${
              this.stableCoinCollateral
            } `,
          },
          {
            value: `${formatFloat(item.otoken.strikePrice)} ${
              this.stableCoinCollateral
            } `,
          },
          { value: formatFloat(item.collateral) },
          this.calcProfitAndLoss(
            parseFloat(item.premiumReceived),
            parseFloat(item.collateral),
            parseFloat(item.otoken.strikePrice),
            parseFloat(item.currentPrice)
          ),
        ];
      });
    },
  },
  methods: {
    formatDate(timestamp) {
      return { value: dayjs.unix(timestamp).format("D MMM YY") };
    },
    calcProfitAndLoss(premium, collateral, strikePrice, currentPrice) {
      const amountOfOtokens = collateral / strikePrice;
      const otokenValue = Math.max(strikePrice - currentPrice, 0);
      const pl = (premium - amountOfOtokens * otokenValue) / collateral;
      return {
        class: getPnlColor(pl),
        value: formatPl(pl * 100),
      };
    },
  },
};
</script>
