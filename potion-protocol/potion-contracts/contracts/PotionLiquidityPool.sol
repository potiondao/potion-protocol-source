/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.4;

import {ICurveManager} from "./interfaces/ICurveManager.sol";
import {ICriteriaManager} from "./interfaces/ICriteriaManager.sol";
import {ControllerInterface} from "./packages/opynInterface/OpynControllerInterface.sol";
import {OtokenInterface} from "./packages/opynInterface/OtokenInterface.sol";
import {OtokenFactoryInterface} from "./packages/opynInterface/OtokenFactoryInterface.sol";
import {Actions} from "./packages/opynInterface/ActionsInterface.sol";
import {AddressBookInterface} from "./packages/opynInterface/AddressBookInterface.sol";
import {WhitelistInterface} from "./packages/opynInterface/WhitelistInterface.sol";
import {OracleInterface} from "./packages/opynInterface/OracleInterface.sol";
import {FixedPointInt256 as FPI} from "./packages/opynInterface/FixedPointInt256.sol";
import {OpynActionsLibrary as ActionsLib} from "./OpynActionsLibrary.sol";
import {PausableUpgradeable} from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import {
    IERC20MetadataUpgradeable as ERC20Interface
} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/IERC20MetadataUpgradeable.sol";
import {
    SafeERC20Upgradeable as SafeERC20
} from "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import {IERC20Upgradeable as IERC20} from "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import {PRBMathSD59x18} from "./packages/PRBMathSD59x18.sol";

/**
 * @title PotionLiquidityPool
 * @notice It allows LPs to deposit, withdraw and configure Pools Of Capital. Buyer can buy OTokens.
 */
contract PotionLiquidityPool is PausableUpgradeable, OwnableUpgradeable {
    // This contract performs significant fixed point arithmetic, and uses TWO DIFFERENT maths libraries for that:
    // 1. Whenever we do a calculation that involves an exchange rate (e.g. the ETH price denominated in USDC) we use the same
    //    library as Opyn. This is so that we can more easily compare our code and results to Opyn's, and perhaps replace our
    //    code with theirs if/when they extend their public interfaces.
    // 2. For our more complex premium calculation logic, we make use of the more powerful PRBMathSD59x18 library. This handles
    //    exponentials and logarithms for us. We also use it for util calculations, because utilisations are used as input in
    //    premium calculations.
    using FPI for FPI.FixedPointInt;
    using PRBMathSD59x18 for int256;
    using SafeERC20 for IERC20;

    /// @dev Strike prices from an otoken contract are expressed with 8 decimals
    uint256 internal constant STRIKE_PRICE_DECIMALS = 8;
    /// @dev Oracle prices are always expressed with 8 decimals
    uint256 internal constant ORACLE_PRICE_DECIMALS = 8;
    /// @dev The otoken (ERC20) that tracks option ownership uses 8 decimals for token quantities
    uint256 internal constant OTOKEN_QTY_DECIMALS = 8;

    /// @dev Seconds per day required for calculating option duration in days
    uint256 internal constant SECONDS_IN_A_DAY = 86400;

    /// @dev Max int size for max tvl validation
    uint256 internal constant MAX_INT = 2**256 - 1;

    /**
     * @notice Initialize this implementation contract
     * @dev Function initializer for the upgradeable proxy.
     * @param _opynAddressBook The address of the OpynAddressBook contract.
     * @param _poolCollateralToken The address of the collateral used in this contract.
     * @param _curveManager The address of the CurveManager contract.
     * @param _criteriaManager The address of the CriteriaManager contract.
     */
    function initialize(
        address _opynAddressBook,
        address _poolCollateralToken,
        address _curveManager,
        address _criteriaManager
    ) external initializer {
        __Ownable_init();
        __Pausable_init_unchained();
        sumOfAllUnlockedBalances = 0;
        sumOfAllLockedBalances = 0;
        maxTotalValueLocked = MAX_INT;
        // We interact with multiple Opyn contracts, but each time we do so we go through the
        // Opyn addressbook contrac to identify the address we want to interact with. This means we are
        // robust to the opyn system being upgraded, provided the addressbook remains constant.
        opynAddressBook = AddressBookInterface(_opynAddressBook);

        // One exception: Opyn's addressbook deploys an upgradable proxy in front of its Controller contract, and upgades
        // that proxy to change the controller. As such we save the proxy address here, and avoid the need
        // to go through the addressbook to get to the controller. This saves some gas.
        opynController = ControllerInterface(opynAddressBook.getController());
        vaultCount = opynController.getAccountVaultCounter(address(this));
        poolCollateralToken = IERC20(_poolCollateralToken);
        crv = ICurveManager(_curveManager);
        crit = ICriteriaManager(_criteriaManager);
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Events
    ///////////////////////////////////////////////////////////////////////////

    /// @notice Emits when an LP deposits (initially unlocked) funds into Potion.
    event Deposited(address indexed lp, uint256 indexed poolId, uint256 amount);

    /// @notice Emits when an LP withdraws unlocked funds from Potion.
    event Withdrawn(address indexed lp, uint256 indexed poolId, uint256 amount);

    /// @notice Emits when an LP associates a set of crtieria with a pool of their capital.
    event CriteriaSetSelected(address indexed lp, uint256 indexed poolId, bytes32 criteriaSetHash);

    /// @notice Emits when an LP associates a pricing curve with a pool of their capital.
    event CurveSelected(address indexed lp, uint256 indexed poolId, bytes32 curveHash);

    /// @notice Emits once per purchase, with details of the buyer and the aggregate figures involved.
    event OptionsBought(
        address indexed buyer,
        address indexed otoken,
        uint256 numberOfOtokens,
        uint256 totalPremiumPaid
    );

    /// @notice Emits for every LP involved in collateralizing a purchase, with details of the LP and the figures involved in their part of the purchase.
    event OptionsSold(
        address indexed lp,
        uint256 indexed poolId,
        address indexed otoken,
        bytes32 curveHash,
        uint256 numberOfOtokens,
        uint256 liquidityCollateralized,
        uint256 premiumReceived
    );

    /// @notice Emits when all collateral for a given otoken (which must have reached expiry) is reclaimed from the Opyn contracts, into this Potion contract.
    event OptionSettled(address indexed otoken, uint256 collateralReturned);

    /// @notice Emits every time that some collateral (preciously reclaimed from the Opyn conracts into this Potion contract) is redistributed to one of the collateralising LPs.
    event OptionSettlementDistributed(
        address indexed otoken,
        address indexed lp,
        uint256 indexed poolId,
        uint256 collateralReturned
    );

    ///////////////////////////////////////////////////////////////////////////
    //  Structs and vars
    ///////////////////////////////////////////////////////////////////////////

    /// @dev A VaultInfo contains the data about a single Opyn Vault.
    struct VaultInfo {
        uint256 vaultId; // the vault's ID in Opyn's contracts. Valid vaultIDs start at 1, so this can be used as an existence check in a map
        uint256 totalContributions; // The total contributed to the vault by Potion LPs, denominated in collateral tokens
        bool settled; // Whether the vault has been settled. That is, whether the unused collateral has, after otoken expiry, been reclaimed from the Opyn contracts into this contract
        uint256 settledAmount; // The amount of unused collateral that was reclaimed from the Opyn contracts upon settlement
        mapping(address => mapping(uint256 => uint256)) contributionsByLp; // The vault contributions, denominated in collateral tokens, indexed by LP and then by the LP's poolId
    }

    /// @dev The keys required to identify a given pool of capital in the lpPools map.
    struct PoolIdentifier {
        address lp;
        uint256 poolId;
    }

    /// @dev The data associated with a given pool of capital, belonging to one LP
    struct PoolOfCapital {
        uint256 total; // The total (locked or unlocked) of capital in the pool, denominated in collateral tokens
        uint256 locked; // The locked capital in the pool, denominated in collateral tokens
        bytes32 curveHash; // Identifies the curve to use when pricing the premiums charged for any otokens sold (& collateralizated) by this pool
        bytes32 criteriaSetHash; // Identifies the set of otokens that this pool is willing to sell (& collateralize)
    }

    /// @dev The counterparty data associated with a given (tranche of an) otoken purchase. For gas efficiency reasons, the buyer must pass in details of the curve and criteria, and these are verified as a match (rather than calculated) on-chain
    struct CounterpartyDetails {
        address lp; // The LP to buy from
        uint256 poolId; // The pool (belonging to LP) that will colalteralize the otoken
        ICurveManager.Curve curve; // The curve used to calculate the otoken premium
        ICriteriaManager.Criteria criteria; // The criteria associated with this curve, which matches the otoken
        uint256 orderSizeInOtokens; // The number of otokens to buy from this particular counterparty
    }

    /// @dev Used only internally, in memory, to track aggregate values across an order involving multiple LPs. This reduces the number of local variables and thereby avoids a "stack too deep" error at compile time.
    struct AggregateOrderData {
        uint256 premium;
        uint256 collateral;
        uint256 orderSize;
    }

    /// @dev Used only internally, in memory, to track parameters involved in calculating collateral requirements. This reduces the number of local variables and thereby avoids a "stack too deep" error at compile time.
    struct CollateralCalculationParams {
        bool collateralMatchesStrike; // true iff the collateral asset and the strike asset are the same (this simplifies the calculation)
        FPI.FixedPointInt strikePrice; // The strike asset price returned by the oracle, in the FixedPointInt representation of decimal numbers
        FPI.FixedPointInt collateralPrice; // The collateral asset price returned by the oracle, in the FixedPointInt representation of decimal numbers
        FPI.FixedPointInt otokenStrikeHumanReadable; // The strike price denominated in strike tokens, in human readable notation (e.g. if strike = 300USDC, this is "300.0" not "300000000"
        uint256 collateralTokenDecimals; // The number of decimals used by the collateral token (may differ from the strike token)
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Contract state
    ///////////////////////////////////////////////////////////////////////////

    /// @dev The maximum value (denominated in collateral tokens) that can be custodied by this contract, or by Opyn on behalf of this contract
    // (i.e. including locked and unlocked balances across all pools of capital).
    uint256 public maxTotalValueLocked;

    /// @dev The number of Opyn vaults that this contract has ever opened
    uint256 public vaultCount;

    /// @dev One Potion vault per token, indexed by otoken address. We know that this map only contains entries for whitelisted (or previously whitelisted) otokens, because we check before creating entries.
    mapping(address => VaultInfo) internal vaults;

    /// @dev Data about pools of capital, indexed first by LP address and then by an (arbitrary) numeric poolId
    mapping(address => mapping(uint256 => PoolOfCapital)) public lpPools;

    /// @dev The aggregate amount of capital currently unlocked in this contract by LPs. Denominated in collateral tokens. This is used for some safety checks, and could theoretically be removed at a later date to reduce gas costs.
    uint256 public sumOfAllUnlockedBalances;

    /// @dev The aggregate amount of capital currently deposited locked in this contract by LPs. Denominated in collateral tokens. This is used for some safety checks, and could theoretically be removed at a later date to reduce gas costs.
    uint256 public sumOfAllLockedBalances;

    // All Opyn contracts are trusted => we assume there is no malicious code within Opyn contracts.
    /// @dev If we want to interact with the Opyn Controller, we already know the address of its transparent proxy. This contract is trusted.
    ControllerInterface public opynController;
    /// @dev If we want to interact with any other Opyn contract, we look up its address in the addressbook. All Opyn contracts are trusted.
    AddressBookInterface public opynAddressBook;

    /// @dev The curve manager is used to manage curves, and curve hashes, and the calculation of prices based on curves.
    ICurveManager public crv;

    /// @dev The criteria manager is used to manage criteria, and sets of criteria, and hashes thereof
    ICriteriaManager public crit;

    /// @dev Currently we support only a single token as collateral. The easiest route to supporting multiple types of collateral may be multiple instances of the PotionLiquidityPool contract. The collateral token is chosen carefully and is therefore probably to be trusted, but we nevertheless attempt to interact with it at the _end_ of each transaction to reduce the scope for re-entrancy attacks!
    IERC20 public poolCollateralToken;

    ///////////////////////////////////////////////////////////////////////////
    //  Admin (owner) functions
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Set the total max value locked per user in a Pool of Capital.
     * @param _newMax The new total max value locked.
     */
    function setMaxTotalValueLocked(uint256 _newMax) external onlyOwner whenNotPaused {
        maxTotalValueLocked = _newMax;
    }

    /**
     * @notice Allows the admin to pause the whole system
     */
    function pause() external onlyOwner whenNotPaused {
        _pause();
    }

    /**
     * @notice Allows the admin to unpause the whole system
     */
    function unpause() external onlyOwner whenPaused {
        _unpause();
    }

    /**
     * @notice Update the contract used to manage curves, and curve hashes, and the calculation of prices based on curves
     * @dev To ensure continued operation for all users, any new CurveManager must be pre-populated with the same data as the existing CurveManager (for reasons of gas efficiency, we do not use an upgradable proxy mechanism)
     * @dev The `CurveManager` can be changed while paused, in case this is required to address security issues
     * @param _new The new address of the CurveManager
     */
    function setCurveManager(ICurveManager _new) external onlyOwner {
        crv = _new;
    }

    /**
     * @notice Update the contract used to manage criteria, and sets of criteria, and hashes thereof
     * @dev Note To ensure continued operation for all users, any new CriteriaManager must be pre-populated with the same data as the existing CriteriaManager (for reasons of gas efficiency, we do not use an upgradable proxy mechanism)
     * @dev The `CriteriaManager` can be changed while paused, in case this is required to address security issues
     * @param _new The new address of the CriteriaManager
     */
    function setCriteriaManager(ICriteriaManager _new) external onlyOwner {
        crit = _new;
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Getters & view functions
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Get the ID of the existing Opyn vault that Potion uses to collateralize a given OToken.
     * @param _otoken The identifier (token contract address) of the OToken. Not checked for validity in this view function.
     * @return The unique ID of the vault, > 0. If no vault exists, the returned value will be 0
     */
    function getVaultId(OtokenInterface _otoken) public view returns (uint256) {
        return vaults[address(_otoken)].vaultId;
    }

    /**
     * @notice Query the locked capital in a specified pool of capital
     * @dev _poolId is generated in the client side.
     * @param _lp The address of the liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @return The amount of capital locked in the pool, denominated in collateral tokens.
     */
    function lpLockedAmount(address _lp, uint256 _poolId) external view returns (uint256) {
        return lpPools[_lp][_poolId].locked;
    }

    /**
     * @notice Query the total capital (locked + unlocked) in a specified pool of capital.
     * @param _lp The address of the liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @return The amount of capital in the pool, denominated in collateral tokens.
     */
    function lpTotalAmount(address _lp, uint256 _poolId) external view returns (uint256) {
        return lpPools[_lp][_poolId].total;
    }

    /**
     * @notice The amount of capital required to collateralize a given quantitiy of a given OToken.
     * @param _otoken The identifier (token contract address) of the OToken to be collateralized. Not checked for validity in this view function.
     * @param _otokenQty The number of OTokens we wish to collateralize.
     * @return The amount of collateral required, denominated in collateral tokens.
     */
    function collateralNeededForPuts(OtokenInterface _otoken, uint256 _otokenQty) external view returns (uint256) {
        CollateralCalculationParams memory collateralCalcParams;
        (address collateralAsset, , address strikeAsset, uint256 strikePrice, , ) = _otoken.getOtokenDetails();
        (
            collateralCalcParams.collateralMatchesStrike,
            collateralCalcParams.strikePrice,
            collateralCalcParams.collateralPrice
        ) = _getLivePrices(strikeAsset, collateralAsset);
        collateralCalcParams.otokenStrikeHumanReadable = FPI.fromScaledUint(strikePrice, OTOKEN_QTY_DECIMALS);
        collateralCalcParams.collateralTokenDecimals = ERC20Interface(collateralAsset).decimals();
        return _collateralNeededForPuts(_otokenQty, collateralCalcParams);
    }

    /**
     * @notice Calculate the premiums for a particular OToken from the provided sellers.
     * @param _otoken The `OToken` for which we calculate the premium charged for a purchase. This is not checked for validity in this view function, nor is it checked for compatibility with sellers.
     * @param _sellers The details of the counterparties and counterparty pricing, for which we calculate the premiums. These are assumed (not checked) to be compatibile with the `Otoken`.
     * @return totalPremiumInCollateralTokens The total premium in collateral tokens.
     * @return perLpPremiumsInCollateralTokens The premiums per LP in collateral tokens, ordered in the same way as the `_sellers` param.
     */
    function premiums(OtokenInterface _otoken, CounterpartyDetails[] memory _sellers)
        external
        view
        returns (uint256 totalPremiumInCollateralTokens, uint256[] memory perLpPremiumsInCollateralTokens)
    {
        perLpPremiumsInCollateralTokens = new uint256[](_sellers.length);

        (address collateralAsset, , address strikeAsset, uint256 strikePrice, , ) = _otoken.getOtokenDetails();
        CollateralCalculationParams memory collateralCalcParams;
        (
            collateralCalcParams.collateralMatchesStrike,
            collateralCalcParams.strikePrice,
            collateralCalcParams.collateralPrice
        ) = _getLivePrices(strikeAsset, collateralAsset);
        collateralCalcParams.otokenStrikeHumanReadable = FPI.fromScaledUint(strikePrice, OTOKEN_QTY_DECIMALS);
        collateralCalcParams.collateralTokenDecimals = ERC20Interface(collateralAsset).decimals();

        // This loop is unbounded. If it runs outof gas that's because the buyer is trying to buy from too many different pools
        // It is the responsibility of the router to not route buyers to too many pools in a singel transaction
        for (uint256 i = 0; i < _sellers.length; i++) {
            CounterpartyDetails memory seller = _sellers[i];
            uint256 collateralRequired = _collateralNeededForPuts(seller.orderSizeInOtokens, collateralCalcParams);
            uint256 premium = _premiumForLp(seller.lp, seller.poolId, seller.curve, collateralRequired);
            perLpPremiumsInCollateralTokens[i] = premium;
            totalPremiumInCollateralTokens = totalPremiumInCollateralTokens + premium;
        }
        return (totalPremiumInCollateralTokens, perLpPremiumsInCollateralTokens);
    }

    /**
     * @notice Calculates the utilization before and after locking new collateral amount.
     * @param _lp The address of the liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @param _collateralToLock The amount of collateral to lock.
     * @return utilBeforeAs59x18 Utilization before locking the collateral specified.
     * @return utilAfterAs59x18 Utilization after locking the collateral specified.
     * @return lockedAmountBefore The total collateral locked before locking the collateral specified.
     * @return lockedAmountAfter The total collateral locked after locking the collateral specified.
     */
    function util(
        address _lp,
        uint256 _poolId,
        uint256 _collateralToLock
    )
        public
        view
        returns (
            int256 utilBeforeAs59x18,
            int256 utilAfterAs59x18,
            uint256 lockedAmountBefore,
            uint256 lockedAmountAfter
        )
    {
        PoolOfCapital storage bal = lpPools[_lp][_poolId];
        lockedAmountBefore = bal.locked;
        lockedAmountAfter = bal.locked + _collateralToLock;
        require(lockedAmountAfter <= bal.total, "util calc: >100% locked");
        require(bal.total > 0, "util calc: 0 balance");

        // Note that the use of fromUint here implies a max total balance in any pool of ~5.8e+58 wei.
        // This is 5.8e+40 human units if the collateral token uses 18 decimals
        utilBeforeAs59x18 = PRBMathSD59x18.fromUint(lockedAmountBefore).div(PRBMathSD59x18.fromUint(bal.total));
        utilAfterAs59x18 = PRBMathSD59x18.fromUint(lockedAmountAfter).div(PRBMathSD59x18.fromUint(bal.total));

        return (utilBeforeAs59x18, utilAfterAs59x18, lockedAmountBefore, lockedAmountAfter);
    }

    /**
     * @notice The specified OToken's strike price as a percentage of the current market spot price.
     * @dev In-The-Money put options will return a value > 100; Out-Of-The-Money put options will return a value <= 100.
     * @param _otoken The identifier (token contract address) of the OToken to get the strike price. Not checked for validity in this view function.
     * @return The strike price as a percentage of the current price, rounded up to an integer percentage.
     *         E.g. if current price is $100, then a strike price of $94.01 returns a strikePercent of 95,
     *         and a strike price of $102.99 returns a strikePercent of 103.
     */
    function percentStrike(OtokenInterface _otoken) public view returns (uint256) {
        // strikePrice() returns a value that assumes 8 digits (i.e. human readable value * 10^8), regardless of the decimals used by any other token
        (, address underlyingAsset, address strikeAsset, uint256 strikePrice, , ) = _otoken.getOtokenDetails();
        uint256 strikePriceInStrikeTokensTimes10e8 = strikePrice;

        // Get the spot prices of the underlying and strike assets
        (, FPI.FixedPointInt memory underlyingPrice, FPI.FixedPointInt memory strikeTokenPrice) =
            _getLivePrices(underlyingAsset, strikeAsset);
        assert(underlyingPrice.value > 0);
        assert(strikeTokenPrice.value > 0);
        FPI.FixedPointInt memory spotPriceInStrikeTokensAsDecimal = underlyingPrice.div(strikeTokenPrice);
        uint256 spotPriceInStrikeTokensTimes10e8 =
            spotPriceInStrikeTokensAsDecimal.toScaledUint(ORACLE_PRICE_DECIMALS, false);

        // To get the strike as a percentage of the spot price, we want to use the same units for both the
        // numerator and the denominator when calculating:
        //    (strikeTokenPrice * 100) / spotPrice
        //
        // Here we add (denominator -1) to the numerator before dividing, to ensure that we round up
        return
            ((strikePriceInStrikeTokensTimes10e8 * 100) + spotPriceInStrikeTokensTimes10e8 - 1) /
            spotPriceInStrikeTokensTimes10e8;
    }

    /**
     * @notice It calculates the number of days (including all partial days) until the specified Otoken expires.
     * @dev reverts if the otoken already expired
     * @param _otoken The identifier (address) of the Otoken. Not checked for validity in this view function.
     * @return The number of days remaining until OToken expiry, rounded up if necessary to make to an integer number of days.
     */
    function durationInDays(OtokenInterface _otoken) public view returns (uint256) {
        uint256 expiry = _otoken.expiryTimestamp();
        require(expiry > block.timestamp, "Otoken has expired");
        uint256 duration = expiry - block.timestamp;
        // To round up the answer, we add SECONDS_IN_A_DAY-1 before we divide
        return (duration + SECONDS_IN_A_DAY - 1) / SECONDS_IN_A_DAY;
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Public interface
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Create an Opyn vault, which Potion will use to collateralize a given OToken.
     * @dev `_otoken` is implicitly checked for validity when we call `_getOrCreateVaultInfo`.
     * @param _otoken The identifier (token contract address) of the OToken.
     * @return The unique ID of the vault, > 0.
     */
    function createNewVaultId(OtokenInterface _otoken) external whenNotPaused returns (uint256) {
        require(getVaultId(_otoken) == 0, "Vault already exists");
        return _getOrCreateVaultInfo(_otoken).vaultId;
    }

    /**
     * @notice Deposit collateral tokens from the sender into the specified pool belonging to the caller.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _amount The amount of collateral tokens to deposit.
     */
    function deposit(uint256 _poolId, uint256 _amount) public whenNotPaused {
        if (_amount > 0) {
            _credit(msg.sender, _poolId, _amount);
            poolCollateralToken.safeTransferFrom(msg.sender, address(this), _amount);
            assert(poolCollateralToken.balanceOf(address(this)) >= sumOfAllUnlockedBalances);
            emit Deposited(msg.sender, _poolId, _amount);
        }
    }

    /**
     * @notice Deposit collateral tokens from the sender into the specified pool belonging to the caller and configures the Curve and CriteriaSet.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _amount The amount of collateral tokens to deposit.
     * @param _curveHash The hash of the new Curve to be set in the specified pool.
     * @param _criteriaSetHash The hash of the new CriteriaSet to be set in the specified pool.
     */
    function depositAndConfigurePool(
        uint256 _poolId,
        uint256 _amount,
        bytes32 _curveHash,
        bytes32 _criteriaSetHash
    ) external whenNotPaused {
        setCurve(_poolId, _curveHash);
        setCurveCriteria(_poolId, _criteriaSetHash);

        // We deposit last as this involves an external call, albeit to a trusted collateral token
        deposit(_poolId, _amount);
    }

    /**
     * @notice Set the "set of criteria" associated with a given pool of capital. These criteria will be used to determine which otokens this pool of capital is prepared to collateralize. If any Criteria in the set is a match, then the otoken can potentially be colalteralized by this pool of capital, subject to the premium being paid and sufficient liquidity being available.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _criteriaSetHash The hash of the immutable CriteriaSet to be associated with this PoolOfCapital.
     */
    function setCurveCriteria(uint256 _poolId, bytes32 _criteriaSetHash) public whenNotPaused {
        // Allow setting criteriaSet = 0x000... to indicate that this capital is not available for use
        require(_criteriaSetHash == bytes32(0) || crit.isCriteriaSetHash(_criteriaSetHash), "No such criteriaSet");
        if (lpPools[msg.sender][_poolId].criteriaSetHash != _criteriaSetHash) {
            lpPools[msg.sender][_poolId].criteriaSetHash = _criteriaSetHash;
            emit CriteriaSetSelected(msg.sender, _poolId, _criteriaSetHash);
        }
    }

    /**
     * @notice Set the curve associated with a given pool of capital. The curve will be used to price the premiums charged for any otokens that this pool of capital is prepared to collateralize.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _curveHash The hash of the immutable Curve to be associated with this PoolOfCapital.
     */
    function setCurve(uint256 _poolId, bytes32 _curveHash) public whenNotPaused {
        require(crv.isKnownCurveHash(_curveHash), "No such curve");
        if (lpPools[msg.sender][_poolId].curveHash != _curveHash) {
            lpPools[msg.sender][_poolId].curveHash = _curveHash;
            emit CurveSelected(msg.sender, _poolId, _curveHash);
        }
    }

    /**
     * @notice Withdraw unlocked collateral tokens from the specified pool belonging to the caller, and send them to the caller's address.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _amount The amount of collateral tokens to withdraw.
     */
    function withdraw(uint256 _poolId, uint256 _amount) external whenNotPaused {
        if (_amount > 0) {
            _debit(msg.sender, _poolId, _amount);
            poolCollateralToken.safeTransfer(msg.sender, _amount);
            assert(poolCollateralToken.balanceOf(address(this)) >= sumOfAllUnlockedBalances);
            emit Withdrawn(msg.sender, _poolId, _amount);
        }
    }

    /**
     * @notice Creates a new otoken, and then buy it from the specified list of sellers.
     * @param _underlyingAsset A property of the otoken that is to be created.
     * @param _strikeAsset A property of the otoken that is to be created.
     * @param _collateralAsset A property of the otoken that is to be created.
     * @param _strikePrice A property of the otoken that is to be created.
     * @param _expiry A property of the otoken that is to be created.
     * @param _isPut A property of the otoken that is to be created.
     * @param _sellers The LPs to buy the new otokens from. These LPs will charge a premium to collateralize the otoken.
     * @param _maxPremium The maximum premium that the buyer is willing to pay, denominated in collateral tokens (wei) and aggregated across all sellers
     * @return premium The total premium paid.
     */
    function createAndBuyOtokens(
        address _underlyingAsset,
        address _strikeAsset,
        address _collateralAsset,
        uint256 _strikePrice,
        uint256 _expiry,
        bool _isPut,
        CounterpartyDetails[] memory _sellers,
        uint256 _maxPremium
    ) external whenNotPaused returns (uint256 premium) {
        require(_collateralAsset == address(poolCollateralToken), "Potion: wrong collateral token");
        OtokenFactoryInterface otokenFactory = OtokenFactoryInterface(opynAddressBook.getOtokenFactory());
        address otoken =
            otokenFactory.createOtoken(_underlyingAsset, _strikeAsset, _collateralAsset, _strikePrice, _expiry, _isPut);
        return buyOtokens(OtokenInterface(otoken), _sellers, _maxPremium);
    }

    /**
     * @notice Buy a OTokens from the specified list of sellers.
     * @dev `_otoken` is implicitly checked for validity when we call `_getOrCreateVaultInfo`.
     * @param _otoken The identifier (address) of the OTokens being bought.
     * @param _sellers The LPs to buy the new OTokens from. These LPs will charge a premium to collateralize the otoken.
     * @param _maxPremium The maximum premium that the buyer is willing to pay, denominated in collateral tokens (wei) and aggregated across all sellers
     * @return premium The aggregated premium paid.
     */
    function buyOtokens(
        OtokenInterface _otoken,
        CounterpartyDetails[] memory _sellers,
        uint256 _maxPremium
    ) public whenNotPaused returns (uint256 premium) {
        AggregateOrderData memory runningTotals;
        VaultInfo storage vault = _getOrCreateVaultInfo(_otoken);

        // We have some info about the otoken that we read for every seller. Get it once and cache it.
        ICriteriaManager.OtokenProperties memory otokenCache;
        address collateralAsset;
        uint256 otokenStrikePrice;
        (
            collateralAsset,
            otokenCache.underlyingAsset,
            otokenCache.strikeAsset,
            otokenStrikePrice,
            ,
            otokenCache.isPut
        ) = _otoken.getOtokenDetails();
        IERC20 collateralToken = IERC20(collateralAsset);

        // For now, only puts are supported and only with one collateral token
        require(collateralToken == poolCollateralToken, "Potion: wrong collateral token");
        require(otokenCache.isPut, "Potion: otoken not a put");

        // Getting the durationInDays implicitly asserts that the otoken has not yet expired
        otokenCache.percentStrikeValue = percentStrike(_otoken);
        otokenCache.wholeDaysRemaining = durationInDays(_otoken);

        // We need the price ratio, strike price, and the decimals used by the collateral token, but we
        // can get these once rather than once-per-seller
        CollateralCalculationParams memory collateralCalcParams;
        (
            collateralCalcParams.collateralMatchesStrike,
            collateralCalcParams.strikePrice,
            collateralCalcParams.collateralPrice
        ) = _getLivePrices(otokenCache.strikeAsset, collateralAsset);
        collateralCalcParams.otokenStrikeHumanReadable = FPI.fromScaledUint(otokenStrikePrice, OTOKEN_QTY_DECIMALS);
        collateralCalcParams.collateralTokenDecimals = ERC20Interface(collateralAsset).decimals();

        // Iterate through sellers, doing checks and optimistically updating with assumption that transaction will succeed
        // This loop is unbounded. If it runs outof gas that's because the buyer is trying to buy from too many different pools
        // It is the responsibility of the router to not route buyers to too many pools in a singel transaction
        require(_sellers.length > 0, "Can't buy from no sellers");

        for (uint256 i = 0; i < _sellers.length; i++) {
            CounterpartyDetails memory seller = _sellers[i];
            bytes32 curveHash = crv.hashCurve(seller.curve);
            require(seller.orderSizeInOtokens > 0, "Order tranche is zero");
            require(crv.isKnownCurveHash(curveHash), "No such curve");
            require(curveHash == lpPools[seller.lp][seller.poolId].curveHash, "Invalid curve");
            require(
                crit.isInCriteriaSet(
                    lpPools[seller.lp][seller.poolId].criteriaSetHash,
                    crit.hashCriteria(seller.criteria)
                ),
                "Invalid criteria hash"
            );

            // Check that the token matches the LP's criteria
            require(seller.criteria.underlyingAsset == otokenCache.underlyingAsset, "wrong underlying token");
            require(seller.criteria.strikeAsset == otokenCache.strikeAsset, "wrong strike token");
            require(seller.criteria.isPut == otokenCache.isPut, "call options not supported");
            require(seller.criteria.maxStrikePercent >= otokenCache.percentStrikeValue, "invalid strike%");
            require(seller.criteria.maxDurationInDays >= otokenCache.wholeDaysRemaining, "invalid duration");

            (uint256 latestPremium, uint256 latestCollateral) =
                _initiatePurchaseAndUpdateFundsForOneLP(seller, collateralCalcParams);
            runningTotals.premium = runningTotals.premium + latestPremium;
            runningTotals.orderSize = runningTotals.orderSize + seller.orderSizeInOtokens;
            runningTotals.collateral = runningTotals.collateral + latestCollateral;
            vault.contributionsByLp[seller.lp][seller.poolId] =
                vault.contributionsByLp[seller.lp][seller.poolId] +
                latestCollateral;
            emit OptionsSold(
                seller.lp,
                seller.poolId,
                address(_otoken),
                curveHash,
                seller.orderSizeInOtokens,
                latestCollateral,
                latestPremium
            );
        }

        require(runningTotals.premium <= _maxPremium, "Premium higher than max");
        collateralToken.safeIncreaseAllowance(opynAddressBook.getMarginPool(), runningTotals.collateral);

        // Calling into Opyn implicitly checks that the otoken is valid (e.g. not a dummy token, and not expired)
        vault.totalContributions = vault.totalContributions + runningTotals.collateral;
        Actions.ActionArgs[] memory opynActions =
            ActionsLib._actionArgsToDepositCollateralAndMintOtokens(
                vault.vaultId,
                _otoken,
                address(collateralToken),
                runningTotals.collateral,
                runningTotals.orderSize
            );
        opynController.operate(opynActions);

        // Transfer colateral at the end, just in case collateral token is malicious (but if it is we are probably screwed for other reasons!)
        collateralToken.safeTransferFrom(msg.sender, address(this), runningTotals.premium);
        assert(poolCollateralToken.balanceOf(address(this)) >= sumOfAllUnlockedBalances);
        emit OptionsBought(msg.sender, address(_otoken), runningTotals.orderSize, runningTotals.premium);
        return runningTotals.premium;
    }

    /**
     * @notice Retrieve unused collateral from Opyn into this contract. Does not redistribute it to our (unbounded number of) LPs
     * @dev `_otoken` is implicitly checked for validity when we call `_getVaultInfo`.
     * Redistribution can be done by calling redistributeSettlement(addresses).
     * @param _otoken The identifier (address) of the expired OToken for which unused collateral should be retrieved.
     */
    function settleAfterExpiry(OtokenInterface _otoken) public whenNotPaused {
        VaultInfo storage v = _getVaultInfo(_otoken);
        require(!v.settled, "Vault already settled");

        // Success or revert
        v.settled = true;

        require(opynController.isSettlementAllowed(address(_otoken)), "Otoken cannot (yet) settle");

        // Get the settled amount of collateral
        v.settledAmount = opynController.getProceed(address(this), v.vaultId);

        if (v.settledAmount > 0) {
            Actions.ActionArgs[] memory openVaultActions = new Actions.ActionArgs[](1);
            openVaultActions[0] = ActionsLib._getSettleVaultAction(address(this), v.vaultId, address(this));
            opynController.operate(openVaultActions);

            emit OptionSettled(address(_otoken), v.settledAmount);
        }
    }

    /**
     * @notice Calculates the outstading settlement from the PoolIdentifier in OTokens.
     * @dev Redistribution can be done by calling redistributeSettlement(addresses).
     * @dev `_otoken` is implicitly checked for validity when we call `_getVaultInfo`.
     * @param _otoken The identifier (address) of the expired OToken for which unused collateral should be retrieved.
     * @param _pool The pool information which the outstanding settlement is calculated.
     * @return collateralDueBack The amount of collateral that can be removed from a vault.
     */
    function outstandingSettlement(OtokenInterface _otoken, PoolIdentifier calldata _pool)
        public
        view
        returns (uint256 collateralDueBack)
    {
        VaultInfo storage v = _getVaultInfo(_otoken);
        uint256 contribution = v.contributionsByLp[_pool.lp][_pool.poolId];
        if (v.totalContributions == 0 || contribution == 0) {
            return 0;
        }

        if (isSettled(_otoken)) {
            return (v.settledAmount * contribution) / v.totalContributions;
        } else {
            uint256 settledAmount = opynController.getProceed(address(this), v.vaultId);
            // Round down, so that we never over-pay
            return (settledAmount * contribution) / v.totalContributions;
        }
    }

    /**
     * @notice Check whether a give OToken has been settled.
     * @dev Settled OTokens may not have had funds redistributed to all (or any) contributing LPs.
     * @dev `_otoken` is implicitly checked for validity when we call `_getVaultInfo`.
     * @param _otoken the (settled or unsettled) OToken.
     * @return True if it is settled, otherwise false
     */
    function isSettled(OtokenInterface _otoken) public view returns (bool) {
        VaultInfo storage v = _getVaultInfo(_otoken);
        return v.settled;
    }

    /**
     * @notice Redistribute already-retrieved collateral amongst the specified pools. This function must be called after settleAfterExpiry.
     * @dev If the full list of PoolIdentifiers owed funds is too long, a partial list can be provided and additional calls to redistributeSettlement() can be made.
     * @dev `_otoken` is implicitly checked for validity when we call `_getVaultInfo`.
     * @param _otoken The identifier (address) of the settled otoken for which retrieved collateral should be redistributed.
     * @param _pools The pools of capital to which the collateral should be redistributed. These pools must be (a subset of) the pools that provided collateral for the specified otoken.
     */
    function redistributeSettlement(OtokenInterface _otoken, PoolIdentifier[] calldata _pools) public whenNotPaused {
        VaultInfo storage v = _getVaultInfo(_otoken);
        require(v.settled, "Vault not yet settled");

        // This loop is unbounded. If it runs out of gas that's because the caller is trying to redistribute
        // funds to too many LPs in one transaction. In that case, the caller can retry with smaller lists
        // (perhaps spreading the long list of LPs across more than one transaction).
        for (uint256 i = 0; i < _pools.length; i++) {
            PoolIdentifier calldata p = _pools[i];
            if (v.contributionsByLp[p.lp][p.poolId] == 0) {
                continue;
            }

            // Round down, so that we never over-pay
            uint256 amountToCredit = (v.settledAmount * v.contributionsByLp[p.lp][p.poolId]) / v.totalContributions;
            _burnLocked(p.lp, p.poolId, v.contributionsByLp[p.lp][p.poolId] - amountToCredit);
            _unlock(p.lp, p.poolId, amountToCredit);
            v.contributionsByLp[p.lp][p.poolId] = 0;
            emit OptionSettlementDistributed(address(_otoken), p.lp, p.poolId, amountToCredit);
        }

        // Check we've not allocated more than we had to give
        assert(poolCollateralToken.balanceOf(address(this)) >= sumOfAllUnlockedBalances);
    }

    /**
     * @notice Retrieve unused collateral from Opyn, and redistribute it to the specified LPs.
     * @dev If the full list of PoolIdentifiers owed funds is too long, a partial list can be provided and additional calls to redistributeSettlement() can be made.
     * @dev `_otoken` is implicitly checked for validity when we call `settleAfterExpiry`.
     * @param _otoken The identifier (address) of the expired otoken for which unused collateral should be retrieved.
     * @param _pools The pools of capital to which the collateral should be redistributed. These pools must be (a subset of) the pools that provided collateral for the specified otoken.
     */
    function settleAndRedistributeSettlement(OtokenInterface _otoken, PoolIdentifier[] calldata _pools)
        external
        whenNotPaused
    {
        settleAfterExpiry(_otoken);
        redistributeSettlement(_otoken, _pools);
    }

    /**
     * @notice Deposit and create a curve and criteria set if they don't exist.
     * @dev This function also sets the curve and criteria set in the specified pool.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _amount The amount of collateral tokens to deposit.
     * @param _curve The Curve to add and set in the pool.
     * @param _criterias A sorted array of Criteria, ordered by Criteria hash.
     */
    function depositAndCreateCurveAndCriteria(
        uint256 _poolId,
        uint256 _amount,
        ICurveManager.Curve memory _curve,
        ICriteriaManager.Criteria[] memory _criterias
    ) external whenNotPaused {
        addAndSetCurve(_poolId, _curve);
        addAndSetCriterias(_poolId, _criterias);

        // We deposit last as this involves an external call, albeit to a trusted collateral token
        deposit(_poolId, _amount);
    }

    /**
     * @notice Add and set a curve.
     * @dev If the curve already exists, it won't be added
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _curve The Curve to add and set in the pool.
     */
    function addAndSetCurve(uint256 _poolId, ICurveManager.Curve memory _curve) public whenNotPaused {
        bytes32 curveHash = crv.addCurve(_curve);
        setCurve(_poolId, curveHash);
    }

    /**
     * @notice Add criteria, criteria set and set the criteria set in the specified pool.
     * @dev If the criteria and criteria set already exists, it won't be added.
     * @param _poolId The identifier for a PoolOfCapital belonging to the caller. Could be an existing pool or a new one.
     * @param _criterias A sorted array of Criteria, ordered by Criteria hash.
     */
    function addAndSetCriterias(uint256 _poolId, ICriteriaManager.Criteria[] memory _criterias) public whenNotPaused {
        uint256 criteriasLength = _criterias.length;
        bytes32[] memory criteriaHashes = new bytes32[](criteriasLength);
        for (uint256 i = 0; i < criteriasLength; i++) {
            criteriaHashes[i] = crit.addCriteria(_criterias[i]);
        }
        bytes32 criteriaSetHash = crit.addCriteriaSet(criteriaHashes);
        setCurveCriteria(_poolId, criteriaSetHash);
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Internals
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Debits unlocked collateral tokens from the specified PoolOfCapital
     * @dev _PoolId is generated on the client side.
     * @param _lp The Address of the Liquidity provider.
     * @param _poolId An (LP-specific) pool identifier..
     * @param _amount The amount to credit to the corresponding PoolOfCapital.
     */
    function _debit(
        address _lp,
        uint256 _poolId,
        uint256 _amount
    ) internal {
        PoolOfCapital storage lpb = lpPools[_lp][_poolId];
        lpb.total = lpb.total - _amount;
        sumOfAllUnlockedBalances = sumOfAllUnlockedBalances - _amount;
        require(lpb.total >= lpb.locked, "_debit: locked > total");
    }

    /**
     * @notice Credits unlocked collateral tokens to the specified PoolOfCapital
     * @dev _PoolId is generated on the client side.
     * @param _lp The Address of the Liquidity provider.
     * @param _poolId An (LP-specific) pool identifier..
     * @param _amount The amount to credit to the corresponding PoolOfCapital.
     */

    function _credit(
        address _lp,
        uint256 _poolId,
        uint256 _amount
    ) internal {
        PoolOfCapital storage lpb = lpPools[_lp][_poolId];
        lpb.total = lpb.total + _amount;
        sumOfAllUnlockedBalances = sumOfAllUnlockedBalances + _amount;
        require(sumOfAllUnlockedBalances + sumOfAllLockedBalances <= maxTotalValueLocked, "Max TVL exceeded");
    }

    /**
     * @notice Burns collateral tokens from the specified PoolOfCapital
     * @dev _PoolId is generated on the client side.
     * @param _lp The Address of the Liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @param _amount The amount of collateral tokens to burn from the specified PoolOfCapital.
     */
    function _burnLocked(
        address _lp,
        uint256 _poolId,
        uint256 _amount
    ) internal {
        PoolOfCapital storage lpb = lpPools[_lp][_poolId];
        lpb.total = lpb.total - _amount;
        lpb.locked = lpb.locked - _amount;
        sumOfAllLockedBalances = sumOfAllLockedBalances - _amount;
        // No need to update sumOfAllUnlockedBalances
    }

    /**
     * @notice Unlocks collateral tokens within the specified PoolOfCapital
     * @dev _PoolId is generated on the client side.
     * @param _lp The Address of the Liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @param _amount The amount to unlock from the specified PoolOfCapital.
     */
    function _unlock(
        address _lp,
        uint256 _poolId,
        uint256 _amount
    ) internal {
        PoolOfCapital storage lpb = lpPools[_lp][_poolId];
        lpb.locked = lpb.locked - _amount;
        sumOfAllUnlockedBalances = sumOfAllUnlockedBalances + _amount;
        sumOfAllLockedBalances = sumOfAllLockedBalances - _amount;
        require(lpb.total >= lpb.locked, "_unlock: locked > total");
        assert(poolCollateralToken.balanceOf(address(this)) >= sumOfAllUnlockedBalances);
    }

    /**
     * @dev Get the VaultInfo for the Opyn vault that Potion uses to collateralize a given otoken
     * @param _otoken The identifier (token contract address) of the otoken. The otoken must have a vault, or the function will throw. Note that only whitelisted (or previously-whitelisted) otokens can have a vault.
     * @return The VaultInfo struct for the now-guaranteed-to-be-valid (i.e. is whitelisted or was previously whitelisted) otoken.
     */
    function _getVaultInfo(OtokenInterface _otoken) internal view returns (VaultInfo storage) {
        require(vaults[address(_otoken)].vaultId > 0, "No such vault");
        return vaults[address(_otoken)];
    }

    /**
     * @notice Get the VaultInfo for the Opyn vault that Potion uses to collateralize a given otoken.
     * @dev A vault will be created only if the otoken is whitelisted and a vault does not already exist.
     * @param _otoken The identifier (token contract address) of a whitelisted otoken.
     * @return The VaultInfo struct for the now-guaranteed-to-be-valid (i.e. is whitelisted or was previously whitelisted) otoken.
     */
    function _getOrCreateVaultInfo(OtokenInterface _otoken) internal returns (VaultInfo storage) {
        if (vaults[address(_otoken)].vaultId == 0) {
            // 0 is not used as a vault ID, so this vault does not exist yet.
            // The otoken is valid (whitelisted) and has no vault, so create a vault
            vaultCount += 1;
            Actions.ActionArgs[] memory openVaultActions = new Actions.ActionArgs[](1);
            openVaultActions[0] = ActionsLib._getOpenVaultAction(address(this), vaultCount);

            // Update our map and create the vault
            vaults[address(_otoken)].vaultId = vaultCount;
            opynController.operate(openVaultActions);

            // If the otoken is not whitelisted it's not a real otoken and we revert.
            // We could have checked this earlier, but doing it last sidesteps reantrancy issues.
            WhitelistInterface whitelist = WhitelistInterface(opynAddressBook.getWhitelist());
            require(whitelist.isWhitelistedOtoken(address(_otoken)), "Invalid otoken");
        }

        return vaults[address(_otoken)];
    }

    /**
     * @notice Increments the locked and total collateral for the LP, on the assumption that the quote will be
     * exercized.
     * @dev Does NOT check that the supplied otoken is valid, or allowed by the LP. Does NOT check that the supplied curve is allowed by the LP.
     * @dev It must only be called by internal functions that ensure the order is subsequntly fulfilled.
     * @param _seller The seller details(LP).
     * @param _collateralCalcParams Struct used to pass other inputs required for collateral calculation
     */
    function _initiatePurchaseAndUpdateFundsForOneLP(
        CounterpartyDetails memory _seller,
        CollateralCalculationParams memory _collateralCalcParams
    ) internal returns (uint256 premium, uint256 collateralAmount) {
        // Take the premium from the buyer; it's paid in the collateral token
        PoolOfCapital storage lpBal = lpPools[_seller.lp][_seller.poolId];

        // Return the collateral amount
        collateralAmount = _collateralNeededForPuts(_seller.orderSizeInOtokens, _collateralCalcParams);
        premium = _premiumForLp(_seller.lp, _seller.poolId, _seller.curve, collateralAmount);
        lpBal.total = lpBal.total + premium;
        lpBal.locked = lpBal.locked + collateralAmount;
        sumOfAllUnlockedBalances = sumOfAllUnlockedBalances + premium - collateralAmount;
        sumOfAllLockedBalances = sumOfAllLockedBalances + collateralAmount;
        require(lpBal.locked <= lpBal.total, "insufficient collateral");
        return (premium, collateralAmount);
    }

    /**
     * @notice The amount of capital required to collateralize a given quantitiy of a given `OToken`.
     * @dev don't introduce rounding errors. this must match the value returned by Opyn's logic, or else options will be insufcciently collateralised
     * @param _otokenQty The number of OTokens we wish to collateralize.
     * @param _collateralCalcParams Struct used to pass other inputs required for collateral calculation
     * @return The amount of collateral required, denominated in collateral tokens.
     */
    function _collateralNeededForPuts(uint256 _otokenQty, CollateralCalculationParams memory _collateralCalcParams)
        internal
        pure
        returns (uint256)
    {
        // Takes the non-expired, non-spread, selling a put case code from _getMarginRequired
        // Otoken quantities always use 8 decimals
        FPI.FixedPointInt memory shortOtokensHumanReadable = FPI.fromScaledUint(_otokenQty, OTOKEN_QTY_DECIMALS);
        FPI.FixedPointInt memory collateralNeededHumanStrikeTokens =
            shortOtokensHumanReadable.mul(_collateralCalcParams.otokenStrikeHumanReadable);
        // convert amount to be denominated in collateral

        FPI.FixedPointInt memory collateralRequired;
        if (_collateralCalcParams.collateralMatchesStrike) {
            // No exchange rate conversion required
            collateralRequired = collateralNeededHumanStrikeTokens;
        } else {
            assert(_collateralCalcParams.collateralPrice.value > 0);
            collateralRequired = _convertAmountOnLivePrice(
                collateralNeededHumanStrikeTokens,
                _collateralCalcParams.strikePrice,
                _collateralCalcParams.collateralPrice
            );
        }

        return collateralRequired.toScaledUint(_collateralCalcParams.collateralTokenDecimals, false);
    }

    /**
     * @notice Calculates the Premium for the supplied counterparty details.
     * @dev Does NOT check that the supplied curve is allowed. Premium calculations involve some orunding and loss of accuracy due
     * to the complex math at play. We expect the calculated premium to be within 0.1% of the correct value (i.e. the value we would
     * get in, say, python with no loss of precision) in all but a few pathological cases (e.g. util below 0.1% and multiple curve
     * parameters very near zero)
     * @param _lp The Address of the Liquidity provider.
     * @param _poolId An (LP-specific) pool identifier.
     * @param _curve The curve used to calculate the premium.
     * @param _collateralToLock The amount of collateral to lock.
     * @return premiumInCollateralTokens
     */
    function _premiumForLp(
        address _lp,
        uint256 _poolId,
        ICurveManager.Curve memory _curve,
        uint256 _collateralToLock
    ) internal view returns (uint256 premiumInCollateralTokens) {
        (int256 utilBeforeAs59x18, int256 utilAfterAs59x18, uint256 lockedAmountBefore, uint256 lockedAmountAfter) =
            util(_lp, _poolId, _collateralToLock);

        // Make sure we're not buying too large an amount, nor an amount so small that we can't calc a premium
        require(utilAfterAs59x18 > utilBeforeAs59x18, "Order tranche too small");
        require(utilAfterAs59x18 <= _curve.max_util_59x18, "Max util exceeded");

        // The result of hyperbolicCurve tells us the premium we should have received in aggregate at any utilisation, as a percentage
        // of the aggregate locked collateral.
        // When calling hyperbolicCurve we pass in a utilisation as a fixed-point decimal (1.0 = 100% utilisation) and get back the
        // a % as a fixed point decimal (1.0 = premium should be 100% of the locked collateral).
        // To get the premium for our new order, we:
        //   1. Calculate the premium we should have received, in aggregate, BEFORE this order
        //   2. Calculate the premium we should have received, in aggregate, AFTER this order (for any non-trivial order, utilisation and
        //      collateral locked will both increase)
        //   3. Charge the buyer difference.
        uint256 premiumBefore =
            crv.hyperbolicCurve(_curve, utilBeforeAs59x18).mul(PRBMathSD59x18.fromUint(lockedAmountBefore)).toUint();
        uint256 premiumAfter =
            crv.hyperbolicCurve(_curve, utilAfterAs59x18).mul(PRBMathSD59x18.fromUint(lockedAmountAfter)).toUint();
        return premiumAfter - premiumBefore;
    }

    /**
     * @notice Return the spot prices of assets A and B, unless A and B are the same asset
     * @param _assetA Asset A address
     * @param _assetB Asset B address
     * @return identicalAssets whether the passed assets were identical; if so, prices of 0 are returned
     * @return scaledPriceA of asset A (not set if identicalAssets=true)
     * @return scaledPriceB of asset B (not set if identicalAssets=true)
     */
    function _getLivePrices(address _assetA, address _assetB)
        internal
        view
        returns (
            bool identicalAssets,
            FPI.FixedPointInt memory scaledPriceA,
            FPI.FixedPointInt memory scaledPriceB
        )
    {
        if (_assetA == _assetB) {
            // N.B. this may be the most common case for puts
            return (true, FPI.fromUnscaledInt(0), FPI.fromUnscaledInt(0));
        }

        OracleInterface oracle = OracleInterface(AddressBookInterface(opynAddressBook).getOracle());

        // Oracle prices are always scaled by 8 decimals
        uint256 priceA = oracle.getPrice(_assetA);
        uint256 priceB = oracle.getPrice(_assetB);

        return (
            false,
            FPI.fromScaledUint(priceA, ORACLE_PRICE_DECIMALS),
            FPI.fromScaledUint(priceB, ORACLE_PRICE_DECIMALS)
        );
    }

    /**
     * @notice Convert an amount in asset A to equivalent amount of asset B, based on a live price.
     * @dev Function includes the amount and applies .mul() first to increase the accuracy.
     * @param _amount Amount in asset A.
     * @param _priceA The price of asset A, as returned by Opyn's oracle (decimals = 8), in the FixedPointInt representation of decimal numbers
     * @param _priceB The price of asset B, as returned by Opyn's oracle (decimals = 8), in the FixedPointInt representation of decimal numbers
     */
    function _convertAmountOnLivePrice(
        FPI.FixedPointInt memory _amount,
        FPI.FixedPointInt memory _priceA,
        FPI.FixedPointInt memory _priceB
    ) internal pure returns (FPI.FixedPointInt memory) {
        // amount A * price A in USD = amount B * price B in USD
        // amount B = amount A * price A / price B
        assert(_priceB.value > 0);
        return _amount.mul(_priceA).div(_priceB);
    }
}
