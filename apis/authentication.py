from variables import credentials
import requests

debug = False


def postAccessToken(grant_type, data):
    if grant_type == 'authorization_code':
        authCode = data
        response = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data={'grant_type': 'authorization_code', 'access_type': 'offline', 'code': authCode,
                                   'client_id': credentials.consumerKey, 'redirect_uri': credentials.callbackUrl})
        if str(response) != "<Response [200]>":
            print("Error with url, re-authenticate!")
            quit()
        return response.json()
    if grant_type == 'refresh_token':
        refreshToken = data
        response = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data={'grant_type': 'refresh_token', 'refresh_token': refreshToken,
                                   'client_id': credentials.consumerKey})
        if str(response) != "<Response [200]>":
            print("Error with url, re-authenticate!")
            quit()
        return response.json()







