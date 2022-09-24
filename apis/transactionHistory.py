"""
APIs for Transaction History
https://developer.tdameritrade.com/transaction-history/apis
"""
import requests
from variables import globals


def getTransaction(transactionId):
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions/' + transactionId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getTransactions(**kwargs):
    args = ["type", "symbol", "startDate", "endDate"]
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()
