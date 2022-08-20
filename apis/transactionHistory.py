# https://developer.tdameritrade.com/transaction-history/apis
import requests
from variables import credentials


def getTransaction(transactionId):  # Working
    return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountNumber + '/transactions/' + transactionId,
                            headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()

def getTransactions(type, ):  # NOT ADDED YET
        return requests.get('https://api.tdameritrade.com/v1/accounts/' + credentials.accountNumber + '/transactions',
                                params={},
                                headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()
