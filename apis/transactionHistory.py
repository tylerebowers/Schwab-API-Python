"""
APIs for Transaction History
https://developer.tdameritrade.com/transaction-history/apis
"""
import requests
from modules import globals, utilities, user


def getTransaction(transactionId):
    user.checkTokens()
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions/' + transactionId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getTransactions(**kwargs):
    user.checkTokens()
    args = ["type", "symbol", "startDate", "endDate"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/transactions',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))
