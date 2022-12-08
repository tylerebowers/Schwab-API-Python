"""
APIs for Watchlist
https://developer.tdameritrade.com/watchlist/apis
"""

import requests
from modules import globals, api
from apis import utilities


# not tested
def createWatchlist(data):  # FIX
    return utilities.apiResponseHandler(
        requests.post('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists',
                      json=data,
                      headers={'Authorization': 'Bearer ' + globals.accessToken}))


def deleteWatchlist(watchListId):  # FIX
    return utilities.apiResponseHandler(requests.delete(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getWatchlist(watchListId):  # FIX
    return utilities.apiResponseHandler(requests.get(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getWatchlistsForMultipleAccounts():  # FIX
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/watchlists',
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getWatchlistsForSingleAccount():  # FIX
    return utilities.apiResponseHandler(
        requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists',
                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def replaceWatchlist(watchListId, data):  # FIX
    return utilities.apiResponseHandler(requests.post(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        json=data, headers={'Authorization': 'Bearer ' + globals.accessToken}))


def updateWatchlist(watchListId, data):  # FIX
    return utilities.apiResponseHandler(requests.patch(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        json=data, headers={'Authorization': 'Bearer ' + globals.accessToken}))


'''
# data for watchlists
{
    "name": "string",
    "watchlistItems": [
        {
            "quantity": 0,
            "averagePrice": 0,
            "commission": 0,
            "purchasedDate": "DateParam\"",
            "instrument": {
                "symbol": "string",
                "assetType": "'EQUITY' or 'OPTION' or 'MUTUAL_FUND' or 'FIXED_INCOME' or 'INDEX'"
            }
        }
    ]
}
'''
