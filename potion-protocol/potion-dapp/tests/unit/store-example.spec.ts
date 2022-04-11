import { shallowMount, createLocalVue } from "@vue/test-utils";
import Vuex, { GetterTree, Store } from "vuex";
import MyPotionsHeader from "@/components/cards/MyPotionsHeader.vue";

// Load vuex
const localVue = createLocalVue();
localVue.use(Vuex);

describe("MyPotionsHeader.vue", () => {
  let getters: GetterTree<any, any>;
  let store: Store<any>;

  beforeEach(() => {
    getters = {
      availablePayout: () => "10",
      activePotions: () => [],
      expiredPotions: () => [],
    };

    store = new Vuex.Store({
      modules: {
        myPotions: {
          getters,
          namespaced: true,
        },
      },
    });
  });
  it("pass myPotions.availablePayout to display-available-payout", () => {
    const wrapper = shallowMount(MyPotionsHeader, { store, localVue });
    const display = wrapper.find("[data-test='display-available-payout']");
    expect(display.attributes("value")).toBe("10");
  });
});
