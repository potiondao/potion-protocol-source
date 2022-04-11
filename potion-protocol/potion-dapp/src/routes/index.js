import Vue from "vue";
import VueRouter from "vue-router";
import store from "../store";
const BasicLayout = () =>
  import(/* webpackChunkName: 'basic-layout' */ "../layouts/Basic");
const PoolsLayout = () =>
  import(/* webpackChunkName: 'pools-layout' */ "../layouts/Pools.vue");
const PotionsLayout = () =>
  import(/* webpackChunkName: 'potions-layout' */ "../layouts/Potions.vue");
const CustomPoolLayout = () =>
  import(
    /* webpackChunkName: 'custom-pool' */ "../layouts/CustomPoolCreation.vue"
  );
const CustomPoolOne = () =>
  import(
    /* webpackChunkName: 'custom-pool' */ "../views/custom-pool/StepOne.vue"
  );
const CustomPoolThree = () =>
  import(
    /* webpackChunkName: 'custom-pool' */ "../views/custom-pool/StepThree.vue"
  );
const CustomPoolTwo = () =>
  import(
    /* webpackChunkName: 'custom-pool' */ "../views/custom-pool/StepTwo.vue"
  );
const DiscoverPools = () =>
  import(/* webpackChunkName: 'discover-pools' */ "../views/DiscoverPools.vue");
const DiscoverPotions = () =>
  import(
    /* webpackChunkName: 'discover-potions' */ "../views/DiscoverPotions.vue"
  );
const EditPool = () =>
  import(
    /* webpackChunkName: 'edit-pool' */ "../views/custom-pool/EditPool.vue"
  );
const FocusedPool = () =>
  import(/* webpackChunkName: 'focused-pool' */ "../views/FocusedPool.vue");
const FocusedTemplatePool = () =>
  import(
    /* webpackChunkName: 'focused-template' */ "../views/FocusedTemplatePool.vue"
  );
const MyPools = () =>
  import(/* webpackChunkName: 'my-pools' */ "../views/MyPools.vue");
const MyPotions = () =>
  import(/* webpackChunkName: 'my-potions' */ "../views/MyPotions.vue");

Vue.use(VueRouter);

const poolCreationPages = ["PoolSetup", "CurveSettings", "PoolReview"];

const routes = [
  { path: "/", redirect: "/potions" },
  {
    path: "",
    name: "PoolsLayout",
    component: PoolsLayout,
    children: [
      {
        path: "/pools/my-pools",
        name: "MyPools",
        component: MyPools,
        meta: {
          private: true,
        },
        beforeEnter: (_, _1, next) => {
          if (store.getters["wallet/connectedToMetamask"]) {
            store.dispatch("pools/resetFocusedPool");
            store.dispatch("pools/getMyPools");
            next();
          } else {
            next({ name: "DiscoverPools" });
          }
        },
      },
      {
        path: "/pools",
        name: "DiscoverPools",
        component: DiscoverPools,
      },
    ],
  },
  {
    path: "",
    name: "PotionsLayout",
    component: PotionsLayout,
    children: [
      {
        path: "/potions",
        name: "DiscoverPotions",
        component: DiscoverPotions,
        beforeEnter: (_, _1, next) => {
          store.dispatch("potions/existing/getPotions");
          next();
        },
      },
      {
        path: "/potions/my-potions",
        name: "MyPotions",
        component: MyPotions,
        meta: {
          private: true,
        },
        beforeEnter: async (_, _1, next) => {
          if (store.getters["wallet/connectedToMetamask"]) {
            await store.dispatch(
              "potions/user/getUserPotions",
              store.getters["wallet/walletAddress"]
            );
            next();
          } else {
            next({ name: "DiscoverPotions" });
          }
        },
      },
    ],
  },
  {
    path: "",
    name: "BasicLayout",
    component: BasicLayout,
    children: [
      {
        path: "/pools/my-pools/pool/:hash",
        name: "Pool",
        component: FocusedPool,
        meta: {
          private: true,
        },
        beforeEnter: (_, _1, next) => {
          if (store.getters["wallet/connectedToMetamask"]) {
            next();
          } else {
            next({ name: "DiscoverPools" });
          }
        },
      },
      {
        path: "/pools/my-pools/pool/edit/:hash",
        name: "EditPool",
        component: EditPool,
        meta: {
          private: true,
        },
        beforeEnter: (_, _1, next) => {
          if (store.getters["wallet/connectedToMetamask"]) {
            next();
          } else {
            next({ name: "DiscoverPools" });
          }
        },
      },
      {
        path: "/pools/template/:hash",
        name: "PoolTemplate",
        component: FocusedTemplatePool,
      },
    ],
  },
  {
    path: "/pools/custom-pool",
    name: "CustomPoolLayout",
    component: CustomPoolLayout,
    children: [
      {
        path: "pool-setup",
        name: "PoolSetup",
        component: CustomPoolOne,
        beforeEnter: async (_, from, next) => {
          await store.dispatch(
            "pools/resetCustomPool",
            poolCreationPages.includes(from.name)
          );
          next();
        },
      },
      {
        path: "curve-settings",
        name: "CurveSettings",
        component: CustomPoolTwo,
        beforeEnter: (_, from, next) => {
          if (
            store.getters["pools/selectedUnderlyings"].length > 0 &&
            poolCreationPages.includes(from.name)
          ) {
            next();
          } else {
            next({ name: "PoolSetup" });
          }
        },
      },
      {
        path: "pool-review",
        name: "PoolReview",
        component: CustomPoolThree,
        beforeEnter: (_, from, next) => {
          if (
            store.getters["pools/selectedUnderlyings"].length > 0 &&
            store.state.pools.customPool.curveSettings.curve.length > 0 &&
            poolCreationPages.includes(from.name)
          ) {
            next();
          } else {
            next({ name: "PoolSetup" });
          }
        },
      },
    ],
  },
];

const router = new VueRouter({
  base: process.env.BASE_URL,
  routes,
});

router.beforeEach(async (_, _2, next) => {
  try {
    if (window.ethereum) {
      await store.dispatch("wallet/checkProvider");
      if (store.getters["wallet/metamaskInstalled"]) {
        await store.dispatch("wallet/getAccounts");
        if (store.getters["wallet/connectedToMetamask"]) {
          store.dispatch("wallet/getCollateralSymbol");
          store.dispatch(
            "wallet/getCollateralBalance",
            store.getters["wallet/walletAddress"]
          );
          await store.dispatch("getBlockEpoch");
        }
      }
    } else {
      store.dispatch("wallet/providerMissingToast");
    }
  } finally {
    next();
  }
});

export default router;
