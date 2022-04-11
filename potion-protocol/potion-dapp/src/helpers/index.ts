import {
  has as _has,
  isNil as _isNil,
  isNumber as _isNumber,
  reverse as _reverse,
  uniqBy as _uniqBy,
} from "lodash-es";

import dayjs from "dayjs";
import { getPriceFromOracle } from "@/services/contracts/oracle";

const _exists = (x) => !_isNil(x);
const validValue = (value, max) => _isNumber(value) && value > 0 && value < max;

const offsetToDate = (blockTimestamp, offset) =>
  _exists(offset)
    ? dayjs.unix(blockTimestamp).add(offset, "day").format("ll")
    : "Invalid Date";
const dateToOffset = (blockTimestamp, offset) => {
  if (_exists(offset)) {
    const expiration = dayjs.unix(offset);
    const today = dayjs.unix(blockTimestamp);
    const diff = expiration.diff(today, "day");
    return diff;
  }
  return "Invalid Date";
};
const getUnderlyingsPriceMap = async (underlyings, decimals = 8) => {
  const map = {};
  for (const underlying of underlyings) {
    if (!_has(map, underlying.address)) {
      map[underlying.address] = await getPriceFromOracle(
        underlying.address,
        decimals.toString()
      );
    }
  }

  return map;
};

const getEtherscanLink = (
  hash,
  operation = "tx",
  url = process.env.VUE_APP_ETHERSCAN_URL
) => `${url}/${operation}/${hash}`;

const numberFormatter = new Intl.NumberFormat(navigator.language, {
  notation: "compact",
  compactDisplay: "short",
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
});

const relativeTimeFormatter = new Intl.RelativeTimeFormat(navigator.language, {
  numeric: "always",
  style: "narrow",
});

const formatNumber = (number: number) =>
  number === 0 ? number : numberFormatter.format(number);

const formatRelativeDate = (date, unit = "day") => {
  //@ts-expect-error
  const parts = relativeTimeFormatter.formatToParts(date, unit);
  return parts
    .slice(1)
    .map((p) => p.value)
    .join("");
};

const getPnlColor = (pnl) => {
  if (pnl === 0) {
    return "text-white";
  }
  return pnl > 0 ? "text-accent-500" : "text-tertiary-500";
};

const _lastUniqBy = (arr, key) => _reverse(_uniqBy(_reverse(arr), key));

export {
  _exists,
  offsetToDate,
  dateToOffset,
  validValue,
  getUnderlyingsPriceMap,
  getEtherscanLink,
  formatNumber,
  formatRelativeDate,
  getPnlColor,
  _lastUniqBy,
};
