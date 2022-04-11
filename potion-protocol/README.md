# Potion Development Enviroment

---

Dependencies:

Requirements to run the development environment

- Node.js Version 14.16.0 LTS
- Yarn
- Install and run Docker (this should add a `docker-compose` command to your command line path)
- If using Linux or WSL2, install the libsecret package. E.g.:
  - Debian/Ubuntu: sudo apt-get install libsecret-1-dev
  - Red Hat-based: sudo yum install libsecret-devel
  - Arch Linux: sudo pacman -S libsecret

---

Initial setup:

1. Clone the repo
2. Initialize the the project and download all dependencies, by running `./scripts/init`

### Frontend Setup

The `./scripts/init` will copy the various `.env` files inside the `./potion-dapp` folder. You WILL NEED to provide an `etherscan api key` and the `etherscan url`.
After you provide the environment variables:

1. Run `./scripts/develop` to start the services and deploy the smart contracts(ganache and subgraph);
2. CD into `potion-dapp` and run `yarn serve:ganache` to run the frontend locally.
3. The wallet mnemonic to import into Metamask is: `test test test test test test test test test test test junk`

## To deploy a local dev & testing environment:

2. Run `./scripts/develop`

3. To test if all of this worked, visit [http://localhost:8000/subgraphs/name/potion-labs/potion-subgraph/graphql](http://localhost:8000/subgraphs/name/potion-labs/potion-subgraph/graphql) and run a query, such as the ones in `potion-subgraph/sample_query.md`, or simply:

   ```
   {
     criterias(first: 5) {
       id
       underlyingAsset
     }
   }
   ```

4. Start the webapp with `yarn serve` and visit [http://localhost:8080](http://localhost:8080) to test if it is working.
## To update all the dependencies:

5. run `./scripts/update`

# Common Setup Errors

- If your subrgaph node server is down and you see the error:

  ```
  thread 'tokio-runtime-worker' panicked at 'Ethereum node provided net_version 1618480152608, but we expected 1618477953366. Did you change networks without changing the network name?', store/postgres/src/chain_store.rs:89:21
  ```

  Delete the `data` folder and restart the setup process (`rm -rf data`).
