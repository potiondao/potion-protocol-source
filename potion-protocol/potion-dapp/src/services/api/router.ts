import { uniqWith as _uniqWith } from "lodash-es";

import ApiService from "@/services/api.service";
import { Criteria } from "@/subgraph";
import { IPoolUntyped } from "@/types";

const baseUrl = process.env.VUE_APP_POTION_SUBGRAPH_URL;
const resource = "";

const Router = {
  getPoolsFromCriteria: async (
    underlyingAddress: string,
    strikeInPercent: string,
    minDuration: string
  ): Promise<IPoolUntyped[]> => {
    const graphqlQuery = `
    {
      criterias(where: {
        underlyingAsset: "${underlyingAddress}",
        maxDurationInDays_gte: ${minDuration},
        maxStrikePercent_gte: ${strikeInPercent}
        }) {
        underlyingAsset {
          address
          name
          symbol
        }
        isPut
        maxStrikePercent
        maxDurationInDays
        strikeAsset {
          address
          name
          symbol
        }
        criteriaSets {
          criteriaSet {
            templates {
              pools(first: 1000, orderBy: averageCost, orderDirection: asc) {
                id
                size
                locked
                unlocked
                utilization
                lp
                poolId
                template {
                  curve {
                    id
                    a
                    b
                    c
                    d
                    maxUtil
                  }
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
      const criterias = response.data.data.criterias as Criteria[];
      const pools: IPoolUntyped[] = [];
      criterias.map((criteria) => {
        criteria.criteriaSets.forEach((criteriaSet) => {
          criteriaSet.criteriaSet.templates.forEach((template) => {
            template.pools.forEach((pool) => {
              pools.push({
                id: pool.id,
                locked: pool.locked,
                poolOrderSize: "0",
                lp: pool.lp,
                poolId: pool.poolId,
                size: pool.size,
                unlocked: pool.unlocked,
                utilization: pool.utilization,
                underlyingAddress: criteria.underlyingAsset.address,
                strikeAddress: criteria.strikeAsset.address,
                maxStrikePercent: criteria.maxStrikePercent,
                maxDurationInDays: criteria.maxDurationInDays,
                isPut: criteria.isPut,
                template: {
                  curve: {
                    id: pool.template.curve.id,
                    a: pool.template.curve.a,
                    b: pool.template.curve.b,
                    c: pool.template.curve.c,
                    d: pool.template.curve.d,
                    maxUtil: pool.template.curve.maxUtil,
                  },
                },
              });
            });
          });
        });
      });
      return _uniqWith(
        pools,
        (poolA, poolB) => poolA.lp === poolB.lp && poolA.poolId === poolB.poolId
      );
    } catch (error) {
      throw new Error(error);
    }
  },
};

export { Router };
