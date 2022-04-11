/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.4;
import {OtokenInterface} from "./packages/opynInterface/OtokenInterface.sol";
import {Actions} from "./packages/opynInterface/ActionsInterface.sol";

library OpynActionsLibrary {
    function _getOpenVaultAction(address _owner, uint256 _vaultId) internal pure returns (Actions.ActionArgs memory) {
        return
            Actions.ActionArgs({
                actionType: Actions.ActionType.OpenVault,
                owner: _owner,
                vaultId: _vaultId,
                secondAddress: address(0),
                asset: address(0),
                amount: 0,
                index: 0,
                data: ""
            });
    }

    function _getSettleVaultAction(
        address _owner,
        uint256 _vaultId,
        address to
    ) internal pure returns (Actions.ActionArgs memory) {
        return
            Actions.ActionArgs({
                actionType: Actions.ActionType.SettleVault,
                owner: _owner,
                vaultId: _vaultId,
                secondAddress: to,
                asset: address(0),
                amount: 0,
                index: 0,
                data: ""
            });
    }

    function _getDepositCollateralAction(
        address _owner,
        uint256 _vaultId,
        address _otoken,
        address _from,
        uint256 _amount
    ) internal pure returns (Actions.ActionArgs memory) {
        return
            Actions.ActionArgs({
                actionType: Actions.ActionType.DepositCollateral,
                owner: _owner,
                vaultId: _vaultId,
                secondAddress: _from,
                asset: _otoken,
                amount: _amount,
                index: 0,
                data: ""
            });
    }

    function _getMintShortOptionAction(
        address _owner,
        uint256 _vaultId,
        address _otoken,
        address _to,
        uint256 _amount
    ) internal pure returns (Actions.ActionArgs memory) {
        return
            Actions.ActionArgs({
                actionType: Actions.ActionType.MintShortOption,
                owner: _owner,
                vaultId: _vaultId,
                secondAddress: _to,
                asset: _otoken,
                amount: _amount,
                index: 0,
                data: ""
            });
    }

    function _actionArgsToDepositCollateralAndMintOtokens(
        uint256 _vaultId,
        OtokenInterface _otoken,
        address _collateralToken,
        uint256 _collateralAmount,
        uint256 _orderSizeInOtokens
    ) internal view returns (Actions.ActionArgs[] memory opynActions) {
        // Deposit collateral and mint options straight to the buyer
        opynActions = new Actions.ActionArgs[](2);
        opynActions[0] = _getDepositCollateralAction(
            address(this),
            _vaultId,
            address(_collateralToken),
            address(this),
            _collateralAmount
        );
        opynActions[1] = _getMintShortOptionAction(
            address(this),
            _vaultId,
            address(_otoken),
            msg.sender,
            _orderSizeInOtokens
        );

        return opynActions;
    }
}
