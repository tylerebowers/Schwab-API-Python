# https://developer.tdameritrade.com/option-chains/apis
import requests
from variables import credentials


def getStreamerSubscriptionKeys():  # NOT ADDED YET
    return requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                        params={},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()
