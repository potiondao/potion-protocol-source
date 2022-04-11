/**
 * SPDX-License-Identifier: UNLICENSED
 */
pragma solidity 0.8.4;

/**
 * @title ICurveManager
 * @notice Keeps a registry of all Curves that are known to the Potion protocol
 */
interface ICurveManager {
    ///////////////////////////////////////////////////////////////////////////
    //  Events
    ///////////////////////////////////////////////////////////////////////////

    /// @notice Emits when new curves are registered.
    /// @dev Curves are immutable once added, so expect at most one log per curveHash.
    event CurveAdded(bytes32 indexed curveHash, Curve curveParams);

    ///////////////////////////////////////////////////////////////////////////
    //  Structs and vars
    ///////////////////////////////////////////////////////////////////////////

    /// @notice A Curve defines a function of the form:
    ///
    ///  f(x) =  a * x * cosh(b*x^c) + d
    ///
    /// @dev All Curve parameters are signed 59x18-bit fixed point numbers, i.e. the numerator part of a number
    /// that has a fixed denominator of 2^64.
    struct Curve {
        int256 a_59x18;
        int256 b_59x18;
        int256 c_59x18;
        int256 d_59x18;
        int256 max_util_59x18;
    }

    /**
     * @notice Add the specified Curve to the registry of Curves that are known to our contract
     * @param _curve The Curve to register
     * @return hash The keccak256 of the Curve
     */
    function addCurve(Curve calldata _curve) external returns (bytes32 hash);

    /**
     * @notice Get the hash of given Curve
     * @param _curve The Curve to be hashed.
     * @return The keccak256 hash of the Curve
     */
    function hashCurve(Curve memory _curve) external pure returns (bytes32);

    /**
     * @notice Check whether the specified hash is the hash of a Curve that is known to our contract
     * @param _hash The hash to look for
     * @return valid True if the hash is that of a known Curve; false if it is not
     */
    function isKnownCurveHash(bytes32 _hash) external view returns (bool valid);

    /**
     * @notice Calculates hyperbolic cosine of an input x, using the formula:
     *
     *            e^x + e^(-x)
     * cosh(x) =  ------------
     *                 2
     *
     * @dev The input and output are signed 59x18-bit fixed point number.
     * @param _input59x18 Signed 59x18-bit fixed point number
     * @return output59x18 Result of computing the hyperbolic cosine of an input x
     */
    function cosh(int256 _input59x18) external pure returns (int256 output59x18);

    /**
     * @notice Evaluates the function defined by curve c at point x, example:
     *
     *    a * x * cosh(b*x^c) + d
     *
     * @dev x is typically utilisation as a fraction (1 = 100%).
     * @dev All inputs are signed 59x18-bit fixed point numbers, i.e. the numerator part of a number
     * that has a fixed denominator of 2^64
     * @dev The output is a signed 59x18-bit fixed point number.
     * @param _curve The Curve values to be used by the function expression mentioned above.
     * @param _x_59x18 The point at which the function expression mentioned above will be calculated.
     * @return output59x18 Result of the function expression mentioned above evaluated at point x.
     */
    function hyperbolicCurve(Curve memory _curve, int256 _x_59x18) external pure returns (int256 output59x18);
}
