"""
APIs for authentication
https://developer.tdameritrade.com/authentication/apis
"""

from apis import utilities
from modules import api
import requests


def postAccessToken(data):
    return utilities.apiResponseHandler(requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                                                      headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                      data=data))
