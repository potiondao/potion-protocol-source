# Overview

[Opyn's contracts](https://github.com/opynfinance/GammaProtocol/tree/master/contracts) are compiled, and deployed by Opyn, and deployed by Potion only for testing purposes, all using solc v0.6. This ensures that the deployed bytecode that we test against will match what is deployed by Opyn on mainnet.

Potion code is compiled using solc v0.8. Among other reasons, this eases integration with our chosen math library.

We achieve this dual-compilation as follows:

- `imports.sol` imports uses solc 0.6. It imports the Opyn code without doing anything with it, resulting in solc 0.6 artifacts.
- `OpynControllerInterface`, `ActionsInterface` and `MarginVaultInterface` are all interface definitions, created by Potion to match Opyn's code (Opyn do not provide these interface definitions). These ease integration with the deployed Opyn contracts - particularly the Controller - and are compiled with solc 0.8 so that they can be imported by the 0.8 Potion contracts.
- `FixedPointInt` is a copy of [Opyn's library of the same name](https://github.com/opynfinance/GammaProtocol/blob/master/contracts/libs/FixedPointInt256.sol), but with the pragma updated to compile using solc 0.8. This library `uses` the `SignedConverter` library.
- The other files in this directory are all copies of [Opyn's provided interface files](https://github.com/opynfinance/GammaProtocol/tree/master/contracts/interfaces), but with the pragma updated to compile using solc 0.8.

# Upgrades

_ALL OF THE CONTRACTS IN THIS DIRECTORY MUST BE CHECKED FOR COMPATIBILITY WITH OPYN'S LATEST CODE AFTER EVERY OPYN UPGRADE._

Use the hardhat script `scripts/compareAbis.ts` to help with this.

---

Changelog:

May 2021 we updated from Opyn commit [752c5c336f28459a9d5ae14cae123e8e47b7b02f](https://github.com/opynfinance/GammaProtocol/tree/752c5c336f28459a9d5ae14cae123e8e47b7b02f) to Opyn commit [9a75da2ad8beefdaa4caa97d17799b50552ca450](https://github.com/opynfinance/GammaProtocol/tree/9a75da2ad8beefdaa4caa97d17799b50552ca450).

This was a pre-audit commit and incorporated the following changes:

Controller:

- New function `donate(address _asset, uint256 _amount)`
- New function `sync(address _owner, uint256 _vaultId)`
- New function `isLiquidatable(address _owner, uint256 _vaultId, uint256 _roundId)`
- Function `isSettlementAllowed(address _otoken) external view returns (bool)` is replaced by `isSettlementAllowed(address _underlying,address _strike,address _collateral,uint256 _expiry)` (both `returns (bool)`)
- Function `getVault(address _owner, uint256 _vaultId) external view returns (MarginVaultInterface.Vault memory)` is replaced by `getVault(address _owner, uint256 _vaultId) public view returns ( MarginVault.Vault memory, uint256, uint256 )`

Otoken

- New function `function getOtokenDetails() external view returns ( address, address, address, uint256, uint256, bool )`

MarginCalculator

- Function `getExcessCollateral(MarginVaultInterface.Vault calldata _vault)` is replaced by `getExcessCollateral(MarginVault.Vault calldata _vault, uint256 _vaultType)`
- New function `isLiquidatable( MarginVault.Vault memory _vault, uint256 _vaultType, uint256 _vaultLatestUpdate, uint256 _roundId ) external view returns ( bool, uint256, uint256 )`

Oracle

- New function `getChainlinkRoundData(address _asset, uint80 _roundId) external view returns (uint256, uint256);`

Actions interface

- New `ActionType` called `Liquidate`

Jul 20221 we updated from Opyn commit [9a75da2ad8beefdaa4caa97d17799b50552ca450](https://github.com/opynfinance/GammaProtocol/tree/9a75da2ad8beefdaa4caa97d17799b50552ca450) to Opyn commit [14b009b0ad4f187b046f1c899123a180b003bb11](https://github.com/opynfinance/GammaProtocol/tree/14b009b0ad4f187b046f1c899123a180b003bb11).

This post-audit commit undid some of the changes in `9a75da2ad8beefdaa4caa97d17799b50552ca450` that had broken back-compatiblity with earlier releases. In particular:

- `getVault(address _owner, uint256 _vaultId) external view returns (MarginVaultInterface.Vault memory)` is restored
- `getVaultWithDetails(address _owner, uint256 _vaultId) public view returns ( MarginVault.Vault memory, uint256, uint256 )` is added
- `isSettlementAllowed(address _otoken) external view returns (bool)` is restored
- `canSettleAssets(address _underlying,address _strike,address _collateral,uint256 _expiry)` is added
