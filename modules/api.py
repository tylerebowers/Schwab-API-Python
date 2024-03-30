"""
This file contains all api requests and functions to initialize the program
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import time
import requests
from modules import universe
from datetime import datetime


def initialize():

    if len(universe.credentials.appKey) != 32 or len(universe.credentials.appSecret) != 16:
        universe.terminal.error("No app key or app secret found, please add your app key in modules/universe.credentials.appKey)")
        quit()

    # show user when tokens were last updated
    _TokenManager("init")  # this also sets universe variables for tokens and token timeouts
    universe.terminal.info(universe.tokens.accessTokenDateTime.strftime("Access token last updated: %d/%m/%y %H:%M:%S"))
    universe.terminal.info(universe.tokens.refreshTokenDateTime.strftime("Refresh token last updated: %d/%m/%y %H:%M:%S"))

    # check if tokens need to be updated and update if needed
    _UpdateTokens()

    # show user when tokens will expire & complete initialization
    universe.terminal.warning(f"Access token expires in {universe.tokens.accessTokenTimeout - (datetime.now() - universe.tokens.accessTokenDateTime).seconds} seconds!")
    universe.terminal.warning(f"Refresh token expires in {universe.tokens.refreshTokenTimeout - (datetime.now() - universe.tokens.refreshTokenDateTime).days} days!")
    universe.terminal.info("Initialization Complete")


def _UpdateTokens():
    if (datetime.now() - universe.tokens.refreshTokenDateTime).days >= (universe.tokens.refreshTokenTimeout-1): #check if we need to update refresh (and access) token
        universe.terminal.user("The refresh token has expired, please update!") # print multiple times?
        _RefreshTokenUpdate()
    elif ((datetime.now() - universe.tokens.accessTokenDateTime).days >= 1) or ((datetime.now() - universe.tokens.accessTokenDateTime).seconds > (universe.tokens.accessTokenTimeout - 60)): #check if we need to update access token
        universe.terminal.info("The access token has expired, updating automatically.")
        _AccessTokenUpdate()
    #else: universe.terminal.info("Token check passed")


def _AccessTokenUpdate():
    # get the token dictionary (we will need to rewrite the wile)
    accessTokenFileTime, refreshTokenFileTime, tokenDictionary = _TokenManager("getFile")
    # get and update to the new access token
    _TokenManager("set", datetime.now(), refreshTokenFileTime, _PostAccessTokenAutomated('refresh_token', tokenDictionary.get("refresh_token")))
    # show user that we have updated the access token
    universe.terminal.info(f"Access token updated: {universe.tokens.accessTokenDateTime}")


def _RefreshTokenUpdate():
    import webbrowser
    # get authorization code (requires user to authorize)
    universe.terminal.user("Please authorize this program to access your schwab account.")
    authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={universe.credentials.appKey}&redirect_uri={universe.credentials.callbackUrl}'
    universe.terminal.user(f"Click to authenticate: {authUrl}")
    universe.terminal.info("Opening browser...")
    webbrowser.open(authUrl)
    responseURL = universe.terminal.input("After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    code = f"{responseURL[responseURL.index('code=')+5:responseURL.index('%40')]}@"  #session = responseURL[responseURL.index("session=")+8:]
    # get new access and refresh tokens
    tokenDictionary = _PostAccessTokenAutomated('authorization_code', code)
    # update token file and variables
    _TokenManager("set", datetime.now(), datetime.now(), tokenDictionary)
    universe.terminal.info("Refresh and Access tokens updated")


def _TokenManager(todo="get", att=None, rtt=None, td=None):
    fileLocation = "modules/tokens.txt"
    accessTokenTimeFormat = "Access token last updated: %d/%m/%y %H:%M:%S\n"
    refreshTokenTimeFormat = "Refresh token last updated: %d/%m/%y %H:%M:%S\n"

    def writeTokenVars(natt, nrtt, ntd):
        universe.tokens.refreshToken = ntd.get("refresh_token")
        universe.tokens.access_token = ntd.get("access_token")
        universe.tokens.accessTokenDateTime = natt
        universe.tokens.refreshTokenDateTime = nrtt
        universe.tokens.id_token = ntd.get("id_token")

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
        elif todo == "set" and att is not None and rtt is not None and td is not None:
            writeTokenFile(att, rtt, td)
            writeTokenVars(att, rtt, td)
        elif todo == "init":
            att, rtt, td = readTokenFile()
            writeTokenVars(att, rtt, td)
    except:
        universe.terminal.error("Error in reading/writing token file, creating new token file.")
        open(fileLocation, 'w').close()
        _RefreshTokenUpdate()


def _ResponseHandler(response):
    try:
        if response.ok:
            return response.json()
    except json.decoder.JSONDecodeError:
        universe.terminal.warning(f"Nothing Returned (Code: {response.status_code})")
        return None
    except AttributeError:
        universe.terminal.error(f"Something else has been returned (Code: {response.status_code})")
        return None


def _PostAccessTokenAutomated(grant_type, code):
    import base64
    headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{universe.credentials.appKey}:{universe.credentials.appSecret}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}
    if grant_type == 'authorization_code': data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': universe.credentials.callbackUrl} #gets access and refresh tokens using authorization code
    elif grant_type == 'refresh_token': data = {'grant_type': 'refresh_token', 'refresh_token': code} #refreshes the access token
    else:
        universe.terminal.error("Invalid grant type")
        return None
    return _ResponseHandler(requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data))


"""

def _checkTokensDaemon():
    while True:
        checkTokensManual()
        time.sleep(60)



def _kwargsHandler(args, kwargs):
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return params


base_url = "https://api.schwabapi.com/trader/v1/"

class accounts:

    @staticmethod
    def accountNumbers():
        return _responseHandler(requests.get(f'{base_url}/accounts/accountNumbers', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def accounts():
        return _responseHandler(
            requests.get(f'{base_url}/accounts/', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def accountNumber():
        return _responseHandler(requests.get(f'{base_url}/accounts/{universe.credentials.accountNumber}', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

'''
class orders:
    @staticmethod
    def accountOrders(accountNumber, maxResults, fromEnteredTime, toEnteredTime, status):
        return _responseHandler(
            requests.get(f'{base_url}/accounts/{universe.credentials.accountNumber}/orders/', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def placeOrder():
        return _responseHandler(
            requests.post(f'{base_url}/accounts/{universe.credentials.accountNumber}/positions/', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def getOrder():
        return _responseHandler(
            requests.get(f'{base_url}/accounts/{universe.credentials.accountNumber}/orders/{orderId}', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def cancelOrder():
        return _responseHandler(
            requests.delete(f'{base_url}/accounts/{universe.credentials.accountNumber}/orders/{orderId}', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def replaceOrder():
        return _responseHandler(
            requests.put(f'{base_url}/accounts/{universe.credentials.accountNumber}/orders/{orderId}', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def orders():
        return _responseHandler(
            requests.get(f'{base_url}/orders', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def previewOrder():
        return _responseHandler(
            requests.post(f'{base_url}/accounts/{universe.credentials.accountNumber}/orders', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

class Transactions:
    @staticmethod
    def transactions():
        return _responseHandler(
            requests.get(f'{base_url}/accounts/{universe.credentials.accountNumber}/transactions', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    @staticmethod
    def accountTransaction():
        return _responseHandler(
            requests.get(f'{base_url}/accounts/{universe.credentials.accountNumber}/transactions/{transactionId}',
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

class UserPreference:
    @staticmethod
    def transactions():
        return _responseHandler(
            requests.get(f'{base_url}/userPreference', headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
'''
"""