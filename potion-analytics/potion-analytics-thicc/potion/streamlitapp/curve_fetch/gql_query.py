"""
This file contains helper functions for interacting with the subgraph and querying curves that
might be out in the world. This info can help the user create curves in the simulator they may
want to test with.
"""
import time
import pandas as pd

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

GET_POTIONS_QUERY_STR = """
    query allPotions($num: Int, $unix_ts: BigInt!) {
      otokens(first: $num, where: { expiry_gt: $unix_ts  }) {
        id
        collateralAsset {
          name
          address
          symbol
        }
        collateralized
        creator
        expiry
        numberOfOTokens
        premium
        purchasesCount
        settled
        orderBook {
          timestamp
          premium
          numberOfOTokens
        }
        strikeAsset {
          name
          symbol
        }
        strikePrice
        underlyingAsset {
          name
          symbol
        }
      }
    }
    """


def create_gql_client(gql_url: str):
    """
    Creates and initializes a GraphQL client and returns a state dictionary with the relevant
    objects.

    Returns
    -------
    state : dict
        A dict containing the keys 'transport', 'client', and 'query'. Transport contains the
        transport method the client uses to query the graph. Client contains the client API object.
        Query contains the gql object containing the query.
    """
    transport = RequestsHTTPTransport(url=gql_url)

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(GET_POTIONS_QUERY_STR)

    return {
        'transport': transport,
        'client': client,
        'query': query
    }


def get_all_potions_query(state_dict, num_potions: int):
    """
    Executes the query which fetches a number of potions from the subgraph. The number can be
    specified by the input argument.

    Parameters
    ----------
    state_dict : dict
        The state dict containing the client
    num_potions : int
        The number of potions to query from the graph

    Returns
    -------
    potion_list : List
        A List containing all of the potions currently in use
    """
    params = {'num': num_potions, 'unix_ts': int(time.time())}

    result = state_dict['client'].execute(state_dict['query'], variable_values=params)

    return result['otokens']


def parse_query_results_to_df(potion_list):
    """
    Parses the List returned by the subgraph into a convenient DataFrame

    Parameters
    ----------
    potion_list : List
        The List of potions returned by the query

    Returns
    -------
    potion_df : pandas.DataFrame
        A DataFrame containing the asset, strike, and expiration info
    """

    # Extract the info we are interested in and transform it into 3 lists
    underlying_asset_list, strike_list, expiration_list = list(
        map(list, zip(*[[otoken['underlyingAsset']['symbol'], float(otoken['strikePrice']),
                         float(otoken['expiry'])] for otoken in potion_list])))

    # Construct a DataFrame backed by the lists
    otoken_df = pd.DataFrame({'Asset': underlying_asset_list, 'Strike': strike_list,
                              'Expiration': expiration_list},
                             columns=['Asset', 'Strike', 'Expiration'])

    # Transform the WETH and WBTC into the strings from the Historical Data Downloader Widget
    otoken_df['Asset'] = otoken_df['Asset'].map({'WETH': 'ethereum', 'WBTC': 'bitcoin'})

    # Calculate the number of days until the otoken expires
    otoken_df['Expiration'] = otoken_df['Expiration'].apply(
        lambda t: (float(t) - time.time()) / 86400.0)

    otoken_df.sort_values(['Asset', 'Strike', 'Expiration'], ascending=[True, True, True],
                          inplace=True, ignore_index=True)

    return otoken_df
