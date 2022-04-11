import "./assets/css/tailwind.css";
import "./assets/css/fonts.css";
import "./assets/css/theme.css";
import "./assets/css/chartTheme.css";
import "vue-toastification/dist/index.css";

import App from "./App.vue";
import Toast from "vue-toastification";
import Vue from "vue";
import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import router from "./routes";
import store from "./store";
import vClickOutside from "v-click-outside";

dayjs.extend(localizedFormat);

Vue.config.productionTip = false;

Vue.use(vClickOutside);
Vue.use(Toast);

new Vue({
  // @ts-ignore
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
