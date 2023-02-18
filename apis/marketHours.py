"""
APIs for Market Hours
https://developer.tdameritrade.com/market-hours/apis
"""

import requests
from modules import universe
from apis import utilities


def getHoursForMultipleMarkets(markets, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/hours',
                                                     params={'apikey': universe.credentials.credentials.consumerKey, 'markets': markets,
                                                         'date': date},
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getHoursForASingleMarkets(market, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/' + market + '/hours',
                                                     params={'apikey': universe.credentials.consumerKey, 'date': date},
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
