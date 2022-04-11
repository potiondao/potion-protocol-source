# Buyers | User Guide

# **Pre-Requisite**

If you have not already done so, please go through [Getting Started](Getting%20St%20f3ba1.md) Section before continuing.

---

Buyers have two Options when buying Potions. Discover Existing Potions or create a new Potion from scratch.

![Untitled](Buyers%20Use%20c2ca5/Untitled.png)

# Option 1 | Discover Potions

This method provides simplicity and economy. Potion Protocol uses [Opyn’s](https://www.opyn.co/) smart contract architecture to create oTokens, these represent a Put Option in Potion Protocol. As these oTokens are already created, the Asset, Strike Price and Duration are already set. In addition, Users can expect a significant gas saving through this flow, as they will not need to create a new oToken on chain, a more complex and expensive transaction. 

****Selecting a Potion****

![Untitled](Buyers%20Use%20c2ca5/Untitled%201.png)

Discover Potions allows Users to browse through the 'Most Purchased' and the 'Most Collateralized' Potions available. Browse the available Potions and select a Potion you would like to buy. You will be presented with the modal window below.

<aside>
<img src="Buyers%20Use%20c2ca5/twitter-logo3.png" alt="Buyers%20Use%20c2ca5/twitter-logo3.png" width="40px" /> Click the pop out link on each Potion card to check out the Potion on Etherscan!

</aside>

## Buying Your Potion

![Untitled](Buyers%20Use%20c2ca5/Untitled%202.png)

Once you have selected the Potion you would like to buy you will be presented with the above modal window. As well as the key information (Asset, Strike, Duration), you can see other useful information like the order book history, gas estimation and price per potion. 
Here you need to decide a couple of things before buying your Potion:

1. **The Quantity of Potions** you want to Purchase -  this depends on your overall strategy and the number of available Potions. 
2.  **The Slippage Tolerance** is the amount of change to the order price you are willing to accept. Due to the nature of the blockchain, this can change slightly between submitting the order and being submitting and the transaction being processed.

Once you are happy with your selection click 'Buy Potion'! You will be asked to confirm the transaction in Metamask. You will see notifications on the progress of your transaction in the dApp and can also view in Etherscan. 

Once your transaction has successfully been processed you will be able to view it in [My Potions](Buyers%20Use%20c2ca5.md).

# Option 2 | Create a Potion

![Untitled](Buyers%20Use%20c2ca5/Untitled%203.png)

If you want to set your own parameters for your Potion, you can also create your own Potion. To begin, click the Create Potion button at the top of the page. You will then be presented with the 'Recipe' view where you will set the parameters for your Potion.

## **Your Put Recipe**

1. **Asset  -** The first step is to choose the underlying asset that you would like to buy your Potion on. This will depend on your overall risk strategy, whether the Potion ends 'In the Money' or 'Out of the Money' will depend on the price of the underlying asset when the Potion expires. Once you have chosen the asset click 'Next'
    
    ![Untitled](Buyers%20Use%20c2ca5/Untitled%204.png)
    
2. **Strike Price -** Now you need to select your strike price, this is the maximum price of the underlying asset at expiration that will result in a payout. A decrease below this price will increase the payout (In the Money). An increase over this price will result in no payout (Out of the Money). The ‘Max Strike Price’ is displayed below, this is the maximum strike price available on the network. Once you have selected your strike, click 'Next'.

![Untitled](Buyers%20Use%20c2ca5/Untitled%205.png)

1. **Duration -** The duration is the number of days until the Potion’s expiration. Again this selection will depend on your overall risk strategy. At the specified date, the Potion will expire and any available payout will be withdrawable. The ‘Max Duration’ is displayed below, this is the maximum duration available on the network. Once you have selected a duration, click 'Next'

![Untitled](Buyers%20Use%20c2ca5/Untitled%206.png)

## Review and Create

![Untitled](Buyers%20Use%20c2ca5/Untitled%207.png)

You now have an opportunity to review your Potion 'recipe' before you create it. On this screen you can see all of your previously selected Parameters. You can also see some additional information that is useful when creating your order.

1. **Choose Quantity** - This is the number of Potions that you want to create. Notice the available potions, this is a limit on the number of potions that you can create as determined by the available liquidity for your selected Recipe. 

2. **Price & Order Total -** This shows you the current price per Potion, the Quantity of Potions that you have selected to order and the total cost of your order. This is always payable in USDC. 

3. **Slippage Tolerance -** Slippage occurs when the Order price changes between the initial order request and the order settlement. This can happen due to the nature of blockchain technology and the block time. Here you will select your Slippage Tolerance, this will be the amount of slippage you are willing to accept and still execute the order. 

4. **Gas Estimation -**  This displays the expected gas cost that you will need to pay in order to send the transaction to the blockchain.

Once you have reviewed and are satisfied with your recipe click 'Create Potion'! You will be asked to confirm the transaction in Metamask. You will see notifications on the progress of your transaction in the dApp and can also view in Etherscan. 

Once your transaction has successfully been processed you will be able to view it in My Potions.

## Similar Potions

![Untitled](Buyers%20Use%20c2ca5/Untitled%208.png)

When creating your Potion, you may have noticed a 'Similar Potions' Panel below. This displays Potions that have a similar 'Recipe' to your creation and already exist on chain. This means that if you buy one of the similar potions you will save on the gas costs associated with creating a new Potion from Scratch. 

To buy one of the similar Potions, hover over the Potion card and select 'Buy Potion'. This will then take you through the same user journey as Discover Potions

# My Potions

If you have not already done so, please go through the Buying Potions Section before continuing.

The My Potions view is where users can view details about Potions they have bought and withdraw any available payout following expiration.

![Untitled](Buyers%20Use%20c2ca5/Untitled%209.png)

## Active Potions

The Active Potions section displays Potions which are yet to expire. As the Expiration date has not past, the payout for an active Potion is Not Withdrawable. However, alongside other key details, you will see a display of the current payout based on the current price of the underlying asset.

![Untitled](Buyers%20Use%20c2ca5/Untitled%2010.png)

## Expired Potions

The Expired Potions Section displays Potions with expiration dates in the past. Each Potion card will display details about the Potion and one of three options:

- **Not Withdrawable -** These Potions expired 'Out of the Money' and therefor have no payout to withdraw.
- **Withdraw -** These Potions expired 'In the Money' and therefor have a payout to withdraw.
- **Already Withdrawn -** This is displayed when you have already withdrawn your payout. The amount of payout withdrawn is also displayed.

![Untitled](Buyers%20Use%20c2ca5/Untitled%2011.png)

## Withdrawing Payout

To withdraw your payout, simply click the 'Withdraw' button. This will trigger your MetaMask to open and you will be asked to approve the transaction. Once the transaction is approved and processed, the funds will be available in your Metamask wallet.

![Untitled](Buyers%20Use%20c2ca5/Untitled%2012.png)