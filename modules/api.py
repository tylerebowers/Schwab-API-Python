"""
This file contains all api requests and functions to initialize the program
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import requests
import threading
from modules import universe
from datetime import datetime


class tokens:
    refreshToken = None
    accessToken = None
    idToken = None
    refreshTokenDateTime = None
    accessTokenDateTime = None
    refreshTokenTimeout = 7 # in days
    accessTokenTimeout = 1800 # in seconds


def initialize():

    if len(universe.credentials.appKey) != 32 or len(universe.credentials.appSecret) != 16:
        universe.cTerm.error("No app key or app secret found, please add your app key in modules/universe.credentials.appKey")
        quit()

    # load token from file
    _TokenManager("init")  # this also sets universe variables for tokens and token timeouts
    # show user when tokens were last updated
    universe.cTerm.info(tokens.accessTokenDateTime.strftime("Access token last updated: %Y-%m-%d %H:%M:%S"))
    universe.cTerm.info(tokens.refreshTokenDateTime.strftime("Refresh token last updated: %Y-%m-%d %H:%M:%S"))
    # check if tokens need to be updated and update if needed
    updateTokensManual()

    # show user when tokens will expire & complete initialization
    universe.cTerm.warning(f"Access token expires in {tokens.accessTokenTimeout - (datetime.now() - tokens.accessTokenDateTime).seconds} seconds!")
    universe.cTerm.warning(f"Refresh token expires in {tokens.refreshTokenTimeout - (datetime.now() - tokens.refreshTokenDateTime).days} days!")

    # get account numbers & hashes
    universe.cTerm.info("Filling account number and account hash...")
    resp = accounts.accountNumbers()
    if resp.ok:
        universe.credentials.accountNumber = resp.json()[0].get('accountNumber', None)
        universe.credentials.accountHash = resp.json()[0].get('hashValue', None)
    else:
        universe.cTerm.error("Could not get account numbers and account hash.")
    
    universe.cTerm.info("Initialization Complete")


def updateTokensManual():
    if (datetime.now() - tokens.refreshTokenDateTime).days >= (tokens.refreshTokenTimeout-1): #check if we need to update refresh (and access) token
        universe.cTerm.user("The refresh token has expired, please update!") # print multiple times?
        _RefreshTokenUpdate()
    elif ((datetime.now() - tokens.accessTokenDateTime).days >= 1) or ((datetime.now() - tokens.accessTokenDateTime).seconds > (tokens.accessTokenTimeout - 60)): #check if we need to update access token
        universe.cTerm.info("The access token has expired, updating automatically.")
        _AccessTokenUpdate()
    #else: universe.cTerm.info("Token check passed")

def updateTokensAutomatic():
    def checker():
        import time
        while True:
            updateTokensManual()
            time.sleep(60)
    threading.Thread(target=checker, daemon=True).start()


def _AccessTokenUpdate():
    # get the token dictionary (we will need to rewrite the wile)
    accessTokenFileTime, refreshTokenFileTime, tokenDictionary = _TokenManager("getFile")
    # get and update to the new access token
    _TokenManager("set", datetime.now(), refreshTokenFileTime, _PostAccessTokenAutomated('refresh_token', tokenDictionary.get("refresh_token")))
    # show user that we have updated the access token
    universe.cTerm.info(f"Access token updated: {tokens.accessTokenDateTime}")


def _RefreshTokenUpdate():
    import webbrowser
    # get authorization code (requires user to authorize)
    universe.cTerm.user("Please authorize this program to access your schwab account.")
    authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={universe.credentials.appKey}&redirect_uri={universe.credentials.callbackUrl}'
    universe.cTerm.user(f"Click to authenticate: {authUrl}")
    universe.cTerm.info("Opening browser...")
    webbrowser.open(authUrl)
    responseURL = universe.cTerm.input("After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    code = f"{responseURL[responseURL.index('code=')+5:responseURL.index('%40')]}@"  #session = responseURL[responseURL.index("session=")+8:]
    # get new access and refresh tokens
    tokenDictionary = _PostAccessTokenAutomated('authorization_code', code)
    # update token file and variables
    _TokenManager("set", datetime.now(), datetime.now(), tokenDictionary)
    universe.cTerm.info("Refresh and Access tokens updated")


def _TokenManager(todo="get", att=None, rtt=None, td=None):
    fileLocation = "tokens.txt"
    accessTokenTimeFormat = "Access token last updated: %Y-%m-%d %H:%M:%S\n"
    refreshTokenTimeFormat = "Refresh token last updated: %Y-%m-%d %H:%M:%S\n"

    def writeTokenVars(natt, nrtt, ntd):
        tokens.refreshToken = ntd.get("refresh_token")
        tokens.accessToken = ntd.get("access_token")
        tokens.accessTokenDateTime = natt
        tokens.refreshTokenDateTime = nrtt
        tokens.id_token = ntd.get("id_token")

    def writeTokenFile(natt, nrtt, ntd):
        with open(fileLocation, 'w') as file:
            file.write(natt.strftime(accessTokenTimeFormat))
            file.write(nrtt.strftime(refreshTokenTimeFormat))
            file.write(json.dumps(ntd))
            file.flush()

    def readTokenFile():
        with open(fileLocation, 'r') as file:
            fatt = datetime.strptime(file.readline(), accessTokenTimeFormat)
            frtt = datetime.strptime(file.readline(), refreshTokenTimeFormat)
            ftd = json.loads(file.readline())
            return fatt, frtt, ftd
    try:
        if todo == "getFile":
            return readTokenFile()
        elif todo == "set":
            if att is not None and rtt is not None and td is not None:
                writeTokenFile(att, rtt, td)
                writeTokenVars(att, rtt, td)
            else:
                universe.cTerm.error("Error in setting token file, null values given.")
        elif todo == "init":
            att, rtt, td = readTokenFile()
            writeTokenVars(att, rtt, td)
    except Exception as e:
        universe.cTerm.error("Error in reading/writing token file, creating new token file.")
        open(fileLocation, 'w').close()
        _RefreshTokenUpdate()


def _PostAccessTokenAutomated(grant_type, code):
    import base64
    headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{universe.credentials.appKey}:{universe.credentials.appSecret}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}
    if grant_type == 'authorization_code': data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': universe.credentials.callbackUrl} #gets access and refresh tokens using authorization code
    elif grant_type == 'refresh_token': data = {'grant_type': 'refresh_token', 'refresh_token': code} #refreshes the access token
    else:
        universe.cTerm.error("Invalid grant type")
        return None
    return requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data).json()


"""
Below here are all the api calls and functions that they use.
"""


def _ParamsParser(params):
    for key in list(params.keys()):
        if params[key] is None: del params[key]
    return params


def _TimeConvert(dt=None, form="8601"):
    if dt is None: return None
    elif dt is str: return dt
    elif form == "8601": return f'{dt.isoformat()[:-3]}Z'
    elif form == "epoch": return int(dt.timestamp()*1000)
    elif form == "YYYY-MM-DD": return dt.strftime("%Y-%M-%d")
    else: return dt


def formatList(l):  # could also encode symbols here
    if l is None: return None
    elif l is list == str: return l
    else: return ",".join(l)

"""
Accounts and Trading Production
"""
atp_url = "https://api.schwabapi.com/trader/v1"

class accounts:

    @staticmethod
    def accountNumbers():  # /accounts/accountNumbers
        return requests.get(f'{atp_url}/accounts/accountNumbers', headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod
    def getLinkedAccounts(fields=None):  # /accounts
        return requests.get(f'{atp_url}/accounts/', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'fields': fields}))

    @staticmethod  # /accounts/{accountHash}
    def getAccount(fields=None, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'fields': fields}))


class orders:
    @staticmethod  # /accounts/{accountHash}/orders
    def getOrders(maxResults, fromEnteredTime, toEnteredTime, status=None, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/orders', headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'maxResults': maxResults, 'fromEnteredTime': _TimeConvert(fromEnteredTime), 'toEnteredTime': _TimeConvert(toEnteredTime), 'status': status}))

    @staticmethod  # /accounts/{accountHash}/orders
    def placeOrder(order, accountHash=None):
        if accountHash is None: accountHash=universe.credentials.accountHash
        return requests.post(f'{atp_url}/accounts/{accountHash}/orders', headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}', "Content-Type": "application/json"}, json=order)

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def getOrder(orderId, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/orders/{orderId}', headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def cancelOrder(orderId, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.delete(f'{atp_url}/accounts/{accountHash}/orders/{orderId}', headers={'Authorization': f'Bearer {tokens.accessToken}'})

    @staticmethod  # /accounts/{accountHash}/orders/{orderId}
    def replaceOrder(orderId, order, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.put(f'{atp_url}/accounts/{accountHash}/orders/{orderId}', headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}', "Content-Type": "application/json"}, json=order)

    @staticmethod  # /orders
    def getAllOrders(maxResults, fromEnteredTime, toEnteredTime, status=None):
        return requests.get(f'{atp_url}/orders', headers={"Accept": "application/json", 'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'maxResults': maxResults, 'fromEnteredTime': _TimeConvert(fromEnteredTime), 'toEnteredTime': _TimeConvert(toEnteredTime), 'status': status}))

    @staticmethod  # /accounts/{accountHash}/previewOrder
    def previewOrder(orderObject, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.post(f'{atp_url}/accounts/{accountHash}/previewOrder', headers={'Authorization': f'Bearer {tokens.accessToken}', "Content-Type": "application.json"}, data=orderObject)


class transactions:
    @staticmethod  # /accounts/{accountHash}/transactions
    def transactions(startDate, endDate, types="TRADE", symbol=None, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/transactions', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'accountNumber': accountHash, 'startDate': _TimeConvert(startDate), 'endDate': _TimeConvert(endDate), 'symbol': symbol, 'types': types}))

    @staticmethod  # /accounts/{accountHash}/transactions/{transactionId}
    def details(transactionId, accountHash=None):
        if accountHash is None: accountHash = universe.credentials.accountHash
        return requests.get(f'{atp_url}/accounts/{accountHash}/transactions/{transactionId}',
                         headers={'Authorization': f'Bearer {tokens.accessToken}'}, params={'accountNumber': accountHash, 'transactionId': transactionId})


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
        return requests.get(f'{mkt_url}/quotes', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'symbols': formatList(symbols), 'fields': fields, 'indicative': indicative}))

    @staticmethod  # /{symbol_id}/quotes
    def getSingle(symbol_id, fields=None):
        return requests.get(f'{mkt_url}/{symbol_id}/quotes', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'fields': fields}))


class options:
    @staticmethod  # /chains
    def chains(symbol, contractType=None, strikeCount=None, includeUnderlyingQuotes=None, strategy=None, interval=None, strike=None, range=None, fromDate=None, toDate=None, volatility=None, underlyingPrice=None, interestRate=None, daysToExpiration=None, expMonth=None, optionType=None, entitlement=None):
        return requests.get(f'{mkt_url}/chains', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'symbol': symbol, 'contractType': contractType, 'strikeCount': strikeCount, 'includeUnderlyingQuotes': includeUnderlyingQuotes, 'strategy': strategy, 'interval': interval, 'strike': strike, 'range': range, 'fromDate': fromDate, 'toDate': toDate, 'volatility': volatility, 'underlyingPrice': underlyingPrice, 'interestRate': interestRate, 'daysToExpiration': daysToExpiration, 'expMonth': expMonth, 'optionType': optionType, 'entitlement': entitlement}))

    @staticmethod  # /expirationchain
    def expirationChain(symbol):
        return requests.get(f'{mkt_url}/expirationchain', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'symbol': symbol}))

class pricehistory:
    @staticmethod  # /pricehistory
    def getPriceHistory(symbol, periodType=None, period=None, frequencyType=None, frequency=None, startDate=None, endDate=None, needExtendedHoursData=None, needPreviousClose=None):
        return requests.get(f'{mkt_url}/pricehistory', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'symbol': symbol, 'periodType': periodType, 'period': period, 'frequencyType': frequencyType, 'frequency': frequency, 'startDate': _TimeConvert(startDate, 'epoch'), 'endDate': _TimeConvert(endDate, 'epoch'), 'needExtendedHoursData': needExtendedHoursData, 'needPreviousClose': needPreviousClose}))


class movers:
    @staticmethod  # /movers
    def getMovers(symbol, sort=None, frequency=None):
        return requests.get(f'{mkt_url}/movers', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'symbol': symbol, 'sort': sort, 'frequency': frequency}))


class marketHours:
    @staticmethod  # /markets
    def getHours(symbol, date=None):
        return requests.get(f'{mkt_url}/markets', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'markets': symbol, 'date': _TimeConvert(date, 'YYYY-MM-DD')}))

    @staticmethod  # /markets/{market_id}
    def byMarket(market_id, date=None):
        return requests.get(f'{mkt_url}/markets/{market_id}', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params=_ParamsParser({'date': _TimeConvert(date, 'YYYY-MM-DD')}))

class instruments:
    @staticmethod  # /instruments
    def get(symbol, projection):
        return requests.get(f'{mkt_url}/instruments', headers={'Authorization': f'Bearer {tokens.accessToken}'}, params={'symbol': symbol, 'projection': projection})

    @staticmethod  # /instruments/{cusip}
    def byCusip(cusip_id):
        return requests.get(f'{mkt_url}/instruments/{cusip_id}', headers={'Authorization': f'Bearer {tokens.accessToken}'})
