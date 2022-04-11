import ApiService from "../api.service";

const getGas = async () => {
  const resource = `https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=${process.env.VUE_APP_ETHERSCAN_KEY}`;
  try {
    const response = await ApiService.get(resource);
    return response.data.result;
  } catch (error) {
    throw new Error(error);
  }
};

export { getGas };
