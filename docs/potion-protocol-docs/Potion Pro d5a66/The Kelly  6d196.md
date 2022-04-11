# The Kelly Machine AMM

A smart contract architecture for automated decentralized risk markets based on the Kelly Criterion designed for long term capital sustainability.

### ***Abstract***

A key blocker to scalability in derivative AMMs is the risk of non survival for the LP. Many existing architectures are based on Black-Scholes-Merton pricing which is known to inadequately characterize crypto instruments and risk ruin for LPs. In this paper we introduce the ***Kelly Machine*** - an automatic market maker architecture for risk management based on the Kelly Criterion and survival constraints.

While the Kelly Criterion is traditionally used to implement optimal *risk sizing* strategies, here we present an extension of the use of the Kelly Criterion into the realm of optimal combined *risk pricing & sizing* strategies. The result of this optimization are so-called “***Kelly Optimal bonding curves*”** which allow the creation of automated Kelly Criterion based trading strategies.

The Kelly Machine was designed in the hopes of contributing towards higher levels of market stability and risk management within the decentralized ecosystem, and will be released as a public good.

# 1. General system overview

An automatic market maker (AMM) is a set of smart contracts that autonomously manage capital on behalf of Liquidity Providers (LPs), in order to create automated on-chain services to buyers.

[https://lh3.googleusercontent.com/oUuQsSi3qivmtmtDBKHNyM7zHn7zpI03yjTRqoxQTRLNTAOY0mmjhaDR9YAxfibfpJv4ItyMtlFE0rxv-0kan-gi3PL3YS0BxmOAHFPOd3ckY2BV41Y1DtS4DTdYmPo99a9-WtKN](https://lh3.googleusercontent.com/oUuQsSi3qivmtmtDBKHNyM7zHn7zpI03yjTRqoxQTRLNTAOY0mmjhaDR9YAxfibfpJv4ItyMtlFE0rxv-0kan-gi3PL3YS0BxmOAHFPOd3ckY2BV41Y1DtS4DTdYmPo99a9-WtKN)

The Kelly Machine is **a new class of AMM designed to create on-chain risk instruments such as asset price insurance**. For example, a fully collateralized insurance on the price of Ethereum at $3000 for a duration of 1 month.

## **Participants**

Potion’s Kelly Machine intermediates two sets of users: Liquidity Providers (LPs), and Insurance Buyers.

LPs act as insurance providers - they provide capital to underwrite and collateralize the insurance policies being created and sold by the AMM. LPs charge a premium every time they collateralize an insurance contract. LPs participate in the hopes that premiums will more than offset losses from insurance claims, and that in the long run they will experience capital growth.

Insurance buyers buy insurance contracts which are securely collateralized on chain. At contract expiration time, the policy automatically assigns the correct insurance payout across the buyer and the seller of the contract.  Buyers participate because they want to protect themselves against risk (hedge application), or because they want to trade optionality in hopes the market crashes and they collect a large payout from a small premium (up to 10X and even 100X+  payout).

## **Pricing heuristic**

The Potion Kelly Machine uses an automated pricing system based on capital utilization that automatically charges a higher premium when the amount of capital at risk is higher. This ultimately results in LPs being able to become better protected from ruin.

An extension of the Kelly Criterion optimization is proposed. This optimization allows LPs to passively price insurance contracts at Kelly optimal prices automatically, by relying on a bonding curve relating capital utilization and premium required, what we call **“Kelly Optimal bonding curves”.**

[https://lh6.googleusercontent.com/CuJ_ISkfDtQkyQCzI50unnhIk69RCgqJzi8AR0jvbu2dwI3fKWV8477FBMQ25X89JOEpG5ZdM45OtTcwNIFZd76OwQvjuRdL0CijGgLReTNmol6RscC4agnPn_a4NpLATNBDsZyw](https://lh6.googleusercontent.com/CuJ_ISkfDtQkyQCzI50unnhIk69RCgqJzi8AR0jvbu2dwI3fKWV8477FBMQ25X89JOEpG5ZdM45OtTcwNIFZd76OwQvjuRdL0CijGgLReTNmol6RscC4agnPn_a4NpLATNBDsZyw)

# 2. Kelly Optimal bonding curves

Consider an insurance seller, selling insurance contracts with a Payoff Curve such as:

[https://lh5.googleusercontent.com/SWSxJe8JsIvXCyEDugHnrsK_UZsXNZIo0iU8fM4ZVFAqqoVVu-tBGCUZdsU1C7nt7e5mkM7DbPDNFWu7t2eTSHLdb8TyTEF4DC-9lhhOuBhUl9i5Oj3gXl6hlHN7R4HHVlzj-Xil](https://lh5.googleusercontent.com/SWSxJe8JsIvXCyEDugHnrsK_UZsXNZIo0iU8fM4ZVFAqqoVVu-tBGCUZdsU1C7nt7e5mkM7DbPDNFWu7t2eTSHLdb8TyTEF4DC-9lhhOuBhUl9i5Oj3gXl6hlHN7R4HHVlzj-Xil)

$$
\begin{align*}

\text{Payoff}\Big(S,R,p(u)\Big)= \begin{cases}
    R-S+p(u) & \text{if  $R<S$}\\
    p(u) & \text{if $R \geq S$}
  \end{cases}
\tag{1.1}
\end{align*}
$$

Where $S$ is the insurance strike price as percentage of current price , $R$ is the random return of the underlying asset being insured, and $p(u)$ is the premium charged by the LP as a function of utilization.

The expected growth rate for an LP can be written as:

$$
\mathbb E \big[G \big] = \text{exp} \big[  \sum_{r_{min}}^{r_{max}}Prob(r)\cdot \big(1+Payoff(S,r, p(u))\big)
 \big] -1
\tag{1.2}
$$

Here (1.2) is shown for various premium scenarios:

[https://lh3.googleusercontent.com/w-RVtbaYNTp1jg2yGfN-ihWPuTqBka8PgfK1SD66ERJqwPjC-HXzym5c7Za4yrnDnvB8Tvny20dL8UTCzhDve3wdV5vpzfS9lYO0FNxP7KQsUmqF1Mbz6uedjhZcvGA-JQH2Pds_](https://lh3.googleusercontent.com/w-RVtbaYNTp1jg2yGfN-ihWPuTqBka8PgfK1SD66ERJqwPjC-HXzym5c7Za4yrnDnvB8Tvny20dL8UTCzhDve3wdV5vpzfS9lYO0FNxP7KQsUmqF1Mbz6uedjhZcvGA-JQH2Pds_)

Where each line represents a different premium p. The premiums in color contain Kelly optimal conditions at the utilizations marked with a dot. Those are premiums that display a local maxima between 0% and 100% utilization.

Kelly Optimal pairs of util and premium all have in common that they have positive CAGR expectation. An LP can implement this pricing strategy using **Kelly Optimal Bonding Curves,** which can be found by joining all the Kelly Optimal points:

[https://lh5.googleusercontent.com/mx2LzHZeS4ByWfMOWPfZIqld6Rrfzo5Pn2AvHuxMhiwaSsDqwIWdGDruliCiZ-FZLyuoTBnpAIrdXcBM8tOpblPxLfXUZLfpRo-jvyPPFvTJyiqwudn1McH2kJqimwB2AQU2YF6v](https://lh5.googleusercontent.com/mx2LzHZeS4ByWfMOWPfZIqld6Rrfzo5Pn2AvHuxMhiwaSsDqwIWdGDruliCiZ-FZLyuoTBnpAIrdXcBM8tOpblPxLfXUZLfpRo-jvyPPFvTJyiqwudn1McH2kJqimwB2AQU2YF6v)

It can be observed that the resulting optimal bonding curves $p^*_K(u)$ generated via this method closely fit the following family of functions:

$$
\begin{align*}
\begin{align*}
p^{*}_{K}(u) \approx 
p^{*'}_{K}(u) =

a\cdot u\cdot \cosh(b\cdot u^c) + d 

  
\end{align*}
\tag{1.3}

\end{align*}
$$

[https://lh4.googleusercontent.com/xuVG7-plz8Webbf0NJP0Ad5G9mvsfHWUklRWgWpIvFF6lhwA_7Vrz1t_47aOxv0Rdzxli02VgWm7TvX0vF2Q1kJr8OmmIBKz7hc_IzUOjdI7uX5hfOihpp2Kzi1rKsqlCZu_PUpA](https://lh4.googleusercontent.com/xuVG7-plz8Webbf0NJP0Ad5G9mvsfHWUklRWgWpIvFF6lhwA_7Vrz1t_47aOxv0Rdzxli02VgWm7TvX0vF2Q1kJr8OmmIBKz7hc_IzUOjdI7uX5hfOihpp2Kzi1rKsqlCZu_PUpA)

A more thorough explanation of the mathematical derivations involved in creating optimal bonding curves is available here: 

## **Kelly Curve clustering**

Each statistical risk model combined with a payoff function can be translated into a Kelly optimal premium curve. Curves produced for multiple instruments and statistical assumptions can be compared and sorted. Below is an example of 50 different insurance pricing curves, for 50 different asset and insurance parameters:

[https://lh3.googleusercontent.com/FsPNFz5wJ1xnVakenPAxeTQlROjDr2oSPedBAF88As4hjefcWV_dRH-wtq5e7sjwKHJ4d3xRIKw-8hJuCYqVHR6kfD59phuRMprKI_gB2rgv2t7apficT6KzHtHXeIBYwOI8rQ5M](https://lh3.googleusercontent.com/FsPNFz5wJ1xnVakenPAxeTQlROjDr2oSPedBAF88As4hjefcWV_dRH-wtq5e7sjwKHJ4d3xRIKw-8hJuCYqVHR6kfD59phuRMprKI_gB2rgv2t7apficT6KzHtHXeIBYwOI8rQ5M)

Consider the following:

*If*

- Risk Instrument A → Optimal Curve A
- Risk Instrument B → Optimal Curve B

*And*

- Optimal Curve B > Optimal Curve A for all utilizations between 0% to 100%

*Then*

- Instrument B more risky than Instrument A
- Growth(pricing A with B) > Growth(pricing A with A)

*therefore*

- expected growth when pricing A and B with B is  higher than when only pricing B with B

On this basis, clusters can be created such that each cluster is denominated by the most expensive curve in it. By doing this, LPs are always pricing risk at Kelly optimal prices *OR ABOVE,* therefore retaining and extending their positive mathematical expectation of survival.

This would be equivalent to the use of “fractional Kelly”, used by risk practitioners to customize Kelly Criterion to fall into “under_betting” conditions.

[LPs can use a single curve to price multiple assets of lower risk](https://lh4.googleusercontent.com/1-XZFLUNNYDLhb-jDUdTKt4hdVhCmmxN4_H2uwLp3Q6M7Yd_8eBqcqA-dUKC4UZ_CTJqdUoKG6g-Lv4PnSekoTS2l4W8ryGHwN9JxymEN3M7c6J5hxZbS1WlexOmx09CiVXe66AI)

LPs can use a single curve to price multiple assets of lower risk

With this technique, the Kelly Machine allows LPs to create pools of capital with a single curve, and sell many different risk instruments from it leading to significant improvements in capital efficiency and market depth.

Simulated Backtests for this and all previous points presented in this section are shown in section 3 of this document.

# 2. Smart contract architecture

The Kelly Machine has the following high level smart contract architecture:

[https://lh6.googleusercontent.com/wjnOEF7dXHduCbgi9aR3WyQ8Ii7IX6mDi1QYMkauuTvTZkqca58K71KyVGICMTVe47OhcnnFYTeGwgyuHzJIczXjtrbVC5U0DO6YIIqx8TZ5o_w6Ql9W2fphX5xqyO4c0nCtxC5l](https://lh6.googleusercontent.com/wjnOEF7dXHduCbgi9aR3WyQ8Ii7IX6mDi1QYMkauuTvTZkqca58K71KyVGICMTVe47OhcnnFYTeGwgyuHzJIczXjtrbVC5U0DO6YIIqx8TZ5o_w6Ql9W2fphX5xqyO4c0nCtxC5l)

- Potion Liquidity Smart Contract holds stablecoin liquidity in pools segregated by LP, each containing a customizable bonding curve parameterization.
- When the correct premium is sent by the buyer, an ERC20 Insurance contract is created using Opyn’s oToken contracts. Buyers can see in their wallet the ownership of the tokenized insurance contract.
- At contract expiry, the Chainlink Oracle is called to retrieve external price information, and payoff is executed.

### **LP Smart Contract Pools**

Each LP manages their capital from an isolated capital pool. In it, each LP can specify the 4 parameters describing the bonding curve, and the list of assets that the pool can price and sell.

[https://lh3.googleusercontent.com/d5Ix7HwY7RoV-9EbEWg2wCpEliNFsNQwwZaMajzi0FV0l4tqGph4FTtKYYUsCJMf0c13yHLG3vvKbQ4M1CjrMNLtCSIVTAGKO_gqQrXNzhgIykU01m4bUIRjFooezrq7o6PcrQwF](https://lh3.googleusercontent.com/d5Ix7HwY7RoV-9EbEWg2wCpEliNFsNQwwZaMajzi0FV0l4tqGph4FTtKYYUsCJMf0c13yHLG3vvKbQ4M1CjrMNLtCSIVTAGKO_gqQrXNzhgIykU01m4bUIRjFooezrq7o6PcrQwF)

Buyers are able to calculate the premiums required for any given insurance contract, by reading on chain the current utilization and the bonding curve of the pool. With this information, the buyer can work out the correct premium to send to the pool for the desired order size.

### **Decentralized Order Book architecture: The emerging bonding curve.**

Since each LP has the ability to specify their unique bonding curve, there will exist a range of prices offered in the market. Through a router running in their browsers, users are able to split their orders into one or multiple LPs in the network, according to their price curves and util levels. The router finds the cheapest available pools, and sends them capital.

[https://lh6.googleusercontent.com/nwISXRoZjnJQl_8EZ1AYRX6OupuwCDxXA2POphplwDBdtQmlIgepOLRly4HclT0KtnCnkzc8RmqU4sdFE3TvxQgzwVWfNrqCllw7EIrwDpEypQBVE7TysyiHe_YiL87vxkif2RP-](https://lh6.googleusercontent.com/nwISXRoZjnJQl_8EZ1AYRX6OupuwCDxXA2POphplwDBdtQmlIgepOLRly4HclT0KtnCnkzc8RmqU4sdFE3TvxQgzwVWfNrqCllw7EIrwDpEypQBVE7TysyiHe_YiL87vxkif2RP-)

Cheaper LPs will get filled first, more expensive LPs last, giving raise to a **decentralized order book**.

From the perspective of the user all LPs together combine into a seemingly single large LP with a single price curve: **the Emergent Bonding Curve (EBC)**, which reflects the aggregated market risk sentiment**.**

### **Gas aware router engine**

The router algorithm is based on the concept of discrete marginal cost. Each pool is discretized into units of collateral, which are priced according to their respective bonding curves. Using a heap algorithm, the router finds the cheapest units of collateral across pools in an iterative process until the total order size is allocated.

[https://lh5.googleusercontent.com/J3kKlUivc_MQFPOtpIaMkBUJa8IZZmYh2n8Xd1pr6KSw4HBEaDrRCWW4iIjCkDdhzgk2uRjJe2qfOUEX4wJqUDOMD917Zc-w2jejFINYRSqkhvNd42EhmBAWBEDaReCe1DzIxRt3](https://lh5.googleusercontent.com/J3kKlUivc_MQFPOtpIaMkBUJa8IZZmYh2n8Xd1pr6KSw4HBEaDrRCWW4iIjCkDdhzgk2uRjJe2qfOUEX4wJqUDOMD917Zc-w2jejFINYRSqkhvNd42EhmBAWBEDaReCe1DzIxRt3)

Gas cost of interacting with new LPs is taken into account by the router in the distribution process, minimizing both the premium and total gas cost in a holistic approach.

# 3. System Backtest

Via Monte Carlo simulation Kelly optimal bonding curves where backtested to measure long term LP capital growth performance. 

Our results show that the backtest result (CAGR) is consistent with the analytically predicted one by Kelly Criterion.

[Intervals of confidence for CAGR as function of util, resulting from Montecarlo simulations of Kelly Machines with Kelly Optimal bonding curves. Each frame represents a different strike of a Bitcoin 7 day duration insurance.](https://lh3.googleusercontent.com/LYW4BGXAfySu3Hi3wzuKcz4gMmsEArz98MOBc3MpP0ZCF5tNXWDtPuWqEd1OtyDRYS6MZ0fjozPED6PE1fU7VrlLnOj8COM3hPN4ECEVDbLsa-GhU-PnaTKYw-6bkIpzFl2sb6kP)

Intervals of confidence for CAGR as function of util, resulting from Montecarlo simulations of Kelly Machines with Kelly Optimal bonding curves. Each frame represents a different strike of a Bitcoin 7 day duration insurance.

We are able to also analyze the drawdown confidence intervals produced in the simulations. These can represent the risk an LP is exposed to:

[https://lh3.googleusercontent.com/7qtMw7jOBuB2uDjYbWyEpXyAkU5VIX2pCmKg_cg-yLs1ESSPoG59xMD8vtVzXI5YOB_Eq_T0fnXWQeEbdiWB_zkuiT4OiqYloWUGcT74HHrwlNrLSpWlCglAOTQ7VExxJzZXjvIC](https://lh3.googleusercontent.com/7qtMw7jOBuB2uDjYbWyEpXyAkU5VIX2pCmKg_cg-yLs1ESSPoG59xMD8vtVzXI5YOB_Eq_T0fnXWQeEbdiWB_zkuiT4OiqYloWUGcT74HHrwlNrLSpWlCglAOTQ7VExxJzZXjvIC)

### **Batch backtesting**

We performed batch backtest for hundreds of assets with different permutations of instrument parameters, market conditions and asset classes. In each simulation risk and reward were monitored. Presented in the graph below, each point is the result of the one instrument backtest:

[https://lh6.googleusercontent.com/P-s0KlnHFEuD7FWLliDyG5kZHYgzwJwru9Ib6C__0YEEGW_v-gcGQG6O7FeWaSDRRJYwfSkmP-ZU3mM-IzJZZ_LAHNxQufOmvGzQXJoLdlvmFEJavaLNRW7mjLsQDsxvtke4Lfs7](https://lh6.googleusercontent.com/P-s0KlnHFEuD7FWLliDyG5kZHYgzwJwru9Ib6C__0YEEGW_v-gcGQG6O7FeWaSDRRJYwfSkmP-ZU3mM-IzJZZ_LAHNxQufOmvGzQXJoLdlvmFEJavaLNRW7mjLsQDsxvtke4Lfs7)

All samples in the simulation have in common positive median CAGR as expected from Kelly Criterion optimization constraints. 

Note that the data (PDF) used for the backtest is the same we’ve used to train the optimal bonding curve. That is why results are “ideal”. Actual performance will depend on how well expected PDF matches actual results. This is further discussed in the estimation error section later in this paper.

### **Black-Scholes Benchmarking**

Backtests were performed on LPs selling insurance on the same instruments priced with perfect volatility (simulated vol = implied vol) in BSM's pricing vs perfect full pdf (simulated pdf = trained pdf) in Kelly's pricing.

An example of results is shown below:

[https://lh5.googleusercontent.com/oB5wzqmQrYtE3I3aY7dv6MlQJVxAjdS3Jtdzu3-rohlWgX2YN0g2sMj3IC-xGbbaA7K9pi2z0t6QSKOqehTGlhnVI8HPMaeDBs8lbjpc74psE69bqO_jX5QdpdIsunkU1eeLbifh](https://lh5.googleusercontent.com/oB5wzqmQrYtE3I3aY7dv6MlQJVxAjdS3Jtdzu3-rohlWgX2YN0g2sMj3IC-xGbbaA7K9pi2z0t6QSKOqehTGlhnVI8HPMaeDBs8lbjpc74psE69bqO_jX5QdpdIsunkU1eeLbifh)

The main driver for Kelly’s superior performance is the fact that Black Scholes assumes an incorrect statistical model for these assets (*Lognormal distribution of prices*). This assumption is incorrect for many markets, and particularly for crypto markets, leading to poor performance including bankruptcy. 

### **Fat tailed asset support**

Unlike BSM, the Kelly Optimization is not limited to a lognormal distribution and instead accepts any information model including fat tailed and power law distribution models.

Below, on the left the bonding curve and simulations for Bitcoin full history empirical distribution.

On the right, the same information model with one additional sample added in: an artificial ‘Black Swan’ (in this case a single extra return sample of -1).

[Upper row: Bonding curves. Lower Row: Simulated LP bankrolls over time.    Left column: Historical model. Right column: Fat tailed historical model.    All: Kelly Machine simulated at 70% utilization, selling Bitcoin insurance of duration 1 month.](https://lh6.googleusercontent.com/iZil8eBS5NYHFZ447YjCLVokHAhKt0JnIjs6ZMAJveKbHyarFy4OlMgdIUp6pYuwaN5bm4mykRpeCZ9VGoeTnfSZtjUVVQwGD8d9Qra8vokH1ceWYzhYhmmL8J_5AC9jTDuoHy8U)

Upper row: Bonding curves. Lower Row: Simulated LP bankrolls over time.    Left column: Historical model. Right column: Fat tailed historical model.    All: Kelly Machine simulated at 70% utilization, selling Bitcoin insurance of duration 1 month.

One simple significant sample completely changes the output of the Kelly Optimization: the curve becomes much more Convex, because now it’s a lot riskier to use high utilization *(one could lose everything if the “-1” comes into play)*. 

This is a simple example of the benefit of using Kelly Bonding Curves as a risk management tool: simulations show that even in simulated black swan environments median growth rate remains positive.

For more information refer to paper: Kelly Optimal bonding curves for fat tailed assets. 

### **Estimation Error Backtest**

In real life conditions, LPs face the risk of overestimating the risk of an asset, and producing expensive curves, or underestimating the risk of an asset, and producing cheap curves.

Below the blue curve is tested against the correct market (yellow), a more bearish market than estimated (red), and a more bullish market than estimated (green).

[https://lh5.googleusercontent.com/Ikm26gNygiyWTG3S-JuuSGAXzHgJp8qSS60UAVLmXXVPvVqNh8guJ8V6YNr1IojZG-RNPHxnQJJ81LNZ0Th3Bm4M7Zn_t_NQvx_35h_iLWNPofTMa0dSD57IRRvY6S7wh4nNtH5q](https://lh5.googleusercontent.com/Ikm26gNygiyWTG3S-JuuSGAXzHgJp8qSS60UAVLmXXVPvVqNh8guJ8V6YNr1IojZG-RNPHxnQJJ81LNZ0Th3Bm4M7Zn_t_NQvx_35h_iLWNPofTMa0dSD57IRRvY6S7wh4nNtH5q)

In order to put a floor to the estimation risk impact, custom bonding curves can be created that cross bull and bear reference market models. This can be used to create a custom risk reward response that anticipates a wide range of mispricing scenarios.

[https://lh3.googleusercontent.com/n-23Y4BelTA13z4Xgm-LISkX426Uwl3UFPSR8JuXCDLN2CMLLPh7Us3KbZg51HiUj7yWwb60NVca1txQUfnCZ3TEcmHEGez68Qf1wC3zWA7I8pkjWTfyH5BKNMJdpxPTWUX1pX_7](https://lh3.googleusercontent.com/n-23Y4BelTA13z4Xgm-LISkX426Uwl3UFPSR8JuXCDLN2CMLLPh7Us3KbZg51HiUj7yWwb60NVca1txQUfnCZ3TEcmHEGez68Qf1wC3zWA7I8pkjWTfyH5BKNMJdpxPTWUX1pX_7)

LPs can use this method to implement multi-weather curves less sensitive to mis-estimations, and more responsive to rapid market sentiment changes.

### **Curve clustering backtest**

We tested an LP selling an equal weight portfolio of several instruments with a single curve.

Below you can see in blue the risk reward of single asset pool performance, vs in red the risk reward of a multi_asset pool. 

[https://lh3.googleusercontent.com/QIs1FsJkZVXU-FdV4rgJCtFR6RUXfw9hr5CfNfab8_TN5jFkdGjQBU-Um3OdYaI4Ih02DuZkDH4yiTkNiwkOHthbsZuzqT44WWHqfNuqH5FzZyj29wG7Z8QCgb8ykvBwmT7V9Vwq](https://lh3.googleusercontent.com/QIs1FsJkZVXU-FdV4rgJCtFR6RUXfw9hr5CfNfab8_TN5jFkdGjQBU-Um3OdYaI4Ih02DuZkDH4yiTkNiwkOHthbsZuzqT44WWHqfNuqH5FzZyj29wG7Z8QCgb8ykvBwmT7V9Vwq)

The historical empirical correlation between assets was used during simulations. Any other correlation model can be backtested.

This assumes constant equal weight of all assets which are ideal conditions, but illustrates nonetheless the directional impact of asset clustering.  

# Summary TL;DR

- The Kelly Criterion can be utilized as a heuristic for market sustainable premium pricing
- Kelly Machine allows automatic trading at Kelly Criterion optimal prices on a decentralized programmable blockchain via Kelly Optimal bonding curves
- Web3 decentralized order book splits orders across LP pools for best price execution for buyers
- Custom curves can be written by LPs to mitigate estimation error and automatically respond to information risk
- Clustering in pools can benefit LP risk adjusted results while increasing capital efficiency and market liquidity
- Montecarlo simulation results match analytical expectations and show positive median long term capital growth
- Opportunity to extend the project via Open source community development

The team performed this research in the spirit of web 3 public goods research in hopes it contributes towards robust automated risk-management for the benefit of all.

# Roadmap

- Expiration_Less insurance
- Auto_Managed pools
- Perpetual Automated portfolio tail risk hedger

## Further reading