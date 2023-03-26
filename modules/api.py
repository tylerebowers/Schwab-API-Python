"""
This file makes sure that the refresh and access tokens are up-to-date.
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Wrapper
"""
import json
import time
import urllib
import threading
from modules import universe
from datetime import datetime
from apis import authentication


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
        universe.terminal.info("Please make sure that modules/tokens.txt exists and that your environment is setup correctly (ie running program from main.py).")
        quit()
    universe.terminal.info("" + accessTokenFileTime)
    universe.terminal.info("" + refreshTokenFileTime)
    universe.tokens.accessTokenDateTime = datetime.strptime(accessTokenFileTime, "Access token last updated: %d/%m/%y %H:%M:%S")
    universe.tokens.refreshTokenDateTime = datetime.strptime(refreshTokenFileTime,
                                                     "Refresh token last updated: %d/%m/%y %H:%M:%S")
    if (datetime.now() - universe.tokens.refreshTokenDateTime).days >= 89:
        universe.terminal.error("The refresh token has expired, please update.")
        _refreshTokenUpdate()
    elif (datetime.now() - universe.tokens.accessTokenDateTime).days >= 1 or (
            (datetime.now() - universe.tokens.accessTokenDateTime).seconds > ((universe.tokens.authTokenTimeout * 60) - 60)):
        universe.terminal.info("The access token has expired, updating automatically.")
        _accessTokenUpdate()
    else:
        universe.tokens.accessToken = tokenDictionary.get("access_token")
        universe.tokens.refreshToken = tokenDictionary.get("refresh_token")
    universe.terminal.info(f"Refresh token expires in {90-(datetime.now() - universe.tokens.refreshTokenDateTime).days} days!")
    universe.terminal.info("Initialization Complete")


def _refreshTokenUpdate():
    print("[INPUT]: Click to authenticate: " + "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=" +
          urllib.parse.quote(universe.credentials.callbackUrl,
                             safe='') + "&client_id=" + universe.credentials.consumerKey + "%40AMER.OAUTHAP")
    responseURL = input("[INPUT]: After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    authCode = urllib.parse.unquote(responseURL.split("code=")[1])
    newTokens = _postAccessTokenAutomated('authorization_code', authCode)
    universe.tokens.accessTokenDateTime = datetime.now()
    universe.tokens.refreshTokenDateTime = datetime.now()
    with open('modules/tokens.txt', 'w') as file:
        file.write(universe.tokens.accessTokenDateTime.strftime("Access token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(universe.tokens.refreshTokenDateTime.strftime("Refresh token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(json.dumps(newTokens))
        file.flush()
        file.close()
    universe.tokens.accessToken = newTokens.get("access_token")
    universe.tokens.refreshToken = newTokens.get("refresh_token")
    universe.terminal.info("Refresh and Access tokens updated")


def _accessTokenUpdate():
    with open('modules/tokens.txt', 'r') as file:
        file.readline()
        refreshTokenFileTime = file.readline()
        dictionary = json.loads(file.readline())
        file.close()
    try:
        newAccessToken = _postAccessTokenAutomated('refresh_token', dictionary.get("refresh_token"))
    except Exception as e:
        newAccessToken = dictionary
        print(e)
        for i in range(3): universe.terminal.warning("Problem with access token request, check your internet connection!")
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


def getTokensFromFile(requestType):
    # requestType = access_token, refresh_token, scope, expires_in, refresh_token_expires_in, token_type
    with open('modules/tokens.txt', 'r') as file:
        file.readline()
        file.readline()
        tokenDictionary = json.loads(file.readline())
        file.close()
    if requestType == "raw" or requestType == "all" or requestType == "dictionary":
        return tokenDictionary
    else:
        match requestType:
            case "access_token":
                return tokenDictionary.get("access_token")
            case "refresh_token":
                return tokenDictionary.get("refresh_token")
            case "scope":
                return tokenDictionary.get("scope")
            case "expires_in":
                return tokenDictionary.get("expires_in")
            case "refresh_token_expires_in":
                return tokenDictionary.get("refresh_token_expires_in")
            case "token_type":
                return tokenDictionary.get("token_type")
            case _:
                universe.terminal.warning("Invalid requestType ")


def _postAccessTokenAutomated(grant_type, code):
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
        _refreshTokenUpdate()
    elif (datetime.now() - universe.tokens.accessTokenDateTime).days >= 1 or (
            (datetime.now() - universe.tokens.accessTokenDateTime).seconds > ((universe.tokens.authTokenTimeout * 60) - 120)):
        universe.terminal.info("The access token has expired, updating automatically.")
        _accessTokenUpdate()


def _checkTokensDaemon():
    def _checkTokens():
        while True:
            checkTokensManual()
            time.sleep(60)

    universe.threads.append(threading.Thread(target=_checkTokens, daemon=True))