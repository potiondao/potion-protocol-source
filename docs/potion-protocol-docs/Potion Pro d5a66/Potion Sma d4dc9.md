# Potion Smart Contract System Description

This document outlines the scope of Potion’s smart contracts operational capabilities.

It provides a high level description for how the system has been designed to behave.

## Basic description of the system

- Potion v0 is a market maker for [put options](https://www.investopedia.com/terms/p/putoption.asp): it helps sellers (LPs) and buyers find a price for option trades.
- **Basic process:**
    - LPs perform certain mathematical analysis off-chain, to come up with a “premium bonding curve”. These are curves that represent a pricing function that depends on LP pool utilisation.
    - LPs create capital pools in the Potion protocol, and can bind the aforementioned bonding curves to them.
    - Each capital pool in the Potion system belongs to a single LP. Each pool has its own utilization state, separate from the rest.
    - Each pool is associated with a customisable criteria set (a collection of assets, strikes and durations for which that the LP is willing to underwrite put options)
    - Options are collateralized using USDC, only if buyers pay the premiums described by the curve when buying an option that matches the pool criteria set.
    - When a buyer buys an option, the collateral can come from a single or multiple LP pools. The buyer describes the pools they wish to buy from.
    - Buyers discover the cheapest Pools and build their orders using a smart router (off-chain) that inspects all available prices on-chain, and proposes optimal selection of pools according to their curves and current utils. For clarity, this router is out of the scope of the audit.
    - Potion relies on Opyn for the collateralisation and settlement of the “otokens” that are Opyn’s on-chain representation of options.
    - When a buyer buys an option, they pay a premium to their chosen LP(s), and those LPs send the required amount of collateral to Opyn’s smart contract system, to fully collateralize the options. The buyer is then issued with some oTokens (ERC20 tokens) with their chosen settlement date and strike price.
    - Users can mint brand new oToken option contracts with precise strike and duration, or can re-use pre-minted oToken contracts (accepting whichever strike and duration they were minted with).
    - Otokens represent European options, and are cash settled on expiry. Once oTokens expire, buyers and LPs can exercise, and withdraw the respective payoff (again, in the stablecoin used as collateral) from the contract.

## Architecture

- There is one LP contract holding all collateral for all LPs, and keeping track of the criteria sets and utilizations configured for each pool of capital.
- Users interact with a router to find cheapest available pool of capital.
- When a buyer gets an option, an oToken contract is minted, and collateralized with capital from various LPs.
- There is one single LP contract, and as many oTokens as option configurations minted.

[https://lh6.googleusercontent.com/ORiphpQC3Glp_B1za6j8p95oswlGXC6e8d2Ek1ddRZjou0SiOr1OytAcaWer__hOA94XNvontPqod3ES2UmZ9N0RlFckAOmg4VIuvpvPpksforHZj8AAOoNOFSidFa6LvC1GVNx_](https://lh6.googleusercontent.com/ORiphpQC3Glp_B1za6j8p95oswlGXC6e8d2Ek1ddRZjou0SiOr1OytAcaWer__hOA94XNvontPqod3ES2UmZ9N0RlFckAOmg4VIuvpvPpksforHZj8AAOoNOFSidFa6LvC1GVNx_)

**Potion LP Pools**

- LPs can create Pools that they control, and that are unique to them. These pools are data structures mapped inside the PotionLiquidity.sol contract.
- Each LP pool will have its own **Pool Utilization** (and therefore will be quoting different pricing relative to other pools at different utils or with different curves):
    - For $\text{PoolOfCapital}_k$, $\text{Utilization}_k$ is defined as:
    
    $$
    \text{Utilisation}_k = \frac{\text{LockedCapital}_k}{\text{TotalCapital}_k}
    $$
    
    - LockedCapital is the capital that is actively being used to collateralise oTokens, and which has therefore been transferred to Opyn’s smart contracts.
- Each LP will have its own **Pool Criteria Set**, which describes the options that can be collateralised with capital from the pool. Each criteria in the criteria set contains 3 main pieces of data:
    - Asset: Defines the underlying assets for which the pool can lock collateral.
    - Strike: If strike is set to K%, then this pool will only collateralise options of strike K and below. For example, if Strike criteria is 120%, this means a strike that is 120% of the spot price at the time of purchase. I.e. 20% “in the money” (ITM) at the time of purchase.
    - Duration: Like Strike, if criteria is set to Duration d, the pool can use its capital to collateralize options with any duration <= d
- Because each Criteria Set can contain multiple criteria, the same pool of capital can optionally configure itself to:
    - sell multiple assets at once (eg, ETH, BTC, MKR could all be sold by the same pool).
    - Sell options at multiple strike percentages (e.g. all of 10% ITM, At The Money (ATM), and 10% Out of The Money (OTM))

## Key functionality and system behavior

- **LPs can deposit collateral. Once deposited, this collateral can only be controlled by them.**
- **LPs can create pools**. Each pool belongs to a single LP, and defines:
    1. Premiums: through bonding curve based on cosh function with 5 parameters a,b,c,d and maxUtilisation
    2. The asset(s) that the LP is willing to write options for (through criteria sets)
    3. The range of durations, in days, that the LP is willing to write options for (through criteria sets)
    4. The range of strike prices, as a percentage of the Chainlink-derived spot price, that the LP is willing to write options for (through criteria sets)
    5. Examples:
        - $\text{LP}_A$creates a pool for UNI strike 20% OTM 1day, MKR 25% OTM 1day, and USDC 5% OTM 7days, all with premium curve A.
        - $\text{LP}_B$creates a pool for wBTC strike 5% ITM, duration 1 month, with premium curve B.
        
- **LPs can supply capital into valid oTokens in exchange for valid premiums.** Provided that premiums matching the bonding curve are sent to the contract, and that the oToken specifications meet the criteria set, the contract will release capital from the pool into Opyn’s system to collateralise newly-minted otokens. The smart contract verifies:
    1. oToken meets asset, strike and duration criteria
    2. Premium matches the value expected from the bonding curve, considering the utilization of the pool both before and after the purchase of the option.
    
- **LPs can reclaim capital from oTokens back into LP manager contract. Once the oTokens have expired, LPs can “claim back” their payoff. This is a two-stage process:**
    1. Funds are reclaimed from the Opyn contracts into the PotionLiquidityPool contract. This is atomic.
    2. Funds are redistributed to the appropriate LPs
        - If the number of LPs is large, this may need to be done across multiple transactions. The EOA issuing the request (probably a user of our webapp) is responsible for specifying the list of LPs, and the smart contract merely verifies them.

Either or both stages can be done by anyone, on behalf of LPs. And if the number of LPs is small, both stages can be done in the same transaction.

- **LP can withdraw capital from the PotionLiquidity.sol contract. At any point LPs can remove unlocked capital from the Potion system.**
    1. **LPs can withdraw any unlocked capital straight away**. This will increase the utilization value of that pool of capital.
    2. **LP can signal intent to withdraw utilized (locked) capital, for future withdrawal**. In practice this is done by configuring zero criteria for the pool, so that the locked capital in the pool cannot be re-used by new buyers once it has been reclaimed (unlocked).
    
- **LPs can update the criteria set or curve. At any point LPs can update the curve or criteria set of their pools**
    1. **Update criteria set**. Adding or removing assets, changing duration, changing strikes
    2. **Update curve**. Choose new curve parameters for the existing assets.
    
- **Buyers (or protocols) can buy options. The Potion liquidity system will supply collateral to oTokens when all rules are met.**

- **Buyers can exercise options**. Potion (through Opyn’s oToken contracts) operates cash-settled European-style options, meaning they can only be exercised at expiry, and not before.
    1. When an option is exercised, the Chainlink oracle will supply the price of the underlying at settlement, and payoffs for LP and users will be calculated.
    2. The buyer-side of this settlement process happens in Opyn’s contracts and is therefore out of scope.
    3. The unused collateral is returned to individual LPs through Potion’s contracts, so this part of the process is in scope.
    
- **Buyers can withdraw payoffs**. Once the option has been exercised, payoffs can be withdrawn into their wallets.

## **Resulting system behavior**

- No LPs are able to affect the balance, utilisation or pricing from other LPs
- No users are able to affect the pricing of LPs, other than by purchasing options and updating utilization.
- Capital in the system is totally self managed.

This was the document used to brief our auditors, Consensys Diligence.