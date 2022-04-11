import ganacheAdresses from "potion-contracts/deploy/ganache.json";
import kovanAdresses from "potion-contracts/deploy/kovan.json";
import kovanDemoAdresses from "potion-contracts/deploy/kovan.demo.json";
import kovanIndependentAdresses from "potion-contracts/deploy/kovan.independent.json";

import kovanTokens from "@/assets/tokenlists/kovan.default.json";
import kovanDemoTokens from "@/assets/tokenlists/kovan.demo.default.json";

import mainnetTokens from "@/assets/tokenlists/mainnet.default.json";
import ganacheTokens from "@/assets/tokenlists/ganache.default.json";

const addresses = {
  ganache: ganacheAdresses,
  kovan: kovanAdresses,
  "kovan.demo": kovanDemoAdresses,
  "kovan.independent": kovanIndependentAdresses,
};

const tokens = {
  kovan: kovanTokens,
  "kovan.demo": kovanDemoTokens,
  mainnet: mainnetTokens,
  ganache: ganacheTokens,
};

const contractsAddresses =
  process.env.VUE_APP_ETH_NETWORK in addresses
    ? addresses[process.env.VUE_APP_ETH_NETWORK]
    : addresses["ganache"];

const tokenList =
  process.env.VUE_APP_ETH_NETWORK in tokens
    ? tokens[process.env.VUE_APP_ETH_NETWORK]
    : null;

export { contractsAddresses, tokenList };
