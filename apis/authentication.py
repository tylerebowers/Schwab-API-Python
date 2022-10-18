"""
APIs for authentication
https://developer.tdameritrade.com/authentication/apis
"""

from modules import utilities
import requests


def postAccessToken(data):
    return utilities.responseHandler(requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data=data))
