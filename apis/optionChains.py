"""
APIs for Option Chains
https://developer.tdameritrade.com/option-chains/apis
"""
import requests
from modules import universe, api
from apis import utilities


def getOptionChain(**kwargs):
    args = ["symbol", "contractType", "strikeCount", "includeQuotes", "strategy", "interval", "strike", "range", "fromDate", "toDate", "volatility", "underlyingPrice", "interestRate", "daysToExpiration", "expMonth", "optionType"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
