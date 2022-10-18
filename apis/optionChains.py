"""
APIs for Option Chains
https://developer.tdameritrade.com/option-chains/apis
"""
import requests
from modules import globals, utilities, user

def getOptionChain(**kwargs):
    user.checkTokens()
    args = ["symbol", "contractType", "strikeCount", "includeQuotes", "strategy", "interval", "strike", "range", "fromDate", "toDate", "volatility", "underlyingPrice", "interestRate", "daysToExpiration", "expMonth", "optionType"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))
