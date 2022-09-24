"""
APIs for authentication
https://developer.tdameritrade.com/authentication/apis
"""

from variables import globals
import requests


def postAccessToken(grant_type, code):
    if grant_type == 'authorization_code':
        authCode = code
        data = {'grant_type': 'authorization_code', 'access_type': 'offline', 'code': authCode,
                'client_id': globals.consumerKey, 'redirect_uri': globals.callbackUrl}
    elif grant_type == 'refresh_token':
        refreshToken = code
        data = {'grant_type': 'refresh_token', 'refresh_token': refreshToken,
                'client_id': globals.consumerKey}
    else:
        return "error"
    response = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data=data)
    if str(response) != "<Response [200]>":
        print("Error with url, re-authenticate!")
        quit()
    return response.json()
