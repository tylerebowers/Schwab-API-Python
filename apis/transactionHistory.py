"""
APIs for Transaction History
https://developer.tdameritrade.com/transaction-history/apis
"""
import requests
from variables import credentials


def getTransaction(transactionId):
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountNumber + '/transactions/' + transactionId,
        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()


def getTransactions(**kwargs):
    args = ["type", "symbol", "startDate", "endDate"]
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountNumber + '/transactions',
                        params=params,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()
