"""
APIs for Accounts and Trading
https://developer.tdameritrade.com/account-access/apis
"""

import requests
from modules import universe
from apis import utilities

"""
Orders
"""


def cancelOrder(orderId):
    return utilities.apiResponseHandler(
        requests.delete('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                        headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getOrder(orderId):
    return utilities.apiResponseHandler(
        requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getOrdersByPath(**kwargs):  # times are entered as "yyyy-MM-dd"
    args = ("maxResults", "fromEnteredTime", "toEnteredTime", "status")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(
        requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                     params=params,
                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getOrdersByQuery(**kwargs):
    args = ("accountId", "maxResults", "fromEnteredTime", "toEnteredTime", "status")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/orders/',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def placeOrder(data):
    return utilities.apiResponseHandler(
        requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                      json=data,
                      headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def replaceOrder(orderId, data):
    return utilities.apiResponseHandler(requests.put('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                                                     json=data,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


"""
Saved Orders  #THESE WILL BE REMOVED IN THE SCHWAB UPDATE
"""


def createSavedOrder(data):
    return utilities.apiResponseHandler(requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders',
                                                      json=data,
                                                      headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def deleteSavedOrder(savedOrderId):
    return utilities.apiResponseHandler(requests.delete(
        'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
        headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getSavedOrder(savedOrderId):
    return utilities.apiResponseHandler(requests.get(
        'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
        headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getSavedOrdersByPath():
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/',
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


# not tested
def replaceSavedOrder(savedOrderId, data):  # FIX
    return utilities.apiResponseHandler(requests.put(
        'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
        params=data,
        headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


"""
Accounts
"""


# not tested
def getAccount(**kwargs):
    args = ("fields")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber,
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


# not tested
def getAccounts(**kwargs):
    args = ("fields")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def examples():
    print("------------------------------------")
    print("Examples for: api-accountsAndTrading")
    print("------------------------------------")
    print("Orders do not have examples yet")
    print("------------------------------------")
    print("Saved Orders have not been tested an do not have examples")
    print("------------------------------------")
    print("accountsAndTrading.getAccount()")
    print(getAccount())
    print("------------------------------------")
    print("accountsAndTrading.getAccounts()")
    print(getAccounts())
    print("------------------------------------")
    return

