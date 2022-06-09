# Potion Smart Contracts

This repository contains the Smart Contracts of the Potion protocol.

Potion is a decentralized protocol for the creation of price insurance contracts running on the Ethereum network.

Before getting started please be sure to have installed the [Requirements](#requirements).

## Requirements

- [NodeJS](https://nodejs.org/en/download/) (v14)

- [Yarn](https://yarnpkg.com/getting-started/install)

## Install dependencies

`yarn install`

## Compile / Build

`yarn build`

As part of the build, [typescript bindings](https://github.com/ethereum-ts/TypeChain) types are generated for the contracts. This facilitates compile-time checks on scripts and tests, as well as auto-complete etc. in modern IDEs.

## Run tests

`yarn test`

Tests are written using [Waffle's chai matchers](https://ethereum-waffle.readthedocs.io/en/latest/). By default, they execute against a Hardhat Network, which greatly speeds up testing compared with other mainstream options (e.g. truffle, ganache, testrpc) and also [enables console logging](https://hardhat.org/hardhat-network/), which can be a godsend when diagnosing smart contract bugs.

## Run tests with gas measurements

- `yarn test:gas` to report to screen; OR
- `yarn test:gasreport` to archive results to file, which can be useful for retrospectively tracking the impacts of code changes on gas usage

## Lint and prettify code

This is automated on commit (see `lint-staged` config in `package.json`), but can also be run at any time:

- `yarn lint` reports without fixing; OR
- `yarn lint:fix` fixes where fixes are known

For a smooth development experience it is recommended that you also configure your IDE to format code on save, using the prettier settings in `package.json`

## Opyn dependencies

The project makes use of [smart contracts from Opyn](https://github.com/opynfinance/GammaProtocol) to collateralise and represent options. See [our Opyn README](./contracts/packages/opynInterface/README.md) for details of how this is handled on a technical level, including details of what must be done when Opyn upgrade their code.

## Deployments

The project includes a deployment script located at `./scripts/deploy.ts`.

This script imports a configuration file (`./scripts/lib/deployConfig`) that includes configuration information for the different Ethereum networks(kovan, goerli, mainnet) and development environments.

In order to deploy to the different Ethereum networks. We include some predefined script tasks:

- `deploy:kovan` # deploys to Kovan

- `deploy:goerli` # deploys to Goerli

- `deploy` # deploys to mainnet

- `deploy:ganache` # creates a local deployment for testing

Depending which network you want to deploy, we need to define some environment variables.

We have included an .env.dist file that contains the required environment variables.

For instance, if we want to deploy to `Kovan`, we require the following variables.

- KOVAN_MNEMONIC="<VALUE>"
- KOVAN_WEB3_ENDPOINT="<VALUE>"

## Post Deployment Actions

In some escenarios we may require to execute actions after a deployment to a certain network, for instance, we could use Post Deployment Actions for:

- To allocate collateral tokens from a faucet to users.

- To deploy sample tokens

- To Initialize sample purchases and sample data.

In order to do so, we have created a set of `postDeployActions` functions.

The `postDeployActions` are configured in the `./scripts/lib/deployConfig` file. For instance, if we want to execute an action after a deployment to the `Kovan` network, you should have a configuration as:

```
    kovan: {
        ....
        postDeployActions: [<Post Deploy Action>],
    }
```

The Post Deploy Action has to implement the following interface:

```
export interface PostDeployAction {
  executePostDeployAction(
    depl: Deployment,
    dataAlreadyDeployed: PostDeployActionsResults,
    printProgress: boolean,
  ): Promise<PostDeployActionResult>
}
```
