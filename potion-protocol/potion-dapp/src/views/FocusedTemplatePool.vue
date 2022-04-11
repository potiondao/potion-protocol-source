<template>
  <div class="container py-8 mx-auto" v-if="subgraphData">
    <TemplatePoolHeader
      :assets="assetsFlat"
      :pnl="subgraphData.pnlPercentage"
      :cloned="subgraphData.numPools"
      :size="subgraphData.size"
      :currency="stableCoinCollateral"
      :creatorName="creatorName"
      :etherscanLink="etherscanLink"
    />
    <div class="grid grid-flow-row gap-5 mt-5 grid-cols-1 xl:grid-cols-4">
      <div class="grid order-2 grid-cols-1 gap-5 xl:order-1 xl:col-span-3">
        <PoolPerformanceCard
          :performance-data="chartData"
          :today-timestamp="blockEpoch"
          v-if="loadedSnapshots"
        />
        <BondingCurveCard
          :parameters="subgraphData.curve"
          :emerging-curves="emergingCurves"
        />
        <div
          class="row-auto"
          v-for="underlying in assetsFlat"
          :key="underlying.id"
        >
          <UnderlyingListItem
            :underlying="underlying.symbol"
            :strike="underlying.strike"
            :duration="underlying.duration"
            :currentPrice="getPrice(underlying.address)"
            :collateral="stableCoinCollateral"
            :address="underlying.address"
          />
        </div>
      </div>
      <div class="order-1 xl:order-2">
        <CloneTemplate @cloneTemplate="cloneTemplate" :gasUnits="gasUnits" />
      </div>
    </div>
  </div>
</template>

<script>
import PoolPerformanceCard from "@/components/cards/PoolPerformance.vue";
import UnderlyingListItem from "@/components/cards/UnderlyingListItem.vue";
import TemplatePoolHeader from "@/components/cards/TemplatePoolHeader.vue";
import CloneTemplate from "@/components/cards/CloneTemplateCard.vue";
import BondingCurveCard from "@/components/cards/BondingCurve.vue";

import { getEmergingBondingCurvesFromCriterias } from "@/services/router/worker.worker.ts";

import { createNewPool } from "../services/contracts/pools";
import { mapActions, mapGetters } from "vuex";
import { getUnderlyingsPriceMap } from "@/helpers";
import { estimateSavePool } from "@/services/contracts/pools";
import { getEtherscanLink, _lastUniqBy } from "@/helpers";
import { get as _get } from "lodash-es";
import { lookupAddress } from "@/services/ethers";

const getSnapshotData = (snapshot) => {
  const size = parseFloat(snapshot.size);
  const locked = parseFloat(snapshot.locked);
  const timestamp = parseInt(snapshot.timestamp);
  const actionAmount = parseFloat(snapshot.actionAmount);
  const actionType = parseInt(snapshot.actionType);
  const absPnL = parseFloat(snapshot.pnlTotal);
  const templatePnlPercentage = parseFloat(snapshot.templatePnlPercentage);
  const templateSize = parseFloat(snapshot.templateSize);
  const templateUtilization = parseFloat(snapshot.templateUtilization);
  return {
    size,
    locked,
    timestamp,
    actionAmount,
    actionType,
    absPnL,
    templatePnlPercentage,
    templateSize,
    templateUtilization,
  };
};

export default {
  components: {
    UnderlyingListItem,
    PoolPerformanceCard,
    TemplatePoolHeader,
    CloneTemplate,
    BondingCurveCard,
  },
  data() {
    return {
      creatorName: "",
      subgraphData: null,
      snapshots: [],
      underlyingsPriceMap: {},
      emergingCurves: [],
      gasUnits: "21000",
      loadedSnapshots: false,
    };
  },
  async mounted() {
    this.subgraphData = await this.getTemplate(
      `id: "${this.$route.params.hash}"`
    );

    this.$set(
      this,
      "underlyingsPriceMap",
      await getUnderlyingsPriceMap(this.assetsFlat)
    );
    this.getTemplateSnapshots();
    this.$nextTick(async () => {
      this.$set(
        this,
        "emergingCurves",
        _lastUniqBy(
          await getEmergingBondingCurvesFromCriterias(this.ICriteria),
          "underlyingSymbol"
        )
      );
    });
    this.creatorName = await this.getENS();
    this.gasUnits = await this.estimateGas();
  },

  computed: {
    ...mapGetters(["blockEpoch"]),
    ...mapGetters("wallet", ["stableCoinCollateral"]),
    etherscanLink() {
      return getEtherscanLink(this.subgraphData.creator, "address");
    },
    criterias() {
      return _get(this, ["subgraphData", "criteriaSet", "criterias"], []);
    },

    ICriteria() {
      return this.criterias.map((x) => {
        return {
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
    assetsFlat() {
      return this.criterias.map((x) => {
        return {
          id: x.criteria.id,
          address: x.criteria.underlyingAsset.address,
          decimals: x.criteria.underlyingAsset.decimals,
          name: x.criteria.underlyingAsset.name,
          symbol: x.criteria.underlyingAsset.symbol,
          isPut: x.criteria.isPut,
          duration: x.criteria.maxDurationInDays,
          strike: x.criteria.maxStrikePercent,
        };
      });
    },
    chartData() {
      return this.snapshots.map((snapshot) => {
        const {
          actionType,
          timestamp,
          templatePnlPercentage,
          templateSize,
          templateUtilization,
        } = getSnapshotData(snapshot);
        const templateUtilPercent = 100 * templateUtilization;
        return {
          actionType,
          liquidity: templateSize,
          utilization: templateUtilPercent,
          timestamp,
          pnl: templatePnlPercentage,
        };
      });
    },
    statusBarData() {
      return {
        address: this.subgraphData.id,
        assets: this.subgraphData.assets,
        pnl: "0",
        cooked: this.subgraphData.numPools,
        size: { value: this.subgraphData.size, symbol: "" },
        curve: this.subgraphData.curve,
      };
    },
  },
  methods: {
    ...mapActions(["runWithLoader", "showToast"]),
    ...mapActions("pools", ["getTemplate", "getSnapshots", "approveDeposit"]),
    async getENS() {
      const ens = await lookupAddress(this.subgraphData.creator);
      if (ens.includes(".eth")) {
        return ens;
      } else {
        return `${this.subgraphData.creator.substr(0, 7)}...`;
      }
    },
    async estimateGas() {
      return await estimateSavePool(
        100,
        this.subgraphData.curve,
        this.assetsFlat.map((criteria) => {
          return {
            address: criteria.address,
            strike: criteria.strike,
            duration: criteria.duration,
          };
        }),
        2
      );
    },
    async getTemplateSnapshots() {
      const num = 1000;
      let snapshots = [];
      do {
        const ids = this.snapshots.map((s) => s.id);
        snapshots = await this.getSnapshots({
          templateAddress: this.subgraphData.id,
          num,
          alreadyLoadedIds: ids.length > 0 ? ids : [""],
        });
        snapshots.forEach((s) => this.snapshots.push(s));
      } while (num <= snapshots.length);
      this.loadedSnapshots = true;
    },
    async cloneTemplate(value) {
      const callback = async () => {
        await this.approveDeposit({ amount: parseFloat(value) });
        const transaction = await createNewPool(
          parseFloat(parseFloat(value).toFixed(6)),
          this.subgraphData.curve,
          this.assetsFlat.map((criteria) => {
            return {
              address: criteria.address,
              strike: criteria.strike,
              duration: criteria.duration,
            };
          })
        );
        this.showToast({
          title: "Creating your Pool",
          subtitle: "Check the status on etherscan",
          etherscanLink: getEtherscanLink(transaction.hash),
        });
        const receipt = await transaction.wait();
        if (receipt.status) {
          this.showToast({
            title: "Your new Pool is ready",
            subtitle: "You can see the transaction on etherscan",
            etherscanLink: getEtherscanLink(transaction.hash),
          });
          this.$router.push({ name: "MyPools" });
        }
      };
      const errorMessage = "Error cloning the template";
      await this.runWithLoader({ callback, errorMessage });
    },
    getPrice(name) {
      return (this.underlyingsPriceMap[name.replace(/ /g, "")] || 0).toString();
    },
  },
};
</script>
