import { log, BigDecimal, Bytes } from "@graphprotocol/graph-ts";
import { CurveAdded } from "../generated/CurveManager/CurveManager";
import { Curve } from "../generated/schema";
import { int59x18ToDecimal } from "./helpers";

export function createCriteriaId(criteriaHash: Bytes): string {
  return criteriaHash.toHexString();
}

export function createCriteriaSetId(criteriaSetHash: Bytes): string {
  return criteriaSetHash.toHexString();
}

export function createCriteriaJoinedCriteriaSetId(
  criteriaHash: Bytes,
  criteriaSetHash: Bytes
): string {
  return criteriaHash.toHexString() + criteriaSetHash.toHexString();
}

function calculateAverageCostAux(
  curve: Curve,
  util: BigDecimal,
  locked: BigDecimal,
  size: BigDecimal
): BigDecimal {
  if (size.gt(BigDecimal.fromString("0"))) {
    // a * x * cosh(b*x^c) + d
    const a = parseFloat(curve.a.toString());
    const b = parseFloat(curve.b.toString());
    const c = parseFloat(curve.c.toString());
    const d = parseFloat(curve.d.toString());
    const utilFloat = parseFloat(util.toString());
    const maxUtil = parseFloat(curve.maxUtil.toString());
    const lockedFloat = parseFloat(locked.toString());
    const sizeFloat = parseFloat(size.toString());
    const unlockedFloat = maxUtil * sizeFloat - lockedFloat;
    log.info("calculateAverageCostAux {}", [unlockedFloat.toString()]);

    const upperPremiumPercent = a * maxUtil * Math.cosh(b * maxUtil ** c) + d;
    const lowerPremiumPercent =
      a * utilFloat * Math.cosh(b * utilFloat ** c) + d;
    const premium =
      sizeFloat * maxUtil * upperPremiumPercent -
      lockedFloat * lowerPremiumPercent;
    if (unlockedFloat > 1) {
      return BigDecimal.fromString(premium.toString()).div(
        BigDecimal.fromString(unlockedFloat.toString())
      );
    }
  }
  return BigDecimal.fromString(Number.MAX_SAFE_INTEGER.toString());
}

export function calculateAverageCost(
  curveId: string,
  util: BigDecimal,
  locked: BigDecimal,
  size: BigDecimal
): BigDecimal {
  log.debug("calculateAverageCost {}", [curveId]);
  const curve = Curve.load(curveId);
  if (curve) {
    return calculateAverageCostAux(curve as Curve, util, locked, size);
  }
  return BigDecimal.fromString(Number.MAX_SAFE_INTEGER.toString());
}

/**
 * Called when a CurveAdded event is emitted. Creates a new Curve entity.
 * @param {CurveAdded} event Descriptor of the event emitted.
 */
export function handleCurveAdded(event: CurveAdded): void {
  const curveId: Bytes = event.params.curveHash;
  let curve = Curve.load(curveId.toHexString());
  if (curve == null) {
    curve = new Curve(curveId.toHexString());

    curve.a = int59x18ToDecimal(event.params.curveParams.a_59x18);
    curve.b = int59x18ToDecimal(event.params.curveParams.b_59x18);
    curve.c = int59x18ToDecimal(event.params.curveParams.c_59x18);
    curve.d = int59x18ToDecimal(event.params.curveParams.d_59x18);
    curve.maxUtil = int59x18ToDecimal(event.params.curveParams.max_util_59x18);

    curve.save();
  } else {
    log.warning("Tried to save the same curve multiple times, curveId is {}", [
      curveId.toString(),
    ]);
  }
}
