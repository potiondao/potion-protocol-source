/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.4;
import {OtokenInterface} from "./packages/opynInterface/OtokenInterface.sol";
import {PRBMathSD59x18} from "./packages/PRBMathSD59x18.sol";
import {ICurveManager} from "./interfaces/ICurveManager.sol";

/**
 * @title CurveManagerNew
 * @notice Keeps a registry of all Curves that are known to the Potion protocol
 */
contract CurveManager is ICurveManager {
    using PRBMathSD59x18 for int256;

    ///////////////////////////////////////////////////////////////////////////
    //  Curve constraints
    ///////////////////////////////////////////////////////////////////////////
    /// @dev PRBMathSD59x18 scale numbers to 1e18, so it can represents numbers in that range.
    int256 private constant A_LOWER_BOUND = 0;
    int256 private constant A_UPPER_BOUND = 10e18; // 10 as 59x18 decimal
    int256 private constant B_LOWER_BOUND = 0;
    int256 private constant B_UPPER_BOUND = 20e18; // 20 as 59x18 decimal
    int256 private constant C_LOWER_BOUND = 0;
    int256 private constant C_UPPER_BOUND = 1000e18; // 1000 as 59x18 decimal
    int256 private constant D_LOWER_BOUND = 0;
    int256 private constant D_UPPER_BOUND = 20e18; // 20 as 59x18 decimal
    int256 private constant UTIL_LOWER_BOUND = 0; // 0 -> 0%. Also used as bound for max_util
    int256 private constant UTIL_UPPER_BOUND = 1e18; // 1 -> 100%  as 59x18 decimal. Also used as bound for max_util

    /// @dev whether a Curve instance is known to us, indexed by the hash of the struct
    mapping(bytes32 => bool) public registeredCurves;

    ///////////////////////////////////////////////////////////////////////////
    //  Public interfaces
    ///////////////////////////////////////////////////////////////////////////

    /**
     * @notice Add the specified Curve to the registry of Curves that are known to our contract
     * @param _curve The Curve to register
     * @return hash The keccak256 of the Curve
     */
    function addCurve(Curve calldata _curve) external override onlyValidCurves(_curve) returns (bytes32 hash) {
        hash = hashCurve(_curve);
        if (!registeredCurves[hash]) {
            registeredCurves[hash] = true;
            emit CurveAdded(hash, _curve);
        }
        return hash;
    }

    /**
     * @notice Get the hash of given Curve
     * @param _curve The Curve to be hashed.
     * @return The keccak256 hash of the Curve
     */
    function hashCurve(Curve calldata _curve) public pure override returns (bytes32) {
        return
            keccak256(
                abi.encodePacked(_curve.a_59x18, _curve.b_59x18, _curve.c_59x18, _curve.d_59x18, _curve.max_util_59x18)
            );
    }

    /**
     * @notice Check whether the specified hash is the hash of a Curve that is known to our contract
     * @param _hash The hash to look for
     * @return valid True if the hash is that of a known Curve; false if it is not
     */
    function isKnownCurveHash(bytes32 _hash) external view override returns (bool valid) {
        return registeredCurves[_hash];
    }

    /**
     * @notice Calculate x^y, assuming 0^0 is 1, where x and y are both signed 59x18 fixed point numbers
     * @dev Revert on overflow.
     *
     * @param _x_59x18 Signed 59x18-bit fixed point number
     * @param _y_59x18 Signed 59x18-bit fixed point number
     * @return Signed 59x18-bit fixed point number
     */
    function powerDecimal(int256 _x_59x18, int256 _y_59x18) external pure returns (int256) {
        require(_x_59x18 >= 0, "powerDecimal: base must be >= 0");

        if (_x_59x18 == 0 && _y_59x18 == 0) {
            // Return 1 as a 59x18-bit fixed point number
            return 1e18;
        } else if (_x_59x18 == 0) {
            return 0; // ln(0) undefined so require special case
        } else {
            return _y_59x18.mul(_x_59x18.ln()).exp();
        }
    }

    /**
     * @notice Calculates hyperbolic cosine of an input x, using the formula:
     *
     *            e^x + e^(-x)
     * cosh(x) =  ------------
     *                 2
     *
     * @dev The input and output are signed 59x18-bit fixed point number.
     * @param _input59x18 Signed 59x18-bit fixed point number, less than or equal to 10.
     * @return output59x18 Result of computing the hyperbolic cosine of an input x
     */
    function cosh(int256 _input59x18) public pure override returns (int256 output59x18) {
        // The maximum input we need to support when called by hyperbolicCurve is `b*x^c`
        // We know that |x| <= 1, so the max input we must support is B_UPPER_BOUND
        require(_input59x18 >= 0, "Cosh input < 0");
        require(_input59x18 <= B_UPPER_BOUND, "Cosh input too high");
        int256 numerator = _input59x18.exp().add(_input59x18.mul(PRBMathSD59x18.fromInt(-1)).exp());
        return numerator.div(PRBMathSD59x18.fromInt(2));
    }

    /**
     * @notice Evaluates the function defined by curve c at point x (0 <= x <= 1), example:
     *
     *    a * x * cosh(b*x^c) + d
     *
     * @dev x is typically utilisation as a fraction (1 = 100%). We only support 0 <= x <= 1.
     * @dev All inputs are signed 59x18-bit fixed point numbers
     * @dev The output is a signed 59x18-bit fixed point number.
     * @param _curve The Curve values to be used by the function expression mentioned above.
     * @param _x_59x18 The point at which the function expression mentioned above will be calculated. Must be between 0 and 1, inclusive.
     * @return output59x18 Result of the function expression mentioned above evaluated at point x.
     */
    function hyperbolicCurve(Curve calldata _curve, int256 _x_59x18)
        external
        pure
        override
        returns (int256 output59x18)
    {
        // We do not check that the curve is valid here, but note that only valid curves can be added to our registry
        require(_x_59x18 >= UTIL_LOWER_BOUND, "x input too low");
        require(_x_59x18 <= UTIL_UPPER_BOUND, "x input too high");
        int256 coshPart = cosh(_curve.b_59x18.mul(PRBMathSD59x18.pow(_x_59x18, _curve.c_59x18)));

        output59x18 = _curve.d_59x18.add(coshPart.mul(_curve.a_59x18).mul(_x_59x18));

        return output59x18;
    }

    ///////////////////////////////////////////////////////////////////////////
    //  Internals
    ///////////////////////////////////////////////////////////////////////////
    modifier onlyValidCurves(Curve calldata _curve) {
        require(_curve.a_59x18 >= A_LOWER_BOUND && _curve.a_59x18 <= A_UPPER_BOUND, "Invalid A value");
        require(_curve.b_59x18 >= B_LOWER_BOUND && _curve.b_59x18 <= B_UPPER_BOUND, "Invalid B value");
        require(_curve.c_59x18 >= C_LOWER_BOUND && _curve.c_59x18 <= C_UPPER_BOUND, "Invalid C value");
        require(_curve.d_59x18 >= D_LOWER_BOUND && _curve.d_59x18 <= D_UPPER_BOUND, "Invalid D value");
        require(
            _curve.max_util_59x18 > UTIL_LOWER_BOUND && _curve.max_util_59x18 <= UTIL_UPPER_BOUND,
            "Invalid Max util value"
        );
        _;
    }
}
