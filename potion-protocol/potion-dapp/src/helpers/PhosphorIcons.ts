const iconWeights = ["bold", "fill", "light", "thin", "regular"];
const strokeWeightMap = {
  bold: 24,
  light: 12,
  thin: 8,
  regular: 16,
};

const weightValidator = (value) => iconWeights.includes(value);
const weightToStroke = (weight) => strokeWeightMap[weight];

export { weightValidator, weightToStroke };
