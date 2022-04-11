import axios from "redaxios";

/**
 * This object wraps the basic axios methods
 */
const ApiService = {
  init(baseURL: string) {
    /**
     * We can set the base url for the endpoint.
     * Best practice should be having more than one instance of axios (one per endpoint)
     * we can do this by `axios.create()`
     */
    axios.defaults.baseURL = baseURL;
    axios.defaults.headers.common["Accept"] = "application/json";
  },
  get(resource: string) {
    return axios.get(resource);
  },
  post(resource: string, data: any) {
    return axios.post(resource, data);
  },
  graphql(resource: string, query: string, variables = {}) {
    return axios.post(resource, {
      query,
      variables,
    });
  },
};

export default ApiService;
