export const timePeriodEpochMilliSeconds = function (days) {
  return new Date().setDate(new Date().getDate() - days);
};

export const timePeriodEpochSeconds = function (milliseconds) {
  return Math.floor(milliseconds / 1000);
};
