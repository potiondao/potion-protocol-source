# Subgraph Events

The purpose of this document is to describe the changes to different entities when an event emitted by the smart contracts.

## PotionLiquidityPool

### event Deposited(address indexed lp, uint256 indexed poolId, uint256 amount)

If pool does not exist, create an empty pool for that LP using the poolId. Increment the size field by `amount`.

### event Withdrawn(address indexed lp, uint256 indexed poolId, uint256 amount)

Subtract `amount` from LP size. The pool must exist for this event to happen

### event CriteriaSetSelected(address indexed lp, uint256 indexed poolId, bytes32 criteriaSetHash)

Change the criteriaSetHash for the pool. 

### CurveSelected(address indexed lp, uint256 indexed poolId, bytes32 curveHash)

Change the curveHash for the pool.

### OptionsBought(address indexed buyer, address indexed otoken, uint256 numberOfOtokens, uint256 totalPremiumPaid)

Create an empty new BuyerRecord (if one does not exist for the buyer address and oToken address). Then add the number of tokens, and totalPremiumPaid.

Note: Assuming that totalPremiumPaid is in units of the oToken's collateral.

### event OptionsSold(address indexed lp, uint256 indexed poolId, address indexed otoken, bytes32 curveHash, uint256 numberOfOtokens, uint256 liquidityCollateralized, uint256 premiumReceived);

The Pool should have its size increased by `premiumReceived` and have its locked increased by `liquidityCollateralized`.

In addition, if a LPRecord has not been created yet, create an empty one. Then increment liquidityCollateralized, totalLiquidityCollateralized, and premiumReceived.

### OptionSettled(address indexed otoken, uint256 collateralReturned)

(Don't think anything needs to be done here)

### event OptionSettlementDistributed(address indexed otoken, address indexed lp, uint256 indexed poolId, uint256 collateralReturned)

Subtract collateralReturned from each pool's locked liquidity, and subtract it from the liquidityCollateralized for the LPRecord.
