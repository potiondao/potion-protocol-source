// SPDX-License-Identifier: UNLICENSED
// For testing token functions on testnet
pragma solidity 0.8.4;

import "./FaucetToken.sol";

contract SampleUnderlyingToken is FaucetToken {
    /* solhint-disable no-empty-blocks */
    constructor(string memory symbol) FaucetToken(0, "SampleUnderlyingToken", 18, symbol) {}

    /* solhint-enable no-empty-blocks */
}
