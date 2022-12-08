"""
This file makes sure that the refresh and access tokens are up-to-date.
import modules/user and use api.initialize() runs the checks
Coded by Tyler Bowers on 6D/8M/2022Y
Find my contact info and other projects at tylerebowers.com
"""
import json
import time
import urllib
import threading
from modules import globals
from datetime import datetime
from apis import authentication


def initialize():
    if len(globals.consumerKey) != 32:
        print("ERROR: Please check to make sure that you have your consumer key in modules/globals.py")
        print("INFO: If you do have the key and this check is failing you can remove it in modules/api.py")
        quit()
    try:
        with open('modules/tokens.txt', 'r') as file:
            accessTokenFileTime = file.readline().strip('\n')
            refreshTokenFileTime = file.readline().strip('\n')
            tokenDictionary = json.loads(file.readline())
            file.flush()
            file.close()
    except:
        print("ERROR: Error in reading from file.")
        print(
            "INFO: Please make sure that modules/tokens.txt exists and that your environment is setup correctly (ie running program from main.py).")
        quit()
    print("INFO: " + accessTokenFileTime)
    print("INFO: " + refreshTokenFileTime)
    globals.accessTokenDateTime = datetime.strptime(accessTokenFileTime, "Access token last updated: %d/%m/%y %H:%M:%S")
    globals.refreshTokenDateTime = datetime.strptime(refreshTokenFileTime,
                                                     "Refresh token last updated: %d/%m/%y %H:%M:%S")
    if (datetime.now() - globals.refreshTokenDateTime).days >= 89:
        print("ERROR: The refresh token has expired, please update.")
        refreshTokenUpdate()
    elif (datetime.now() - globals.accessTokenDateTime).days >= 1 or (
            (datetime.now() - globals.accessTokenDateTime).seconds > ((globals.authTokenTimeout * 60) - 60)):
        print("INFO: The access token has expired, updating automatically.")
        accessTokenUpdate()
    else:
        globals.accessToken = tokenDictionary.get("access_token")
        globals.refreshToken = tokenDictionary.get("refresh_token")
    print("INFO: Initialization Complete")


def refreshTokenUpdate():
    print("INPUT: Click to authenticate: " + "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=" +
          urllib.parse.quote(globals.callbackUrl,
                             safe='') + "&client_id=" + globals.consumerKey + "%40AMER.OAUTHAP")
    responseURL = input("INPUT: After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
    authCode = urllib.parse.unquote(responseURL.split("code=")[1])
    newTokens = postAccessTokenAutomated('authorization_code', authCode)
    globals.accessTokenDateTime = datetime.now()
    globals.refreshTokenDateTime = datetime.now()
    with open('modules/tokens.txt', 'w') as file:
        file.write(globals.accessTokenDateTime.strftime("Access token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(globals.refreshTokenDateTime.strftime("Refresh token last updated: %d/%m/%y %H:%M:%S") + "\n")
        file.write(json.dumps(newTokens))
        file.flush()
        file.close()
    globals.accessToken = newTokens.get("access_token")
    globals.refreshToken = newTokens.get("refresh_token")
    print("INFO: Refresh and Access tokens updated")


def accessTokenUpdate():
    with open('modules/tokens.txt', 'r') as file:
        file.readline()
        refreshTokenFileTime = file.readline()
        dictionary = json.loads(file.readline())
        file.close()
    newAccessToken = postAccessTokenAutomated('refresh_token', dictionary.get("refresh_token"))
    dictionary['access_token'] = newAccessToken.get('access_token')
    with open('modules/tokens.txt', 'w') as file:
        file.write(datetime.now().strftime("Access token last updated: %d/%m/%y %H:%M:%S"))
        file.write("\n" + refreshTokenFileTime)
        file.write(json.dumps(dictionary))
        file.flush()
        file.close()
    globals.accessToken = dictionary.get("access_token")
    globals.refreshToken = dictionary.get("refresh_token")
    globals.accessTokenDateTime = datetime.now()
    print("INFO: Access token updated")


def getTokensFromFile(
        requestType):  # access_token, refresh_token, scope, expires_in, refresh_token_expires_in, token_type
    with open('modules/tokens.txt', 'r') as file:
        file.readline()
        file.readline()
        tokenDictionary = json.loads(file.readline())
        file.flush()
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
                print("WARNING: Invalid requestType ")


def postAccessTokenAutomated(grant_type, code):
    if grant_type == 'authorization_code':
        data = {'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code,
                'client_id': globals.consumerKey, 'redirect_uri': globals.callbackUrl}
        return authentication.postAccessToken(data)
    elif grant_type == 'refresh_token':
        data = {'grant_type': 'refresh_token', 'refresh_token': code,
                'client_id': globals.consumerKey}
        return authentication.postAccessToken(data)


def checkTokensManual():
    if (datetime.now() - globals.refreshTokenDateTime).days > 89:
        print("WARNING: The refresh token has expired, please update.")
        refreshTokenUpdate()
    elif (datetime.now() - globals.accessTokenDateTime).days >= 1 or (
            (datetime.now() - globals.accessTokenDateTime).seconds > ((globals.authTokenTimeout * 60) - 120)):
        print("INFO: The access token has expired, updating automatically.")
        accessTokenUpdate()


def checkTokensDaemon():
    def _checkTokens():
        while True:
            checkTokensManual()
            time.sleep(60)

    globals.threads.append(threading.Thread(target=_checkTokens, daemon=True))
