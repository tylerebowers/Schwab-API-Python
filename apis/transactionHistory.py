"""
APIs for Transaction History
https://developer.tdameritrade.com/transaction-history/apis
"""
import requests
from modules import universe, api
from apis import utilities


def getTransaction(transactionId):
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions/' + transactionId,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getTransactions(**kwargs):
    args = ("type", "symbol", "startDate", "endDate")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
