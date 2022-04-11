// SPDX-License-Identifier: UNLICENSED
// Adapted from public domain Opyn code
pragma solidity 0.8.4;

import {MarginVaultInterface} from "./MarginVaultInterface.sol";

interface MarginCalculatorInterface {
    function getExpiredPayoutRate(address _otoken) external view returns (uint256);

    function getExcessCollateral(MarginVaultInterface.Vault calldata _vault, uint256 _vaultType)
        external
        view
        returns (uint256 netValue, bool isExcess);

    function isLiquidatable(
        MarginVaultInterface.Vault memory _vault,
        uint256 _vaultType,
        uint256 _vaultLatestUpdate,
        uint256 _roundId
    )
        external
        view
        returns (
            bool,
            uint256,
            uint256
        );
}
