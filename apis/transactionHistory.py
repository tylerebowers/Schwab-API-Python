"""
APIs for Transaction History
https://developer.tdameritrade.com/transaction-history/apis
"""
import requests
from modules import globals, api
from apis import utilities


def getTransaction(transactionId):
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions/' + transactionId,
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getTransactions(**kwargs):
    args = ["type", "symbol", "startDate", "endDate"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))
