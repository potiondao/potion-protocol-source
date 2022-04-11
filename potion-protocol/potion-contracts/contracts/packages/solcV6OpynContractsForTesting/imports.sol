// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.6.10;

// Import any external dependencies that we want hardhat to have access to and for which we wish to generate typechain bindings
import {AddressBook} from "gamma-protocol/contracts/core/AddressBook.sol";
import {Controller} from "gamma-protocol/contracts/core/Controller.sol";
import {MarginCalculator} from "gamma-protocol/contracts/core/MarginCalculator.sol";
import {MarginPool} from "gamma-protocol/contracts/core/MarginPool.sol";
import {MockERC20} from "gamma-protocol/contracts/mocks/MockERC20.sol";
import {MockOracle} from "gamma-protocol/contracts/mocks/MockOracle.sol";
import {MockAddressBook} from "gamma-protocol/contracts/mocks/MockAddressBook.sol";
import {MockOtoken} from "gamma-protocol/contracts/mocks/MockOtoken.sol";
import {MockWhitelistModule} from "gamma-protocol/contracts/mocks/MockWhitelistModule.sol";
import {Oracle} from "gamma-protocol/contracts/core/Oracle.sol";
import {Otoken} from "gamma-protocol/contracts/core/Otoken.sol";
import {OtokenFactory} from "gamma-protocol/contracts/core/OtokenFactory.sol";
import {OtokenFactory} from "gamma-protocol/contracts/core/OtokenFactory.sol";
import {Whitelist} from "gamma-protocol/contracts/core/Whitelist.sol";