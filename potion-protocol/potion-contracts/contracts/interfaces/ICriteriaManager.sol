/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.4;

import {OtokenInterface} from "../packages/opynInterface/OtokenInterface.sol";

/**
 * @title ICriteriaManager
 * @notice Keeps a registry of all Criteria and CriteriaSet instances that are know to the Potion protocol.
 */
interface ICriteriaManager {
    ///////////////////////////////////////////////////////////////////////////
    //  Events
    ///////////////////////////////////////////////////////////////////////////

    /// @notice Emits when new criteria are registered.
    /// @dev Criteria are immutable once added, so expect at most one log per criteriaHash.
    event CriteriaAdded(bytes32 indexed criteriaHash, Criteria criteria);

    /// @notice Emits when a new set of criteria is registered.
    /// @dev Criteria sets are immutable once added, so expect at most one log per criteriaSetHash.
    event CriteriaSetAdded(bytes32 indexed criteriaSetHash, bytes32[] criteriaSet);

    ///////////////////////////////////////////////////////////////////////////
    //  Structs and vars
    ///////////////////////////////////////////////////////////////////////////

    /// @dev A Criteria is considered a match for an OToken if the assets match, and the isPut flag matches, and maxStrikePercent is greater than or equal to the option's strike as a percentage of the current spot price, and maxDurationInDays is greater than or equal to the number of days (whole days or part days) until the OToken expires.
    struct Criteria {
        address underlyingAsset;
        address strikeAsset;
        bool isPut;
        uint256 maxStrikePercent;
        uint256 maxDurationInDays; // Must be > 0 for valid criteria. Doubles as existence flag.
    }

    /// @dev Otoken properties to be checked against Criteria.
    struct OtokenProperties {
        uint256 percentStrikeValue; /// The strike price as a percentage of the current price, rounded up to an integer percentage. E.g. if current price is $100, then a strike price of $94.01 implies a strikePercent of 95, and a strike price of $102.99 implies a strikePercent of 103.
        uint256 wholeDaysRemaining; /// The number of days remaining until OToken expiry, rounded up if necessary to make to an integer number of days.
        address underlyingAsset;
        address strikeAsset;
        bool isPut;
    }

    /// @dev a (non-enumerable) set of Criteria. An OToken is considered a match with a CriteriaSet if one or more of the Criteria within the set is a Match for the option.
    struct CriteriaSet {
        bool exists;
        mapping(bytes32 => bool) hashes;
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Public interfaces
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Add the specified set of Criteria to the registry of CriteriaSets that are known to our contract.
     * @param _hashes A sorted list of bytes32 values, each being the hash of a known Criteria. No duplicates, so this can be considered a set.
     * @return criteriaSetHash The identifier for this criteria set.
     */
    function addCriteriaSet(bytes32[] memory _hashes) external returns (bytes32 criteriaSetHash);

    /**
     * @notice Check whether the specified hash is the hash of a CriteriaSet that is known to our contract.
     * @param _criteriaSetHash The hash to look for.
     * @return valid True if the hash is that of a known CriteriaSet; false if it is not.
     */
    function isCriteriaSetHash(bytes32 _criteriaSetHash) external view returns (bool valid);

    /**
     * @notice Add the specified Criteria to the registry of Criteria that are known to our contract.
     * @param _criteria The Criteria to register.
     * @return hash The keccak256 of the Criteria.
     */
    function addCriteria(Criteria memory _criteria) external returns (bytes32 hash);

    /**
     * @notice Get the hash of given Criteria
     * @param _criteria The Criteria to be hashed.
     * @return The keccak256 hash of the Criteria.
     */
    function hashCriteria(Criteria memory _criteria) external pure returns (bytes32);

    /**
     * @notice Get the hash of an ordered list of hash values.
     * @param _hashes The list of bytes32 values to be hashed. This list must be sorted according to solidity's ordering, and must not contain any duplicate values.
     * @return The keccak256 hash of the set of hashes.
     */
    function hashOfSortedHashes(bytes32[] memory _hashes) external pure returns (bytes32);

    /**
     * @notice Check whether the specified Criteria hash exists within the specified CriteriaSet.
     * @dev Clients should be responsible of passing correct parameters(_criteriaSetHash and _criteriaHash), otherwise we revert.
     * @param _criteriaSetHash The criteria list to be checked.
     * @param _criteriaHash The criteria we are looking for on that list.
     * @return isInSet true if the criteria exists in the criteriaSet; false if it does not.
     */
    function isInCriteriaSet(bytes32 _criteriaSetHash, bytes32 _criteriaHash) external view returns (bool isInSet);

    /**
     * @notice Check that a given token matches some specific Criteria.
     * @param _criteria The criteria to be checked against
     * @param _otokenCache The otoken to check
     */
    function requireOtokenMeetsCriteria(Criteria memory _criteria, OtokenProperties memory _otokenCache) external pure;
}
