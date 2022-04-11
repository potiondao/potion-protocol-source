# Liquidity Provider | User Guide

## **Pre-Requisite**

If you have not already done so, please go through the [Getting Started](Getting%20St%20f3ba1.md) section before continuing.

## Introduction to LPs

Users can create Pools of liquidity which will insure the selected assets using the parameters that the Liquidity Provider (LP) selects. 

![Untitled](Liquidity%20%204051b/Untitled.png)

Like [Buying a Potion](Buyers%20Use%20c2ca5.md) Users have two paths available to them when providing Liquidity:

# Option 1 | Discover Pools

Users can discover and add liquidity to existing Pool, these have been created by other users and already exist on the blockchain.

This method provides simplicity and economy. As these Pools are already created and the parameters are templated for other users.

## **Selecting a Pool**

![Untitled](Liquidity%20%204051b/Untitled%201.png)

You can browse through the discover pools section to find a pool card that matches the parameters by which you would like to provide liquidity. The pool cards are grouped by 'Most Cloned', 'Largest' and 'Top Gainers'. You can also see which address created the original pool template, so if you know some top LPs you can do a carbon copy of their strategy!

Once you select a pool, click 'View Pool Recipe' to see more details about the pool, such as:

1. The underlying assets to be covered
2. The total liquidity in the pool (USDC)
3. The number of times the pool has been cloned
4. The performance of the pool over time (PnL)
5. Who created the original pool template
6. The Historical Pool Utilisation, Liquidity and PnL.
7. The Premium Bonding Curve for the pool

![Untitled](Liquidity%20%204051b/Untitled%202.png)

![Untitled](Liquidity%20%204051b/Untitled%203.png)

## Adding Liquidity to the Pool

If you like the pool that you have selected, it’s easy to add liquidity and start earning yield. Go to the ‘Add Liquidity’ Section on the right hand side of the screen, enter the amount of liquidity that you wish to add and click the ‘Add Liquidity Button’

![Untitled](Liquidity%20%204051b/Untitled%204.png)

The will trigger a request from Metamask to grant the app access to your funds, once this has been approved you will need to approve the transaction. You will be notified when the transaction has been successfully processed and your Pool will now be available in My Pools!

# Option 2 | Create Pool

If you want to create a fully customised pool for your specific needs, are able to do this using the ‘Create Pool’ tool. To access this, go to the Pool Liquidity section of the application and select ‘Create Pool’ towards the top of the screen. 

![Untitled](Liquidity%20%204051b/Untitled%205.png)

## Pool Setup

The first step is to set up the basic paramaters that your pool is going to insure. 

1. Start by selecting the assets that you want to provide insurance for, you can choose one or multiple assets within the pool. 
2. Select your strike price for each asset, this is the price that at which the option can be exercised by the buyer. 
3. Next select the Max Duration for the insurance, buyers from your pool will not be able to Potions that have a duration longer than this, but note they can buy a shorter duration.
4. Lastly, enter the amount of liquidity that you want to initially put into the pool. Note that these are cash settled options so this will always be in USDC and not the underlying asset.  Then click ‘Next’!

![Untitled](Liquidity%20%204051b/Untitled%206.png)

## Curve Settings

On this screen you will be able to customise the Premium Bonding Curve for the pool. The Premium Bonding Curve (find out more about this [here](https://www.notion.so/Introduction-to-the-Potion-Kelly-Machine-e4f419b0e4e54bbaaedf16310b4bebbe)). 

1. You can set your custom curve parameters using the inputs on the right hand side of the screen. 
2. When the parameters are adjusted you will be able to see your Premium bonding curve update on the chart view.

![Untitled](Liquidity%20%204051b/Untitled%207.png)

## Review and Create

The last screen is where you can review your pool settings before creating it on chain. On this screen you will see:

1. The liquidity that you are providing
2. The underlying assets, max strike and Max duration that you are insuring
3. Your Premium Bonding curve settings
4. The estimated gas cost for creating the pool 

![Untitled](Liquidity%20%204051b/Untitled%208.png)

When you are satisfied with the pool that you have created select ‘Create Pool’. You will be asked to approve the transaction in Metamask and will then receive a notification when the Pool has been created. Once it has been created you can view and manage your Pool in My Pools. 

# My Pools

The ‘My Pools’ screen allows you to view and manage your existing Liquidity Pools.

![Untitled](Liquidity%20%204051b/Untitled%209.png)

To view more details and manage your pool you can select ‘Check Pool’. This view, you can review key performance metrics such as:

Once you select a pool, click 'View Pool Recipe' to see more details about the pool, such as:

- The total liquidity in the pool (USDC)
- The performance of the pool over time (PNL)
- Utilisation

In this view you can also Add and Withdraw Liquidity

![Untitled](Liquidity%20%204051b/Untitled%2010.png)

Once on this page you can see more information about the pool. The chart can display Liquidity, PnL, and utilisation over different time periods. As well as presenting you with additional information, you can add liquidity to this pool using the input box on the right hand side.

## Edit Pool

You can use the ‘Edit Pool’ feature to perform various adjustments and optimisations to your pool. Here you can:

- Add Liquidity
- Change the underlying assets being insured
- Adjust Max Strike and Max Duration
- Adjust the premium bonding curve

![Untitled](Liquidity%20%204051b/Untitled%2011.png)