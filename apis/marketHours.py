"""
APIs for Market Hours
https://developer.tdameritrade.com/market-hours/apis
"""


import requests
from variables import globals


def getHoursForMultipleMarkets(markets, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return requests.get('https://api.tdameritrade.com/v1/marketdata/hours',
                        params={'apikey': globals.consumerKey, 'markets': markets, 'date': date},
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getHoursForASingleMarkets(market, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + market + '/hours',
                        params={'apikey': globals.consumerKey, 'date': date},
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()
