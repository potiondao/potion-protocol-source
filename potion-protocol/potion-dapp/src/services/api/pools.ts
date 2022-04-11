import { contractsAddresses } from "@/services/contracts";

import ApiService from "../api.service";

const baseUrl = process.env.VUE_APP_POTION_SUBGRAPH_URL;
const resource = "";

const templateFragments = `fragment templateCardData on Template {
  id
  creator
  numPools
  size
  pnlPercentage
  curve {
    a
    b
    c
    d
    maxUtil
  }
  criteriaSet {
    criterias {
      criteria {
        underlyingAsset {
          address
          decimals
          symbol
          name
        }
        strikeAsset {
          address
          decimals
          symbol
          name
        }
        maxStrikePercent
        maxDurationInDays
      }
    }
  }
}`;

const filteringModeToQuery = {
  bySize: `${templateFragments}
    query loadMoreTemplatesBySize($filteringValue: BigDecimal!, $orderDirection: String, $alreadyLoadedIds: [ID]!, $num: Int = 8) {
      templates(
        where: { size_gt: $filteringValue, id_not_in: $alreadyLoadedIds }
        orderBy: size
        orderDirection: $orderDirection
        first: $num
      ) {
        ...templateCardData
      },
    }
    `,
  byNumber: `${templateFragments}
    query loadMoreTemplatesByNumber($filteringValue: BigDecimal!, $orderDirection: String, $alreadyLoadedIds: [ID]!, $num: Int = 8) {
      templates(
        where: { numPools_gt: $filteringValue, id_not_in: $alreadyLoadedIds }
        orderBy: numPools
        orderDirection: $orderDirection
        first: $num
      ) {
        ...templateCardData
      },
    }
    `,
  byPnl: `${templateFragments}
    query loadMoreTemplatesByPnl($filteringValue: BigDecimal!, $orderDirection: String, $alreadyLoadedIds: [ID]!, $num: Int = 8) {
      templates(
        where: { pnlPercentage_gt: $filteringValue, id_not_in: $alreadyLoadedIds }
        orderBy: pnlPercentage,
        orderDirection: desc,
        first: $num
      ) {
        ...templateCardData
      }
    }
    `,
};

const Pools = {
  getProductsUSDCCollateral: async () => {
    const graphqlQuery = `
    {
      products(where: {isWhitelisted: true, collateral: "${contractsAddresses.collateralTokenAddress.toLowerCase()}"}) {
        id
        underlying {
          decimals
          name
          symbol
          address
        }
      }
    }

    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );
      return response.data.data.products.map((product) => product.underlying);
    } catch (error) {
      throw new Error(error);
    }
  },
  getTemplate: async (params) => {
    const graphqlQuery = `{
      template(${params}) {
        id
        size
        numPools
        pnlPercentage
        creator
        curve {
          a
          b
          c
          d
          maxUtil
        }
        criteriaSet {
          criterias {
            criteria {
              underlyingAsset {
                address
                decimals
                symbol
                name
              }
              strikeAsset {
                address
                decimals
                symbol
                name
              }
              maxStrikePercent
              maxDurationInDays
              isPut
              id
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
      return response.data.data.template;
    } catch (error) {
      throw new Error(error);
    }
  },
  getPopularTemplates: async ({
    num,
    minClones,
    minPnl,
    size,
    orderDirection,
  }) => {
    const graphqlQuery = `${templateFragments}
    query mostPopularTemplates($size: BigDecimal!, $minClones: BigInt!, $minPnl: BigDecimal!, $orderDirection: String, $num: Int = 8) {
      byNumber: templates(
        where: { numPools_gt: $minClones }
        orderBy: numPools
        orderDirection: $orderDirection
        first: $num
      ) {
        ...templateCardData
      },
      bySize: templates(
        where: { size_gt: $size }
        orderBy: size
        orderDirection: $orderDirection
        first: $num
      ) {
        ...templateCardData
      },
      byPnl: templates(
        where: { pnlPercentage_gt: $minPnl }
        orderBy: pnlPercentage,
        orderDirection: desc,
        first: $num
      ) {
        ...templateCardData
      }
    }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { num, size, minClones, minPnl, orderDirection }
      );
      return response.data.data;
    } catch (error) {
      throw new Error(error);
    }
  },
  loadMoreTemplates: async ({
    num,
    filteringMode,
    filteringValue,
    alreadyLoadedIds,
    orderDirection,
  }) => {
    const graphqlQuery = filteringModeToQuery[filteringMode];
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { num, filteringValue, orderDirection, alreadyLoadedIds }
      );
      return response.data.data.templates;
    } catch (error) {
      throw new Error(error);
    }
  },
  getTemplatesByNumbers: async ({ num, minClones, orderDirection }) => {
    const graphqlQuery = `{
      templates(first: ${num}, where: {numPools_gte: ${minClones}}, orderBy: size, orderDirection: ${orderDirection}) {
        id
        numPools
        size
        pnl
        curve {
          a
          b
          c
          d
          maxUtil
        }
        criteriaSet {
          criterias {
            criteria {
              underlyingAsset {
                address
                decimals
                symbol
                name
              }
              strikeAsset {
                address
                decimals
                symbol
                name
              }
              maxStrikePercent
              maxDurationInDays
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
      return response.data.data.templates;
    } catch (error) {
      throw new Error(error);
    }
  },
  getTemplatesBySize: async ({ num, size, orderDirection }) => {
    const graphqlQuery = `{
      templates(first: ${num}, where: {size_gte: ${size}}, orderBy: size, orderDirection: ${orderDirection}) {
        id
        numPools
        size
        pnl
        curve {
          a
          b
          c
          d
          maxUtil
        }
        criteriaSet {
          criterias {
            criteria {
              underlyingAsset {
                address
                decimals
                symbol
                name
              }
              strikeAsset {
                address
                decimals
                symbol
                name
              }
              maxStrikePercent
              maxDurationInDays
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
      return response.data.data.templates;
    } catch (error) {
      throw new Error(error);
    }
  },
  getPool: async (id) => {
    const graphqlQuery = `{
      pool(id: "${id}") {
        id
        poolId
        lp
        size
        locked
        pnlPercentage
        snapshots {
          id
          size
          locked
          pnlPercentage
          actionAmount
          actionType
          timestamp
          utilization
          liquidityAtTrades
        }
        template {
          curve {
            id
            a
            b
            c
            d
            maxUtil
          }
          criteriaSet {
            criterias{
              criteria {
                id
                underlyingAsset {
                  address
                  decimals
                  symbol
                  name
                }
                strikeAsset {
                  address
                  decimals
                  symbol
                  name
                }
                isPut
                maxStrikePercent
                maxDurationInDays
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
      return response.data.data.pool;
    } catch (error) {
      throw new Error(error);
    }
  },
  getNumberOfPools: async (walletAddress) => {
    const graphqlQuery = `
    {
      pools(where: {lp: "${walletAddress}"}) {
        id
      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery
      );
      return response.data.data.pools.length;
    } catch (error) {
      throw new Error(error);
    }
  },
  getPools: async (
    lp: string = null,
    lastPoolId: number = -1,
    first: number = 8
  ) => {
    /**
     * We call it to get all the pools
     * walletAddress: optional parameter, to get the pools from a given wallet
     **/
    const graphqlQuery = `
      query getPools($lp: String!, $lastPoolId: BigInt, $first: Int = 8) {
        pools(
          where: {
            lp: $lp,
            poolId_gt: $lastPoolId,
          },
          orderBy: poolId,
          orderDirection: asc,
          first: $first
        ) {
          id
          lp
          poolId
          size
          locked
          utilization
          pnlPercentage
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
                  strikeAsset {
                    address
                    decimals
                    symbol
                    name
                  }
                  maxStrikePercent
                  maxDurationInDays
                }
              }
            }
          }
          snapshots {
            size
            locked
            timestamp
            actionType
          }
        }
      }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        {
          lp,
          lastPoolId,
          first,
        }
      );
      return response.data.data.pools;
    } catch (error) {
      throw new Error(error);
    }
  },
  getSnapshotsByPool: async (
    currentPool: string,
    alreadyLoadedIds: string[] = [""],
    num: number = 8
  ) => {
    const graphqlQuery = `
      query getSnapshotsByPool($currentPool: ID, $alreadyLoadedIds: [ID], $num: Int) {
        poolSnapshots (
          where: {
            currentPool: $currentPool
            id_not_in: $alreadyLoadedIds
          }
          first: $num
          orderBy: timestamp,
          orderDirection: asc
        ) {
          id
          size
          actionAmount
          actionType
          locked
          timestamp
          poolId
          pnlPercentage
          pnlTotal
          templatePnlPercentage
          templateSize
          templateUtilization
          currentPool {
            id
          }
        }
      }
    `;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        {
          currentPool,
          alreadyLoadedIds,
          num,
        }
      );
      return response.data.data.poolSnapshots;
    } catch (error) {
      throw new Error(error);
    }
  },
  getSnapshotsByTemplate: async (
    templateAddress: string,
    alreadyLoadedIds: string[] = [""],
    num: number = 1000
  ) => {
    const graphqlQuery = `
      query getSnapshotsByTemplate($templateAddress: ID, $alreadyLoadedIds: [ID], $num: Int) {
      poolSnapshots(
        orderBy: timestamp,
        orderDirection: asc,
        where: {
          template: $templateAddress
          id_not_in: $alreadyLoadedIds
        }
        first: $num
        ) {
        id
        size
        actionAmount
        actionType
        locked
        timestamp
        poolId
        pnlPercentage
        pnlTotal
        templatePnlPercentage
        templateSize
        templateUtilization
        currentPool {
          id
        }
      }
    }`;
    try {
      const response = await ApiService.graphql(
        baseUrl + resource,
        graphqlQuery,
        { templateAddress, alreadyLoadedIds, num }
      );
      return response.data.data.poolSnapshots;
    } catch (error) {
      throw new Error(error);
    }
  },
  getLpPoolsForOtoken: async (lp, otokenAddress) => {
    const graphqlQuery = `
    {
      pools(where: {lp: "${lp}"}) {
        poolRecords(where: {otoken: "${otokenAddress}"}) {
          id
          pool {
            poolId
            lp
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
      const pools = response.data.data.pools;
      return pools.filter((pool) => pool.poolRecords.length > 0);
    } catch (error) {
      throw new Error(error);
    }
  },
  /**
   * Function that finds the oTokens of a LP.
   * @param {string} lpAddress Address of the lp.
   * @return {oToken[]} List of non reclaimed oTokens.
   */
  getOTokens: async (id) => {
    const graphqlQuery = `{
      poolRecords(where: {pool: "${id}"}) {
        id
        premiumReceived
        collateral
        numberOfOTokens
        returned
        otoken {
          strikePrice
          expiry
        }
        pool {
          poolId
        }
        lpRecord {
          lp
          otoken {
            id
            underlyingAsset {
              id
              address
              symbol
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
      return response.data.data.poolRecords;
    } catch (error) {
      throw new Error(error);
    }
  },
};

export { Pools };
