// SPDX-License-Identifier: UNLICENSED
// For testing token functions on testnet
pragma solidity 0.8.4;

import "./FaucetToken.sol";

contract PotionTestUSD is FaucetToken {
    /* solhint-disable no-empty-blocks */
    constructor() FaucetToken(0, "PotionTestUSDC", 6, "PUSDC") {}

    /* solhint-enable no-empty-blocks */
}
