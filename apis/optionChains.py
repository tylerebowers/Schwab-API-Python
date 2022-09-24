"""
APIs for Option Chains
https://developer.tdameritrade.com/option-chains/apis
"""
import requests
from variables import globals


def getOptionChain(**kwargs):
    args = ["symbol", "contractType", "strikeCount", "includeQuotes", "strategy", "interval", "strike", "range", "fromDate", "toDate", "volatility", "underlyingPrice", "interestRate", "daysToExpiration", "expMonth", "optionType"]
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()
