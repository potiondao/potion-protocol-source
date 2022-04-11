import { has as _has, isString as _isString, times as _times } from "lodash-es";
import { CurveParams } from "@/types";

const HYPERBOLIC_POINTS = 100;

const curveParamsToHyperbolic = (params: CurveParams) => {
  if (validCurveParams(params)) {
    return _times(HYPERBOLIC_POINTS, (x) => getHyperbolicPoint(x, params));
  }
  return [];
};

const validCurveParams = (params: CurveParams) => {
  return ["a", "b", "c", "d"].every(
    (p) => _has(params, p) && _isString(params[p])
  );
};

const getHyperbolicPoint = (point: number, params: CurveParams) => {
  const x = point / (HYPERBOLIC_POINTS - 1);
  const a = parseFloat(params.a);
  const b = parseFloat(params.b);
  const c = parseFloat(params.c);
  const d = parseFloat(params.d);

  return a * x * Math.cosh(b * Math.pow(x, c)) + d;
};

export { curveParamsToHyperbolic, HYPERBOLIC_POINTS };
