"""
This file contains all api requests and functions to initialize the program
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import requests
import threading
from modules import terminal
from datetime import datetime
from dotenv import load_dotenv
import os


class tokens:
    refreshToken = None
    accessToken = None
    idToken = None
    refreshTokenIssued = None
    accessTokenIssued = None
    refreshTokenTimeout = 7  # in days
    accessTokenTimeout = 1800  # in seconds


class credentials:
    appKey = None
    appSecret = None
    callbackUrl = None
    accountHash = None
    accountNumber = None


def initialize():
    # load credentials
    load_dotenv()
    credentials.appKey = os.getenv('appKey')
    credentials.appSecret = os.getenv('appSecret')
    credentials.callbackUrl = os.getenv('callbackUrl')

    # check if credentials are valid
    if len(credentials.appKey) != 32 or len(credentials.appSecret) != 16:
        terminal.colorPrint.error("No app key or app secret found, please add your app key and app secret in the .env file.")
        quit()

    # load tokens from file
    _TokenManager("init")  # this also sets variables for tokens and token timeouts
    # show user when tokens were last updated and when they will expire
    terminal.colorPrint.info(tokens.accessTokenIssued.strftime(
        "Access token last updated: %Y-%m-%d %H:%M:%S") + f" (expires in {tokens.accessTokenTimeout - (datetime.now() - tokens.accessTokenIssued).seconds} seconds)")
    terminal.colorPrint.info(tokens.refreshTokenIssued.strftime(
        "Refresh token last updated: %Y-%m-%d %H:%M:%S") + f" (expires in {tokens.refreshTokenTimeout - (datetime.now() - tokens.refreshTokenIssued).days} days)")
    # check if tokens need to be updated and update if needed
    _updateTokensManual()

    # get account numbers & hashes, this doubles to make sure that the appKey and appSecret are valid
    terminal.colorPrint.info("Filling account number and account hash -> ", end="")
    resp = accounts.accountNumbers()
    if resp.ok:
        d = resp.json()
        if len(d) == 1:  # only one account
            credentials.accountNumber = d[0].get('accountNumber', None)
            credentials.accountHash = d[0].get('hashValue', None)
            print("Done.")
        else:  # multiple accounts, we must choose one to place orders
            print("Input required.")
            terminal.colorPrint.user("Multiple accounts found, you need to choose the one to place orders with.")
            terminal.colorPrint.user("Options: [" + ", ".join([f"{i + 1}={d[i].get('accountNumber', 'N/A')}" for i in range(len(d))]) + "]")
            sel = int(terminal.colorPrint.input(f"Select one by number ({', '.join([str(i + 1) for i in range(len(d))])}): ")) - 1
            credentials.accountNumber = d[sel].get('accountNumber', None)
            credentials.accountHash = d[sel].get('hashValue', None)
    else:  # app might not be "Ready For Use"
        print("Error.")
        terminal.colorPrint.error("Could not get account numbers and account hash.")
        terminal.colorPrint.error(
            "Please make sure that your app status is \"Ready For Use\" and that the app key and app secret are valid.")
        terminal.colorPrint.error(resp.json())
    resp.close()

    terminal.colorPrint.info("Initialization Complete")


def _updateTokensManual():
    if (datetime.now() - tokens.refreshTokenIssued).days >= (
            tokens.refreshTokenTimeout - 1):  # check if we need to update refresh (and access) token
        terminal.colorPrint.user("The refresh token has expired, please update!")  # print multiple times?
        _RefreshTokenUpdate()
    elif ((datetime.now() - tokens.accessTokenIssued).days >= 1) or (
            (datetime.now() - tokens.accessTokenIssued).seconds > (
            tokens.accessTokenTimeout - 60)):  # check if we need to update access token
        terminal.colorPrint.info("The access token has expired, updating automatically.")
        _AccessTokenUpdate()
    # else: terminal.colorPrint.info("Token check passed")


def updateTokensAutomatic():
    def checker():
        import time
        while True:
            _updateTokensManual()
            time.sleep(60)

    threading.Thread(target=checker, daemon=True).start()


def _AccessTokenUpdate():
    # get the token dictionary (we will need to rewrite the wile)
    accessTokenFileTime, refreshTokenFileTime, tokenDictionary = _TokenManager("getFile")
    # get new tokens
    response = _PostAccessTokenAutomated('refresh_token', tokenDictionary.get("refresh_token"))
    if response.ok:
        newTokenDictionary = response.json()
        # get and update to the new access token
        _TokenManager("set", datetime.now(), refreshTokenFileTime, newTokenDictionary)
        # show user that we have updated the access token
        terminal.colorPrint.info(f"Access token updated: {tokens.accessTokenIssued}")
    else:
        terminal.colorPrint.error("Could not get new access token.")


def _RefreshTokenUpdate():
    import webbrowser
    # get authorization code (requires user to authorize)
    terminal.colorPrint.user("Please authorize this program to access your schwab account.")
    authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={credentials.appKey}&redirect_uri={credentials.callbackUrl}'
    terminal.colorPrint.user(f"Click to authenticate: {authUrl}")
    terminal.colorPrint.info("Opening browser...")
    webbrowser.open(authUrl)
    responseURL = terminal.colorPrint.input("After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    code = f"{responseURL[responseURL.index('code=') + 5:responseURL.index('%40')]}@"  # session = responseURL[responseURL.index("session=")+8:]
    # get new access and refresh tokens
    response = _PostAccessTokenAutomated('authorization_code', code)
    if response.ok:
        newTokenDictionary = response.json()
        # update token file and variables
        _TokenManager("set", datetime.now(), datetime.now(), newTokenDictionary)
        terminal.colorPrint.info("Refresh and Access tokens updated")
    else:
        terminal.colorPrint.error("Could not get new refresh and access tokens.")
        terminal.colorPrint.error(
            "Please make sure that your app status is \"Ready For Use\" and that the app key and app secret are valid.")


def _TokenManager(action="init", at=None, rt=None, td=None):
    fileName = "tokens.json"

    def writeTokenVars(nat, nrt, ntd):
        tokens.refreshToken = ntd.get("refresh_token")
        tokens.accessToken = ntd.get("access_token")
        tokens.id_token = ntd.get("id_token")
        tokens.accessTokenIssued = nat
        tokens.refreshTokenIssued = nrt

    def writeTokenFile(atIssued, rtIssued, tokenDictionary):
        toWrite = {"accessTokenIssued": atIssued.isoformat(), "refreshTokenIssued": rtIssued.isoformat(),
                   "tokenDictionary": tokenDictionary}
        with open(fileName, 'w') as f:
            json.dump(toWrite, f, ensure_ascii=False, indent=4)
            f.flush()

    def readTokenFile():
        with open(fileName, 'r') as f:
            d = json.load(f)
            return datetime.fromisoformat(d.get("accessTokenIssued")), datetime.fromisoformat(
                d.get("refreshTokenIssued")), d.get("tokenDictionary")

    try:
        if action == "getFile":
            return readTokenFile()
        elif action == "set":
            if at is not None and rt is not None and td is not None:
                writeTokenFile(at, rt, td)
                writeTokenVars(at, rt, td)
            else:
                terminal.colorPrint.error("Error in setting token file, null values given.")
        elif action == "init":
            at, rt, td = readTokenFile()
            writeTokenVars(at, rt, td)
    except Exception as e:
        terminal.colorPrint.error("Error in reading/writing token file, creating new token file.")
        open(fileName, 'w').close()
        _RefreshTokenUpdate()


def _PostAccessTokenAutomated(grant_type, code):
    import base64
    headers = {
        'Authorization': f'Basic {base64.b64encode(bytes(f"{credentials.appKey}:{credentials.appSecret}", "utf-8")).decode("utf-8")}',
        'Content-Type': 'application/x-www-form-urlencoded'}
    if grant_type == 'authorization_code':
        data = {'grant_type': 'authorization_code', 'code': code,
                'redirect_uri': credentials.callbackUrl,
                'client_id': credentials.appKey}
    elif grant_type == 'refresh_token':
        data = {'grant_type': 'refresh_token', 'refresh_token': code}  # refreshes the access token
    else:
        terminal.colorPrint.error("Invalid grant type")
        return None
    return requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)


"""
Below here are all the api calls and functions that they use.
"""


def _ParamsParser(params):
    for key in list(params.keys()):
        if params[key] is None: del params[key]
    return params


def _TimeConvert(dt=None, form="8601"):
    if dt is None:
        return None
    elif dt is str:
        return dt
    elif form == "8601":
        return f'{dt.isoformat()[:-3]}Z'
    elif form == "epoch":
        return int(dt.timestamp() * 1000)
    elif form == "YYYY-MM-DD":
        return dt.strftime("%Y-%M-%d")
    else:
        return dt


def formatList(l):  # could also encode symbols here
    if l is None:
        return None
    elif l is list == str:
        return l
    else:
        return ",".join(l)


"""
Accounts and Trading Production
"""
atp_url = "https://api.schwabapi.com/trader/v1"


class accounts:

    @staticmethod
    def accountNumbers():  # /accounts/accountNumbers
        return requests.get(f'{atp_url}/accounts/accountNumbers',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod
    def getAllAccounts(fields=None):  # /accounts
        return requests.get(f'{atp_url}/accounts/', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'fields': fields}))

    @staticmethod  # /accounts/{accountHash}
    def getAccount(fields=None, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'fields': fields}))


class orders:
    @staticmethod  # /accounts/{accountHash}/orders
    def getOrders(maxResults, fromEnteredTime, toEnteredTime, status=None, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser(
                                {'maxResults': maxResults, 'fromEnteredTime': _TimeConvert(fromEnteredTime),
                                 'toEnteredTime': _TimeConvert(toEnteredTime), 'status': status}))

    @staticmethod  # /accounts/{accountHash}/orders
    def placeOrder(order, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.post(f'{atp_url}/accounts/{accountHash}/orders',
                             headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}',
                                      "Content-Type": "application/json"}, json=order)

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def getOrder(orderId, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/orders/{orderId}',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def cancelOrder(orderId, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.delete(f'{atp_url}/accounts/{accountHash}/orders/{orderId}',
                               headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def replaceOrder(orderId, order, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.put(f'{atp_url}/accounts/{accountHash}/orders/{orderId}',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}',
                                     "Content-Type": "application/json"}, json=order)

    @staticmethod  # /orders
    def getAllOrders(maxResults, fromEnteredTime, toEnteredTime, status=None):
        return requests.get(f'{atp_url}/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser(
                                {'maxResults': maxResults, 'fromEnteredTime': _TimeConvert(fromEnteredTime),
                                 'toEnteredTime': _TimeConvert(toEnteredTime), 'status': status}))

    """ #COMING SOON (waiting on Schwab)
    @staticmethod  # /accounts/{accountHash}/previewOrder
    def previewOrder(orderObject, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.post(f'{atp_url}/accounts/{accountHash}/previewOrder',
                             headers={'Authorization': f'Bearer {tokens.accessToken}',
                                      "Content-Type": "application.json"}, data=orderObject)

    """


class transactions:
    @staticmethod  # /accounts/{accountHash}/transactions
    def transactions(startDate, endDate, types, symbol=None, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/transactions',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser(
                {'accountNumber': accountHash, 'startDate': _TimeConvert(startDate), 'endDate': _TimeConvert(endDate),
                 'symbol': symbol, 'types': types}))

    @staticmethod  # /accounts/{accountHash}/transactions/{transactionId}
    def details(transactionId, accountHash=None):
        if accountHash is None: accountHash = credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/transactions/{transactionId}',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params={'accountNumber': accountHash, 'transactionId': transactionId})


class userPreference:
    @staticmethod  # /userPreference
    def userPreference():
        return requests.get(f'{atp_url}/userPreference', headers={'Authorization': f'Bearer {tokens.accessToken}'})


"""
Market Data
"""
mkt_url = "https://api.schwabapi.com/marketdata/v1"


class quotes:
    @staticmethod  # /quotes
    def getList(symbols=None, fields=None, indicative=False):
        return requests.get(f'{mkt_url}/quotes', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser(
                                {'symbols': formatList(symbols), 'fields': fields, 'indicative': indicative}))

    @staticmethod  # /{symbol_id}/quotes
    def getSingle(symbol_id, fields=None):
        return requests.get(f'{mkt_url}/{symbol_id}/quotes', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'fields': fields}))


class options:
    @staticmethod  # /chains
    def chains(symbol, contractType=None, strikeCount=None, includeUnderlyingQuotes=None, strategy=None, interval=None,
               strike=None, range=None, fromDate=None, toDate=None, volatility=None, underlyingPrice=None,
               interestRate=None, daysToExpiration=None, expMonth=None, optionType=None, entitlement=None):
        return requests.get(f'{mkt_url}/chains', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser(
                                {'symbol': symbol, 'contractType': contractType, 'strikeCount': strikeCount,
                                 'includeUnderlyingQuotes': includeUnderlyingQuotes, 'strategy': strategy,
                                 'interval': interval, 'strike': strike, 'range': range, 'fromDate': fromDate,
                                 'toDate': toDate, 'volatility': volatility, 'underlyingPrice': underlyingPrice,
                                 'interestRate': interestRate, 'daysToExpiration': daysToExpiration,
                                 'expMonth': expMonth, 'optionType': optionType, 'entitlement': entitlement}))

    @staticmethod  # /expirationchain
    def expirationChain(symbol):
        return requests.get(f'{mkt_url}/expirationchain', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'symbol': symbol}))


class priceHistory:
    @staticmethod  # /pricehistory
    def bySymbol(symbol, periodType=None, period=None, frequencyType=None, frequency=None, startDate=None,
                        endDate=None, needExtendedHoursData=None, needPreviousClose=None):
        return requests.get(f'{mkt_url}/pricehistory', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'symbol': symbol, 'periodType': periodType, 'period': period,
                                                  'frequencyType': frequencyType, 'frequency': frequency,
                                                  'startDate': _TimeConvert(startDate, 'epoch'),
                                                  'endDate': _TimeConvert(endDate, 'epoch'),
                                                  'needExtendedHoursData': needExtendedHoursData,
                                                  'needPreviousClose': needPreviousClose}))


class movers:
    @staticmethod  # /movers
    def getMovers(symbol, sort=None, frequency=None):
        return requests.get(f'{mkt_url}/movers/{symbol}', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'sort': sort, 'frequency': frequency}))


class marketHours:
    @staticmethod  # /markets
    def byMarkets(symbol, date=None):
        return requests.get(f'{mkt_url}/markets', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'markets': symbol, 'date': _TimeConvert(date, 'YYYY-MM-DD')}))

    @staticmethod  # /markets/{market_id}
    def byMarket(market_id, date=None):
        return requests.get(f'{mkt_url}/markets/{market_id}', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params=_ParamsParser({'date': _TimeConvert(date, 'YYYY-MM-DD')}))


class instruments:
    @staticmethod  # /instruments
    def bySymbol(symbol, projection):
        return requests.get(f'{mkt_url}/instruments', headers={'Authorization': f'Bearer {tokens.accessToken}'},
                            params={'symbol': symbol, 'projection': projection})

    @staticmethod  # /instruments/{cusip}
    def byCusip(cusip_id):
        return requests.get(f'{mkt_url}/instruments/{cusip_id}',
                            headers={'Authorization': f'Bearer {tokens.accessToken}'})
