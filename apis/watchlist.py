"""
APIs for Watchlist
https://developer.tdameritrade.com/watchlist/apis
"""

import requests
from variables import globals


# not tested
def createWatchlist(data):  # FIX
    return requests.post('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists',
                         data=data,
                         headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def deleteWatchlist(watchListId):  # FIX
    return requests.delete(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getWatchlist(watchListId):  # FIX
    return requests.get(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getWatchlistsForMultipleAccounts():  # FIX
    return requests.get('https://api.tdameritrade.com/v1/accounts/watchlists',
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getWatchlistsForSingleAccount():  # FIX
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists',
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def replaceWatchlist(watchListId, data):  # FIX
    return requests.post('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        data=data,
        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def updateWatchlist(watchListId, data):  # FIX
    return requests.patch('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/watchlists/' + watchListId,
        data=data,
        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


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
