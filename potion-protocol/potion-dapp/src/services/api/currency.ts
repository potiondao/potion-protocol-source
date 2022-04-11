import ApiService from "../api.service";

const CurrencyService = {
  getEthToUsd: async function () {
    /**
     * Define the endpoint for the service
     */
    const resource =
      "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd";
    try {
      const response = await ApiService.get(resource);
      return response.data.ethereum.usd;
    } catch (error) {
      throw new Error(error);
    }
  },
};

export { CurrencyService };
