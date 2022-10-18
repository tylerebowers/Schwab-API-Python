"""
APIs for Accounts and Trading
https://developer.tdameritrade.com/account-access/apis
"""

import requests
from modules import globals, utilities, user


"""
Orders
"""


def cancelOrder(orderId):
    user.checkTokens()
    return utilities.responseHandler(
        requests.delete('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/orders/' + orderId,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getOrder(orderId):
    user.checkTokens()
    return utilities.responseHandler(
        requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/orders/' + orderId,
                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getOrdersByPath(**kwargs):  # times are entered as "yyyy-MM-dd"
    user.checkTokens()
    args = ["maxResults", "fromEnteredTime", "toEnteredTime", "status"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(
        requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/orders',
                     params=params,
                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getOrdersByQuery(**kwargs):
    user.checkTokens()
    args = ["accountId", "maxResults", "fromEnteredTime", "toEnteredTime", "status"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/orders/',
                                                 params=params,
                                                 headers={'Authorization': 'Bearer ' + globals.accessToken}))


def placeOrder(data):
    user.checkTokens()
    return utilities.responseHandler(
        requests.post('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/orders',
                      json=data,
                      headers={'Authorization': 'Bearer ' + globals.accessToken}))


def replaceOrder(orderId, data):
    user.checkTokens()
    return utilities.responseHandler(requests.put('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/orders/' + orderId,
                        json=data,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))


"""
Saved Orders
"""


def createSavedOrder(data):  # FIX
    user.checkTokens()
    return utilities.responseHandler(requests.post('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/savedorders',
                         json=data,
                         headers={'Authorization': 'Bearer ' + globals.accessToken}))


def deleteSavedOrder(savedOrderId):
    user.checkTokens()
    return utilities.responseHandler(requests.delete(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/savedorders/' + savedOrderId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getSavedOrder(savedOrderId):
    user.checkTokens()
    return utilities.responseHandler(requests.get(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/savedorders/' + savedOrderId,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getSavedOrdersByPath():
    user.checkTokens()
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/savedorders/',
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))


# not tested
def replaceSavedOrder(savedOrderId, data):  # FIX
    user.checkTokens()
    return utilities.responseHandler(requests.put(
        'https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/savedorders/' + savedOrderId,
        params=data,
        headers={'Authorization': 'Bearer ' + globals.accessToken}))


"""
Accounts
"""


# not tested
def getAccount(**kwargs):
    user.checkTokens()
    args = ["fields"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber,
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))


# not tested
def getAccounts(**kwargs):
    user.checkTokens()
    args = ["fields"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))


def examples():
    user.checkTokens()
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
