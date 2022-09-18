"""
Coded by Tyler Bowers
Find my contact info and other projects at tylerebowers.com
"""
import urllib
from variables import globals
import json
from apis import authentication
from datetime import datetime


def login():
    with open('variables/tokens.txt', 'r') as file:
        accessTokenTime = file.readline().strip('\n')
        if len(accessTokenTime) > 10:
            refreshTokenTime = file.readline().strip('\n')
            if len(refreshTokenTime) > 10:
                tempLine = file.readline()
                if len(tempLine) > 100:
                    tokenDictionary = json.loads(tempLine)
                    print("Last updated: Access Token: " + accessTokenTime + ", Refresh Token: " + refreshTokenTime)
                    accessTokenTime = datetime.strptime(accessTokenTime, "%d/%m/%y %H:%M:%S")
                    refreshTokenTime = datetime.strptime(refreshTokenTime, "%d/%m/%y %H:%M:%S")
                    if (datetime.now() - refreshTokenTime).days > 90:
                        print("The refresh token has expired, please update.")
                        refreshTokenUpdate()
                    elif (datetime.now() - accessTokenTime).days >= 1 or (
                            (datetime.now() - accessTokenTime).seconds > ((globals.authTokenTimeout * 60) - 60)):
                        print("The access token has expired, updating automatically.")
                        accessTokenUpdate()
                    else:
                        globals.accessToken = tokenDictionary.get("access_token")
                        globals.refreshToken = tokenDictionary.get("refresh_token")
        else:
            print("There was an error in the file, rebuild it.")
            refreshTokenUpdate()
    print("Initialization Complete")


def refreshTokenUpdate():
    print("Click to authenticate: " + "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=" +
          urllib.parse.quote(globals.callbackUrl,
                             safe='') + "&client_id=" + globals.consumerKey + "%40AMER.OAUTHAP")
    responseURL = input("Paste the response url here: ")
    try:
        authCode = urllib.parse.unquote(responseURL.split("code=")[1])
    except:
        print('Please copy and past the WHOLE url!')
        quit()
    newTokens = authentication.postAccessToken('authorization_code', authCode)
    with open('variables/tokens.txt', 'w') as file:
        file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S") + "\n")
        file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S"))
        file.write("\n" + json.dumps(newTokens))
    globals.accessToken = newTokens.get("access_token")
    globals.refreshToken = newTokens.get("refresh_token")
    print("Refresh and Access tokens updated")


def accessTokenUpdate():
    with open('variables/tokens.txt', 'r') as file:
        file.readline()
        refreshTokenTime = file.readline()
        dictionary = json.loads(file.readline())
    newAccessToken = authentication.postAccessToken('refresh_token', dictionary.get("refresh_token"))
    dictionary['access_token'] = newAccessToken.get('access_token')
    with open('variables/tokens.txt', 'w') as file:
        file.write(datetime.now().strftime("%d/%m/%y %H:%M:%S"))
        file.write("\n" + refreshTokenTime)
        file.write(json.dumps(dictionary))
    globals.accessToken = dictionary.get("access_token")
    globals.refreshToken = dictionary.get("refresh_token")
    print("Access token updated")


def getToken(requestType):  # access_token, refresh_token, scope, expires_in, refresh_token_expires_in, token_type
    with open('variables/tokens.txt', 'r') as file:
        file.readline()
        file.readline()
        tokenDictonary = json.loads(file.readline())
    if requestType == "raw" or requestType == "all" or requestType == "dictionary":
        return (tokenDictonary)
    else:
        return (tokenDictonary.get(requestType))

