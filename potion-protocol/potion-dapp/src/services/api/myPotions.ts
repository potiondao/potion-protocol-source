import { UserPotions, IPotions } from "@/types";

import ApiService from "../api.service";
import dayjs from "dayjs";

const baseUrl = process.env.VUE_APP_POTION_SUBGRAPH_URL;
const resource = "";

const coingeckoMappings = {
  UNI: "uniswap",
  ETH: "ethereum",
  LINK: "chainlink",
  PTNETH: "ethereum",
  PTNLINK: "chainlink",
  PTNUNI: "uniswap",
};
const buyerFragment = `fragment buyerDataFragment on BuyerRecord
{
  id
  numberOfOTokens
  premium
  expiry
  otoken {
    id
    decimals
    strikePrice
    expiry
    underlyingAsset {
      id
      address
      name
      symbol
    }
  }
}`;
const MyPotions = {
  getExpiredPotions: async (
    buyerAddress: string,
    expiry = dayjs().unix(),
    first = 6,
    alreadyLoadedIds = [""]
  ): Promise<IPotions[]> => {
    const graphqlQuery = ` ${buyerFragment}
    query loadPotions($buyerAddress: String!, $first: Int!, $expiry: BigDecimal!, $alreadyLoadedIds: [ID]!) {
      buyerRecords(orderBy: expiry, orderDirection: desc, first: $first, where: {buyer: $buyerAddress, expiry_lt: $expiry, id_not_in: $alreadyLoadedIds}) {
        ...buyerDataFragment
      }
    }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { buyerAddress, first, expiry, alreadyLoadedIds }
      );

      const potions = response.data.data.buyerRecords as IPotions[];
      return potions;
    } catch (error) {
      throw new Error(error);
    }
  },
  getActivePotions: async (
    buyerAddress: string,
    expiry = dayjs().unix(),
    first = 6,
    alreadyLoadedIds = [""]
  ): Promise<IPotions[]> => {
    const graphqlQuery = ` ${buyerFragment}
    query loadPotions($buyerAddress: String!, $first: Int!, $expiry: BigDecimal!, $alreadyLoadedIds: [ID]!) {
      buyerRecords(orderBy: expiry, orderDirection: asc, first: $first, where: {buyer: $buyerAddress, expiry_gt: $expiry, id_not_in: $alreadyLoadedIds}) {
        ...buyerDataFragment
      }
    }
    `;

    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { buyerAddress, first, expiry, alreadyLoadedIds }
      );

      const potions = response.data.data.buyerRecords as IPotions[];
      return potions;
    } catch (error) {
      throw new Error(error);
    }
  },
  getUserPotions: async (
    buyerAddress: string,
    expiry = dayjs().unix(),
    first = 6
  ): Promise<UserPotions> => {
    const graphqlQuery = ` ${buyerFragment}
    query userPotions($buyerAddress: String!, $first: Int!, $expiry: BigDecimal!) {
      activePotions: buyerRecords(orderBy: expiry, orderDirection: asc, first: $first, where: {buyer: $buyerAddress, expiry_gt: $expiry}) {
        ...buyerDataFragment
      },
      expiredPotions: buyerRecords(orderBy: expiry, orderDirection: desc, first: $first, where: {buyer: $buyerAddress, expiry_lt: $expiry}) {
        ...buyerDataFragment
      }
    }
    `;

    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { buyerAddress, first, expiry }
      );

      const potions = response.data.data as UserPotions;
      return potions;
    } catch (error) {
      throw new Error(error);
    }
  },
  getPriceInUSDOnDate: async (
    symbol: string,
    epoch: string
  ): Promise<string> => {
    try {
      const geckoId = coingeckoMappings[symbol];
      const date = dayjs.unix(parseInt(epoch)).format("DD-MM-YYYY");
      // date is in format dd-mm-yyyy
      // gekoId comes from: https://api.coingecko.com/api/v3/coins/list
      const resource = `https://api.coingecko.com/api/v3/coins/${geckoId}/history?date=${date}`;

      const response = await ApiService.get(resource);

      // Here we check if the date is not returned by the api (implying it does not exist)
      // or the date is in the future.
      if ("market_data" in response.data) {
        const priceInUSD = response.data.market_data.current_price.usd;
        return priceInUSD.toString();
      } else {
        const p = "100";
        return p;
      }
    } catch (error) {
      throw new Error(error);
    }
  },
};

export { MyPotions };
