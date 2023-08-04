"""
This file contains all api requests and functions to initialize the program
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Client
"""

import json
import time
import urllib
import requests
from modules import universe
from datetime import datetime



def initialize():
    if len(universe.credentials.consumerKey) != 32:
        universe.terminal.error("Please check to make sure that you have your consumer key in modules/universe.py")
        universe.terminal.info("If you do have the key and this check is failing you can remove it in modules/api.py")
        quit()
    try:
        with open('modules/tokens.txt', 'r') as file:
            accessTokenFileTime = file.readline().strip('\n')
            refreshTokenFileTime = file.readline().strip('\n')
            tokenDictionary = json.loads(file.readline())
            file.flush()
            file.close()
    except:
        universe.terminal.error("Error in reading from file.")
        universe.terminal.info(
            "Please make sure that modules/tokens.txt exists and that your environment is setup correctly (ie running "
            "program from main.py).")
        quit()
    universe.terminal.info("" + accessTokenFileTime)
    universe.terminal.info("" + refreshTokenFileTime)
    universe.tokens.accessTokenDateTime = datetime.strptime(accessTokenFileTime,
                                                            "Access token last updated: %d/%m/%y %H:%M:%S")
    universe.tokens.refreshTokenDateTime = datetime.strptime(refreshTokenFileTime,
                                                             "Refresh token last updated: %d/%m/%y %H:%M:%S")
    if (datetime.now() - universe.tokens.refreshTokenDateTime).days >= 89:
        universe.terminal.error("The refresh token has expired, please update.")
        _RefreshTokenUpdate()
    elif (datetime.now() - universe.tokens.accessTokenDateTime).days >= 1 or (
            (datetime.now() - universe.tokens.accessTokenDateTime).seconds > (
            (universe.tokens.authTokenTimeout * 60) - 60)):
        universe.terminal.info("The access token has expired, updating automatically.")
        _AccessTokenUpdate()
    else:
        universe.tokens.accessToken = tokenDictionary.get("access_token")
        universe.tokens.refreshToken = tokenDictionary.get("refresh_token")
    universe.terminal.info(
        f"Refresh token expires in {90 - (datetime.now() - universe.tokens.refreshTokenDateTime).days} days!")
    universe.terminal.info("Initialization Complete")


def _RefreshTokenUpdate():
    print("[INPUT]: Click to authenticate: " + "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=" +
          urllib.parse.quote(universe.credentials.callbackUrl,
                             safe='') + "&client_id=" + universe.credentials.consumerKey + "%40AMER.OAUTHAP")
    responseURL = input("[INPUT]: After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    authCode = urllib.parse.unquote(responseURL.split("code=")[1])
    newTokens = _PostAccessTokenAutomated('authorization_code', authCode)
    universe.tokens.accessTokenDateTime = datetime.now()
    universe.tokens.refreshTokenDateTime = datetime.now()
    with open('modules/tokens.txt', 'w') as file:
        file.write(universe.tokens.accessTokenDateTime.strftime("Access token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(
            universe.tokens.refreshTokenDateTime.strftime("Refresh token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(json.dumps(newTokens))
        file.flush()
        file.close()
    universe.tokens.accessToken = newTokens.get("access_token")
    universe.tokens.refreshToken = newTokens.get("refresh_token")
    universe.terminal.info("Refresh and Access tokens updated")


def _AccessTokenUpdate():
    with open('modules/tokens.txt', 'r') as file:
        file.readline()
        refreshTokenFileTime = file.readline()
        dictionary = json.loads(file.readline())
        file.close()
    try:
        newAccessToken = _PostAccessTokenAutomated('refresh_token', dictionary.get("refresh_token"))
    except Exception as e:
        newAccessToken = dictionary
        print(e)
        for i in range(3): universe.terminal.warning(
            "Problem with access token request, check your internet connection!")
    dictionary['access_token'] = newAccessToken.get('access_token')
    with open('modules/tokens.txt', 'w') as file:
        file.write(datetime.now().strftime("Access token last updated: %d/%m/%y %H:%M:%S"))
        file.write("\n" + refreshTokenFileTime)
        file.write(json.dumps(dictionary))
        file.flush()
        file.close()
    universe.tokens.accessToken = dictionary.get("access_token")
    universe.tokens.refreshToken = dictionary.get("refresh_token")
    universe.tokens.accessTokenDateTime = datetime.now()
    universe.terminal.info(f"Access token updated: {universe.tokens.accessTokenDateTime}")


def _PostAccessTokenAutomated(grant_type, code):
    if grant_type == 'authorization_code':
        data = {'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code,
                'client_id': universe.credentials.consumerKey, 'redirect_uri': universe.credentials.callbackUrl}
        return authentication.postAccessToken(data)
    elif grant_type == 'refresh_token':
        data = {'grant_type': 'refresh_token', 'refresh_token': code,
                'client_id': universe.credentials.consumerKey}
        return authentication.postAccessToken(data)


def checkTokensManual():
    if (datetime.now() - universe.tokens.refreshTokenDateTime).days > 89:
        for i in range(3): universe.terminal.warning("The refresh token has expired, please update!")
        _RefreshTokenUpdate()
    elif (datetime.now() - universe.tokens.accessTokenDateTime).days >= 1 or (
            (datetime.now() - universe.tokens.accessTokenDateTime).seconds > (
            (universe.tokens.authTokenTimeout * 60) - 120)):
        universe.terminal.info("The access token has expired, updating automatically.")
        _AccessTokenUpdate()


def _checkTokensDaemon():
    while True:
        checkTokensManual()
        time.sleep(60)


def _responseHandler(response):
    if universe.preferences.printResponseCode: print(response)
    try:
        if response.ok:
            return response.json()
    except json.decoder.JSONDecodeError:
        return "[INFO] Nothing Returned"
    except AttributeError:
        return "[ERROR] Something else has been returned"


def _kwargsHandler(args, kwargs):
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return params


class accountsAndTrading:
    """
    Orders
    """

    @staticmethod
    def cancelOrder(orderId):
        return _responseHandler(
            requests.delete(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getOrder(orderId):
        return _responseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getOrdersByPath(**kwargs):  # times are entered as "yyyy-MM-dd"
        args = ("maxResults", "fromEnteredTime", "toEnteredTime", "status")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getOrdersByQuery(**kwargs):
        args = ("accountId", "maxResults", "fromEnteredTime", "toEnteredTime", "status")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/orders/',
                                             params=params,
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def placeOrder(data):
        return _responseHandler(
            requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                          json=data,
                          headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def replaceOrder(orderId, data):
        return _responseHandler(requests.put(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
            json=data,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    Saved Orders THESE ARE GETTING REMOVED
    """

    @staticmethod
    def createSavedOrder(data):  # FIX
        return _responseHandler(
            requests.post(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders',
                json=data,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def deleteSavedOrder(savedOrderId):
        return _responseHandler(requests.delete(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/'
            + savedOrderId, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getSavedOrder(savedOrderId):
        return _responseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/'
            + savedOrderId, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getSavedOrdersByPath():
        return _responseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/',
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def replaceSavedOrder(savedOrderId, data):  # FIX
        return _responseHandler(requests.put(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
            params=data,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    Accounts
    """

    @staticmethod
    def getAccount(**kwargs):
        args = ("fields")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber,
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getAccounts(**kwargs):
        args = ("fields")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/',
                                             params=params,
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))



class authentication:
    @staticmethod
    def postAccessToken(data):
        return _responseHandler(requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                              data=data))


class instruments:
    @staticmethod
    def searchInstruments(symbol, projection):
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/instruments',
                                             params={'symbol': symbol, 'projection': projection},
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))


    @staticmethod
    def getInstrument(cusip):
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/instruments/' + str(cusip),
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class marketHours:
    @staticmethod
    def getHoursForMultipleMarkets(markets, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/hours',
                                             params={'apikey': universe.credentials.consumerKey, 'markets': markets,
                                                     'date': date},
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getHoursForASingleMarkets(market, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + market + '/hours',
                         params={'apikey': universe.credentials.consumerKey, 'date': date},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class movers:
    @staticmethod
    def getMovers(index, **kwargs):  # Working
        args = ("direction", "change")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + index + '/movers',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class optionChains:
    @staticmethod
    def getOptionChain(**kwargs):
        args = ("symbol", "contractType", "strikeCount", "includeQuotes", "strategy", "interval", "strike", "range",
                "fromDate", "toDate", "volatility", "underlyingPrice", "interestRate", "daysToExpiration", "expMonth",
                "optionType")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                                             params=params,
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class priceHistory:
    @staticmethod
    def getPriceHistory(ticker, **kwargs):
        args = ("periodType", "period", "frequencyType", "frequency", "endDate", "startDate", "needExtendedHoursData")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + ticker + '/pricehistory',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class quotes:

    @staticmethod
    def getQuote(ticker):  # pass in a single ticker="AMD" and receive a real-time quote.
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                         params={'apikey': universe.credentials.consumerKey},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getQuotes(
            tickerList):  # pass in a list tickerList=["AMD","APPL"] and receive a real-time quote on the tickers.
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/quotes',
                                             params={'apikey': universe.credentials.consumerKey,
                                                     'symbol': ",".join(map(str, tickerList))},
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getDelayedQuote(ticker):  # pass in a single ticker="AMD" and receive a ~15min delayed quote.
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                         params={'apikey': universe.credentials.consumerKey}))



class transactionHistory:
    @staticmethod
    def getTransaction(transactionId):
        return _responseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions/'
            + str(transactionId), headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getTransactions(**kwargs):
        args = ("type", "symbol", "startDate", "endDate")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions',
                params=params,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class userInfoAndPreferences:
    @staticmethod
    def getPreferences():
        return _responseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/preferences',
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getStreamerSubscriptionKeys():
        return _responseHandler(
            requests.get('https://api.tdameritrade.com/v1/userprincipals/streamersubscriptionkeys',
                         params={'accountIds': universe.credentials.accountNumber},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
        # example of what is returned: {"keys": [{"key": "c7fb2_this_is_not_a_real_key_6c169b"}]}

    @staticmethod  # fields is a list of (streamerSubscriptionKeys, streamerConnectionInfo, preferences, surrogateIds)
    def getUserPrincipals(**kwargs):
        args = ("fields")
        params = _kwargsHandler(args, kwargs)
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/userprincipals',
                                             params=params,
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def updatePreferences(data):  # I could only get this to work through the dev website for some reason
        return _responseHandler(
            requests.put(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/preferences',
                json=data,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken,
                         'Content-Type': 'application/json'}))


class watchlist:
    @staticmethod
    def createWatchlist(data):  # FIX
        return _responseHandler(
            requests.post(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists',
                json=data,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def deleteWatchlist(watchListId):  # FIX
        return _responseHandler(requests.delete(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/'
            + watchListId, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getWatchlist(watchListId):  # FIX
        return _responseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/'
            + watchListId, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getWatchlistsForMultipleAccounts():  # FIX
        return _responseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/watchlists',
                                             headers={
                                                 'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getWatchlistsForSingleAccount():  # FIX
        return _responseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists',
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def replaceWatchlist(watchListId, data):  # FIX
        return _responseHandler(requests.post(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/'
            + watchListId, json=data, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def updateWatchlist(watchListId, data):  # FIX
        return _responseHandler(requests.patch(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/'
            + watchListId, json=data, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

