"""
APIs for Market Hours
https://developer.tdameritrade.com/market-hours/apis
"""

import requests
from modules import globals, api
from apis import utilities


def getHoursForMultipleMarkets(markets, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/hours',
                                                     params={'apikey': globals.consumerKey, 'markets': markets,
                                                         'date': date},
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getHoursForASingleMarkets(market, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/' + market + '/hours',
                                                     params={'apikey': globals.consumerKey, 'date': date},
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))
