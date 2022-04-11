<template>
  <div class="container py-8 mx-auto" v-if="focusedPool">
    <PoolHeader
      :tokens="underlyingsFlat"
      :pnl="focusedPool.pnlPercentage"
      :utilization="utilizationPercentage"
      :currency="stableCoinCollateral"
      :pool-hash="$route.params.hash"
      :size="focusedPool.size"
      @open-edit="showEdit = true"
    />
    <div class="grid grid-flow-row grid-cols-1 xl:grid-cols-4 gap-5 mt-5">
      <div class="xl:col-span-3 grid grid-cols-1 gap-5 order-2 xl:order-1">
        <PoolPerformanceCard
          :fullHeight="false"
          :performance-data="chartData"
          :today-timestamp="blockEpoch"
          :key="`pool-performance-card-${$route.params.hash}`"
        />
        <BondingCurveCard
          :parameters="focusedPool.template.curve"
          :emerging-curves="emergingCurves"
        />
        <div
          class="row-auto"
          v-for="underlying in underlyingsFlat"
          :key="underlying.id"
        >
          <UnderlyingListItem
            :underlying="underlying.symbol"
            :address="underlying.address"
            :strike="underlying.strike"
            :duration="underlying.duration"
            :currentPrice="getPrice(underlying.address)"
            :expiredOTokens="underlying.expiredOTokens"
            :activeOTokens="underlying.activeOTokens"
            :collateral="stableCoinCollateral"
            @claim-otoken="reclaim"
          />
        </div>
        <OtokenClaimTable
          class="row-auto"
          :priceMap="underlyingsPriceMap"
          :underlyings="underlyingsFlat"
          @claim-otoken="reclaim"
        ></OtokenClaimTable>
      </div>
      <div class="order-1 xl:order-2">
        <LiquidityCard
          :provided="parseFloat(focusedPool.size)"
          :unlocked="unlockedValue"
          :oTokenAvailable="totalRefund"
          @withdrawCollateral="withdraw"
          @addCollateral="deposit"
        />
      </div>
    </div>

    <EditPoolModal
      :emergingCurves="emergingCurves"
      :underlyingsPriceMap="underlyingsPriceMap"
      v-if="showEdit"
      @close-edit="showEdit = false"
    />
  </div>
</template>

<script>
import LiquidityCard from "../components/cards/LiquidityCard.vue";
import PoolPerformanceCard from "../components/cards/PoolPerformance.vue";
import UnderlyingListItem from "../components/cards/UnderlyingListItem.vue";
import PoolHeader from "../components/cards/PoolHeader.vue";
import BondingCurveCard from "@/components/cards/BondingCurve.vue";
import EditPoolModal from "@/components/blocks/EditPoolModal.vue";
import { mapActions, mapGetters } from "vuex";
import { Pools } from "@/services/api/pools";
import OtokenClaimTable from "@/components/blocks/OtokenClaimTable.vue";
import { totalCredit } from "@/services/contracts/pools";
import { getEmergingBondingCurvesFromCriterias } from "@/services/router/worker.worker.ts";
import { getUnderlyingsPriceMap } from "@/helpers";
import { get as _get } from "lodash-es";

const getSnapshotData = (snapshot) => {
  const actionType = parseInt(snapshot.actionType);
  const size = parseFloat(snapshot.size);
  const timestamp = parseInt(snapshot.timestamp);
  const pnlPercentage = parseFloat(snapshot.pnlPercentage);
  const utilization = parseFloat(snapshot.utilization);
  const liquidityAtTrades = parseFloat(snapshot.liquidityAtTrades);
  return {
    actionType,
    size,
    timestamp,
    pnlPercentage,
    utilization,
    liquidityAtTrades,
  };
};

export default {
  components: {
    UnderlyingListItem,
    LiquidityCard,
    PoolPerformanceCard,
    PoolHeader,
    BondingCurveCard,
    EditPoolModal,
    OtokenClaimTable,
  },
  data() {
    return {
      reclaims: {},
      underlyingsPriceMap: {},
      emergingCurves: [],
      showEdit: false,
    };
  },
  async mounted() {
    await this.getBlockEpoch();
    const params = {
      id: this.$route.params.hash,
      walletAddress: this.$store.state.wallet.address,
    };
    await this.getPool(params);
    this.$set(this, "reclaims", await totalCredit(this.expiredOTokens));
    this.$set(
      this,
      "underlyingsPriceMap",
      await getUnderlyingsPriceMap(this.underlyingsFlat)
    );
    this.$nextTick(async () => {
      this.emergingCurves = await getEmergingBondingCurvesFromCriterias(
        this.ICriteria
      );
    });
  },
  computed: {
    ...mapGetters("pools", [
      "totalRefund",
      "focusedPool",
      "expiredOTokens",
      "activeOTokens",
    ]),
    ...mapGetters(["blockEpoch"]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
    criterias() {
      return _get(
        this,
        ["focusedPool", "template", "criteriaSet", "criterias"],
        []
      );
    },
    ICriteria() {
      return this.criterias.map((x) => {
        const expiredOTokens = this.expiredOTokens.filter(
          (item) =>
            item.lpRecord.otoken.underlyingAsset.address ===
            x.criteria.underlyingAsset.address
        );
        expiredOTokens.forEach((item) => {
          item.reclaimable = this.reclaims[item.id];
        });
        return {
          expiredOTokens,
          id: x.criteria.id,
          underlyingAsset: {
            id: x.criteria.underlyingAsset.address,
            decimals: x.criteria.underlyingAsset.decimals,
            name: x.criteria.underlyingAsset.name,
            symbol: x.criteria.underlyingAsset.symbol,
          },
          maxDurationInDays: x.criteria.maxDurationInDays,
          maxStrikePercent: x.criteria.maxStrikePercent,
        };
      });
    },
    underlyingsFlat() {
      return this.criterias.map((x) => {
        const expiredOTokens = this.expiredOTokens.filter(
          (item) =>
            item.lpRecord.otoken.underlyingAsset.address ===
            x.criteria.underlyingAsset.address
        );
        expiredOTokens.forEach((item) => {
          item.reclaimable = this.reclaims[item.id];
        });
        return {
          expiredOTokens,
          id: x.criteria.id,
          address: x.criteria.underlyingAsset.address,
          decimals: x.criteria.underlyingAsset.decimals,
          name: x.criteria.underlyingAsset.name,
          symbol: x.criteria.underlyingAsset.symbol,
          isPut: x.criteria.isPut,
          duration: x.criteria.maxDurationInDays,
          strike: x.criteria.maxStrikePercent,
          activeOTokens: this.activeOTokens.filter(
            (item) =>
              item.lpRecord.otoken.underlyingAsset.address ===
              x.criteria.underlyingAsset.address
          ),
        };
      });
    },
    utilizationPercentage() {
      if (this.focusedPool) {
        return (
          (100 * this.focusedPool.locked) /
          this.focusedPool.size
        ).toString();
      }
      return "0";
    },
    unlockedValue() {
      if (this.focusedPool) {
        return (
          parseFloat(this.focusedPool.size) -
          parseFloat(this.focusedPool.locked)
        );
      } else {
        return 0;
      }
    },
    chartData() {
      return this.focusedPool.snapshots.map((snapshot) => {
        const {
          actionType,
          size,
          timestamp,
          pnlPercentage,
          utilization,
          // liquidityAtTrades,
        } = getSnapshotData(snapshot);
        // We aren't currently using this field but we will need to use it in the future to calculate the PnL in different time ranges
        // console.log(liquidityAtTrades);
        const utilPercent = 100 * utilization;
        return {
          actionType,
          liquidity: size,
          utilization: utilPercent,
          timestamp,
          pnl: pnlPercentage,
        };
      });
    },
  },
  methods: {
    ...mapActions(["getBlockEpoch"]),
    ...mapActions("pools", [
      "getPool",
      "approveDeposit",
      "depositCollateral",
      "withdrawCollateral",
      "reclaimCollateralFromPoolRecord",
      "getMoreFocusedPoolSnapshots",
    ]),
    getPrice(address) {
      return (this.underlyingsPriceMap[address] || 0).toString();
    },
    async deposit(value) {
      const floatValue = parseFloat(value);
      await this.approveDeposit({ amount: floatValue });
      await this.depositCollateral({ depositAmount: floatValue });
      await this.getMoreFocusedPoolSnapshots();
    },
    async withdraw(value) {
      const floatValue = parseFloat(value);
      if (floatValue <= this.unlockedValue) {
        await this.withdrawCollateral({ withdrawAmount: floatValue });
        await this.getMoreFocusedPoolSnapshots();
      }
    },
    async reclaim(oToken) {
      const pools = await Pools.getLpPoolsForOtoken(
        oToken.lpRecord.lp,
        oToken.lpRecord.otoken.id
      );

      const mappedPools = pools.map((pool) => {
        return {
          otokenAddress: oToken.lpRecord.otoken.id,
          lp: pool.poolRecords[0].pool.lp,
          poolId: pool.poolRecords[0].pool.poolId,
        };
      });
      this.reclaimCollateralFromPoolRecord({ mappedPools });
      await this.getMoreFocusedPoolSnapshots();
    },
  },
};
</script>
