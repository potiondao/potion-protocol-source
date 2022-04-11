# Subgraph Entities

## Debugging

If debugging is needed, I recommend using the log module to print debug values.

```
import { log } from "@graphprotocol/graph-ts";
...
log.info("log statement here", [<list of variables>]);s
```

## Queries

The entities below can be queried locally viewing the explorer at: [http://localhost:8000/subgraphs/name/potion-labs/potion-subgraph/graphql?](http://localhost:8000/subgraphs/name/potion-labs/potion-subgraph/graphql?). Here's a link to [documentation on the query language](https://thegraph.com/docs/graphql-api#schema)

## Note on formatting currencies

When the subgraph, the support for reading in data from contracts was in very early stages. As of now, all values are stored as Decimals (for future-proofing of services that rely on this), but with no decimals. EG if an ERC-20 uses FixedPoint and has 2 decimal places, the subgraph would store `250` instead of `2.50`.

## Entities

Entities are treated as individual entries in the subgraph, each entity comes from some type (described below), and has a unique ID. The ID is calculated by combining deterministic properties of each entity.

### Cosh

Contains the parameters (a, b, c, d) and the maximum util for each curve stored on chain. The hash of the parameters is the ID.

### Criteria

Describes one individual criteria that a LP can specify for a pool to write orders for, using the curve to price these orders. This contains the Underlying Assets's address, the token to use price the strike, the Maximum Strike Percentage, and the max duration.

### Criteria Set

Describes a list of individual criterias that is used by a Pool to specify the strategies to underwrite. The list of criterias is a list of sorted hashes.

### Pool

Describes a pool of liquidity created by a LP. It has a Pool ID (int) and LP (address) which defines its creator and number. Also contains data for the total size of the pool, the locked amount, as well as criteriaSetHash, and curveHash.

### Template

This defines the aggregation of pools with the same curveHash and criteriaSetHash. This is used by the application to allow users to discover frequently used curve and criteria set combinations.

### PoolSnapshot

Describes a Pool at a specific timestamp. This is useful for tracking the Profits and Losses (P&L) of a pool. Each snapshot is saved after a pool's on chain values have changed. This has the same fields as a pool, but in addition it has a timestamp, action type, which describes the type of action performed on the pool that caused it to change value, and action Amount (if a withdraw/deposit/exercise occurred.) 

### OToken

Describes an oToken used to describe the relationship between the list of pools providing capital to the token (LP Record), and a list of users who purchase and hold onto a put option (BuyerRecord). This entity holds data on the creator, underlying, collateral, strike asset, strike price, and expiry.

### LPRecord

Describes a LPs claim to an oToken. Note that an LP may have several pools that send capital to a oToken (note the poolIds array). This contains the totalLiquidityCollateralized, which tracks the maximum collateralized liquidity and liquidityCollateralized (the current amount). We have two data points here since a LP can partially reclaim some of their oTokens.

### BuyerRecord

Describes the premium paid and number of oTokens that a buyer/user holds. 
