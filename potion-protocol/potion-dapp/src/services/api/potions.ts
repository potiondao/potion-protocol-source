import ApiService from "../api.service";
import { uniqBy as _uniqBy, get as _get, flatten as _flatten } from "lodash-es";
import { ICriteria, IOToken, PopularOTokens } from "@/types";
import dayjs from "dayjs";

const baseUrl = process.env.VUE_APP_POTION_SUBGRAPH_URL;
const resource = "";

const getUnderlyingCondition = (addresses: string[]) =>
  addresses.length > 0
    ? `(where: { address_in: ${JSON.stringify(addresses)} })`
    : "";

const getCentralItems = <T>(array: T[], itemsToGet: number): T[] => {
  if (array.length > itemsToGet) {
    const center = Math.floor(array.length / 2);
    const offset = Math.floor(itemsToGet / 2);
    const rest = itemsToGet % 2;
    return array.slice(center - rest - offset, center + offset);
  }
  return array;
};

const otokenFragments = `fragment otokenCardData on OToken {
  id
  tokenAddress
  underlyingAsset {
    id
    symbol
    name
    address
  }
  expiry
  strikePrice
}`;

const filteringModeToQuery = {
  mostPurchased: `${otokenFragments}
    query oTokens($expiry: BigInt!, $addresses: [String]!, $alreadyLoadedIds: [ID], $limit: Int = 8) {
      otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, id_not_in: $alreadyLoadedIds, purchasesCount_gt: 1 }
        orderBy: purchasesCount
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
    }
  `,
  mostCollateralized: `${otokenFragments}
    query oTokens($expiry: BigInt!, $addresses: [String]!, $alreadyLoadedIds: [ID], $limit: Int = 8) {
      otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, id_not_in: $alreadyLoadedIds, purchasesCount_gt: 1 }
        orderBy: collateralized
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
    }
  `,
};

const Potions = {
  getMaxStrikeFromUnderlying: async (underlying: string) => {
    let maxStrike = 0;
    let criterias = [];
    const alreadyLoadedIds = [""];
    const graphqlQuery = `query getMaxStrikeFromUnderlying($underlying: String, $alreadyLoadedIds: [ID!]) {
      criterias(where: { underlyingAsset: $underlying, id_not_in: $alreadyLoadedIds }, orderBy: maxStrikePercent, orderDirection: desc) {
        id
        maxStrikePercent
        criteriaSets {
          criteriaSet {
            templates (where: { size_gt: 0, utilization_lt: 100 }) {
              id
            }
          }
        }
      }
    }`;
    try {
      do {
        const response = await ApiService.graphql(
          baseUrl + resource,
          graphqlQuery,
          { underlying, alreadyLoadedIds }
        );
        criterias = _get(response, ["data", "data", "criterias"], []);
        criterias.forEach((c) => alreadyLoadedIds.push(c.id));
        const firstCriteriaWithLiquidity = criterias.find((c) =>
          c.criteriaSets.some((cs: any) => cs.criteriaSet.templates.length > 0)
        );
        maxStrike = parseFloat(
          _get(firstCriteriaWithLiquidity, "maxStrikePercent", "0")
        );
      } while (maxStrike === 0 && criterias.length > 0);

      return maxStrike;
    } catch (error) {
      throw new Error(error);
    }
  },
  getMaxDurationFromStrike: async (
    underlying: string,
    strike: number | string
  ) => {
    let maxDuration = 0;
    let criterias = [];
    const alreadyLoadedIds = [""];
    const graphqlQuery = `query getMaxDurationFromStrike($underlying: String, $strike: String, $alreadyLoadedIds: [ID!]) {
      criterias(where: { underlyingAsset: $underlying, maxStrikePercent_gte: $strike, id_not_in: $alreadyLoadedIds }, orderBy: maxDurationInDays, orderDirection: desc) {
        id
        maxDurationInDays
        criteriaSets {
          criteriaSet {
            templates (where: { size_gt: 0, utilization_lt: 100 }) {
              id
            }
          }
        }
      }
    }`;
    try {
      do {
        const response = await ApiService.graphql(
          baseUrl + resource,
          graphqlQuery,
          { underlying, strike, alreadyLoadedIds }
        );
        criterias = _get(response, ["data", "data", "criterias"], []);
        criterias.forEach((c) => alreadyLoadedIds.push(c.id));
        const firstCriteriaWithLiquidity = criterias.find((c) =>
          c.criteriaSets.some((cs: any) => cs.criteriaSet.templates.length > 0)
        );
        maxDuration = parseFloat(
          _get(firstCriteriaWithLiquidity, "maxDurationInDays", "0")
        );
      } while (maxDuration === 0 && criterias.length > 0);
      return maxDuration;
    } catch (error) {
      throw new Error(error);
    }
  },
  getAvailableUniqueUnderlyingsFromPools: async () => {
    const graphqlQuery = `
    {
      pools(where: {size_gt: 0}) {
        size
        locked
        template {
          criteriaSet {
            criterias {
              criteria {
                underlyingAsset {
                  address
                  decimals
                  symbol
                  name
                }
              }
            }
          }
        }
      }
    }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );

      const filtered = response.data.data.pools.filter(
        (x) => x.locked < x.size
      );
      const flat = [];
      filtered.forEach((x) => {
        flat.push(
          x.template.criteriaSet.criterias.map((y) => {
            return {
              address: y.criteria.underlyingAsset.address,
              decimals: y.criteria.underlyingAsset.decimals,
              name: y.criteria.underlyingAsset.name,
              symbol: y.criteria.underlyingAsset.symbol,
            };
          })
        );
      });

      return _uniqBy(flat.flat(), (x) => {
        return x.address;
      });
    } catch (error) {
      throw new Error(error);
    }
  },
  getAvailableUniqueUnderlyings: async () => {
    const graphqlQuery = `
    {
      templates(where: {size_gt: 0, numPools_gt: 0}) {
        criteriaSet {
          criterias {
            criteria {
              underlyingAsset {
                name
                symbol
                address
                decimals
              }
            }
          }
        }
      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );
      let flat = [];
      response.data.data.templates.forEach((x) => {
        const criterias = _get(x, ["criteriaSet", "criterias"], []);
        flat.push(
          criterias.map((y) => {
            return {
              address: y.criteria.underlyingAsset.address,
              decimals: y.criteria.underlyingAsset.decimals,
              name: y.criteria.underlyingAsset.name,
              symbol: y.criteria.underlyingAsset.symbol,
            };
          })
        );
      });
      flat = flat.flat();
      flat = _uniqBy(flat, (x) => {
        return x.address;
      });
      return flat;
    } catch (error) {
      throw new Error(error);
    }
  },
  getCriteriasFromAsset: async (
    underlyingAddress: string
  ): Promise<ICriteria[]> => {
    underlyingAddress = underlyingAddress.toLowerCase();
    const graphqlQuery = `{
      criterias ( where: { underlyingAsset: "${underlyingAddress}" }) {
        isPut,
        maxStrikePercent,
        maxDurationInDays
        underlyingAsset {
          id
        },
        strikeAsset {
          id
        },

      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );
      const criterias: ICriteria[] = response.data.data
        .criterias as ICriteria[];
      return criterias;
    } catch (error) {
      throw new Error(error);
    }
  },

  getOTokens: async (
    currentEpochinSeconds: string,
    addresses: string[] = []
  ): Promise<IOToken[]> => {
    const graphqlQuery = `{
        otokens(first: 5, orderBy: expiry, orderDirection: asc, where: {
            expiry_gte: "${currentEpochinSeconds}"
        }) {
          tokenAddress
          underlyingAsset ${getUnderlyingCondition(addresses)} {
            id
            symbol
            name
            address
          }
          expiry
          strikePrice
        }
      }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );
      const oTokens = response.data.data.otokens as IOToken[];
      return oTokens;
    } catch (error) {
      throw new Error(error);
    }
  },
  getSimilarPotions: async (
    params: {
      expiry: BigInteger;
      duration: BigInteger;
      strikePrice: number;
      doubleStrikePrice: number;
      addresses: string[];
      limit?: number;
      assetPrice?: number;
    },
    mode: string
  ): Promise<IOToken[]> => {
    if (mode === "strike") {
      return Potions.getSimilarPotionByStrike(params);
    }
    if (mode === "duration") {
      return Potions.getSimilarPotionByDuration(params);
    }
    return Potions.getSimilarPotionByAsset(params);
  },
  getSimilarPotionByAsset: async (params: {
    expiry: BigInteger;
    addresses: string[];
    limit?: number;
    assetPrice?: number;
  }): Promise<IOToken[]> => {
    params.assetPrice = params.assetPrice * 2;
    const graphqlQuery = `${otokenFragments}
    query oTokens($expiry: BigInt!, $addresses: [String]!, $direction: String = "desc", $assetPrice: BigDecimal!, $limit: Int = 5) {
      otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, strikePrice_gt: 0.000001 strikePrice_lte: $assetPrice  }
        orderBy: purchasesCount
        orderDirection: $direction
        first: $limit
      ) {
        ...otokenCardData
      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        params
      );
      const data = response.data.data;
      return data.otokens as IOToken[];
    } catch (error) {
      throw new Error(error);
    }
  },
  getSimilarPotionByStrike: async (params: {
    expiry: BigInteger;
    strikePrice: number;
    doubleStrikePrice: number;
    addresses: string[];
    limit?: number;
  }): Promise<IOToken[]> => {
    params.doubleStrikePrice = params.strikePrice * 2;

    const graphqlQuery = `${otokenFragments}
    query oTokens($expiry: BigInt!, $addresses: [String]!, $strikePrice: BigDecimal!, $doubleStrikePrice: BigDecimal! $limit: Int = 5) {
      minStrike: otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, strikePrice_gt: 0, strikePrice_lte: $strikePrice }
        orderBy: strikePrice
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
      maxStrike: otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, strikePrice_gt: $strikePrice, strikePrice_lt: $doubleStrikePrice, }
        orderBy: strikePrice
        orderDirection: "asc"
        first: $limit
      ) {
        ...otokenCardData
      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        params
      );
      const data = response.data.data;
      const savers = data.minStrike
        .reverse()
        .concat(data.maxStrike) as IOToken[];
      return getCentralItems(savers, params.limit || 5);
    } catch (error) {
      throw new Error(error);
    }
  },
  getSimilarPotionByDuration: async (params: {
    expiry: BigInteger;
    duration: BigInteger;
    strikePrice: number;
    doubleStrikePrice: number;
    addresses: string[];
    limit?: number;
  }): Promise<IOToken[]> => {
    params.doubleStrikePrice = params.strikePrice * 2;
    const graphqlQuery = `${otokenFragments}
    query oTokens($expiry: BigInt!, $duration: BigInt!, $addresses: [String]!, $strikePrice: BigDecimal!, $doubleStrikePrice: BigDecimal!, $limit: Int = 5) {
      minDurationMinStrike: otokens(
        where: { expiry_gte: $expiry, expiry_lte: $duration, underlyingAsset_in: $addresses, strikePrice_gt: 0.000001, strikePrice_lte: $strikePrice }
        orderBy: strikePrice
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
      minDurationMaxStrike: otokens(
        where: { expiry_gte: $expiry, expiry_lte: $duration, underlyingAsset_in: $addresses, strikePrice_gt: $strikePrice, strikePrice_lte: $doubleStrikePrice }
        orderBy: strikePrice
        orderDirection: "asc"
        first: $limit
      ) {
        ...otokenCardData
      },
      maxDurationMinStrike: otokens(
        where: { expiry_gt: $duration, underlyingAsset_in: $addresses, strikePrice_lte: $strikePrice }
        orderBy: strikePrice
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
      maxDurationMaxStrike: otokens(
        where: { expiry_gt: $duration, underlyingAsset_in: $addresses, strikePrice_gt: $strikePrice, strikePrice_lte: $doubleStrikePrice }
        orderBy: strikePrice
        orderDirection: "asc"
        first: $limit
      ) {
        ...otokenCardData
      },
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        params
      );
      const data = response.data.data;
      const maxDuration = getCentralItems(
        data.maxDurationMinStrike.reverse().concat(data.maxDurationMaxStrike),
        params.limit || 5
      ) as IOToken[];
      const minDuration = getCentralItems(
        data.minDurationMinStrike.reverse().concat(data.minDurationMaxStrike),
        params.limit || 5
      ) as IOToken[];
      return getCentralItems(
        minDuration.concat(maxDuration),
        params.limit || 5
      );
    } catch (error) {
      throw new Error(error);
    }
  },
  getMostPopular: async (
    expiry: string,
    addresses: string[] = [],
    limit = 8
  ): Promise<PopularOTokens> => {
    const graphqlQuery = `${otokenFragments}
    query oTokens($expiry: BigInt!, $addresses: [String]!, $limit: Int = 8) {
      mostPurchased: otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, purchasesCount_gt: 0 }
        orderBy: purchasesCount
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
      mostCollateralized: otokens(
        where: { expiry_gte: $expiry, underlyingAsset_in: $addresses, purchasesCount_gt: 0 }
        orderBy: collateralized
        orderDirection: "desc"
        first: $limit
      ) {
        ...otokenCardData
      },
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        {
          expiry,
          addresses,
          limit,
        }
      );
      return response.data.data as PopularOTokens;
    } catch (error) {
      throw new Error(error);
    }
  },
  loadMorePopularPotions: async (
    expiry: string,
    filteringMode: string,
    alreadyLoadedIds: string[] = [""],
    addresses: string[] = [],
    limit = 8
  ) => {
    const graphqlQuery = filteringModeToQuery[filteringMode];
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { expiry, alreadyLoadedIds, addresses, limit }
      );
      return response.data.data.otokens;
    } catch (error) {
      throw new Error(error);
    }
  },
  getOrders: async (otokenId: string) => {
    const graphqlQuery = `
      query oTokenOrders($otokenId: String!) {
        orders: orderBookEntries(
          where: { otoken: $otokenId }
          orderBy: timestamp
          orderDirection: asc
        ) {
          premium
          timestamp
          numberOfOTokens
        }
      }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { otokenId }
      );
      return response.data.data.orders;
    } catch (error) {
      throw new Error(error);
    }
  },
};

export { Potions };
