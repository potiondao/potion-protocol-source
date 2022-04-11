# Potion Subgraph

This subgraph tracks changes Pools, Curves, Criterias, and oTokens, with data aggregated to the pool level. The data stored in the subgraph tracks actions like the following:

- Liquidity deposits / withdraws from individual pools
- Pools changing curves
- Pools changing criteria sets
- Option purchase and exercise by users from pools
- Settlement and distibution of capital after expiry of an option.

## Running Locally

This is designed to be ran within the `potion-protocol` repository. `yarn prepare` looks for the relative import of json files located in `potion-contracts/deploy` to find the deployed address of contracts.

There are instructions in [the potion-protocol README](../README.md) on how to mock all of the data, including running the dockerized [graph-node](https://github.com/graphprotocol/graph-node).

Once the `graph-node` is launched and running locally at `http://localhost:8020`, use the commands `yarn prepare:ganache && yarn build-deploy` to deploy the potion-subgraph from within this folder or `subgraph-deploy` from within the root of `potion-protocol`.

Example Queries: [docs/schemas.md](docs/schemas.md)

## To deploy to kovan

First log in to https://thegraph.com/studio/ and create yourself a subgraph. Once you have a subgraph you should see a "deploy key" in the top-right.

N.B. Never "Publish" your subgraph if it's only intended for testing!

1. Ensure you have the correct config in subgraph.yaml. E.g. run `yarn prepare:kovan` or `yarn prepare:kovan.independent`
2. Authenticate the CLI: `npx graph auth --studio <your deploy key>`
   - If the `--studio` is not recognised, try installing a newer version of the graph command line tool, either locally or globally, and using that.
3. Build the subgraph: `graph codegen && graph build`
4. Deploy the subgraph: `graph deploy --studio test`. You will need to specify a version number.

## Entity Documentation

Visit [docs/schemas.md](docs/schemas.md)

## Running tests

To run our unit tests you need to have the [matchstick](https://github.com/LimeChain/matchstick) binary in the `bin` folder.
Because it is specific for your OS, we can't add this binary to our repository and you need to retrieve it yourself

- If you use Ubuntu or OSX or Windows there are binaries already available in the matchstick repo, just fetch it and put in the `bin` folder
- If there isn't a prebuilt binary for your system you will need to manually compile matchstick: for doing it you need `rust`, `cargo` and `postgre` installed in your system
