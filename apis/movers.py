# https://developer.tdameritrade.com/movers/apis
import requests
from variables import credentials


def getMovers(index, direction, change):  # Working
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + index + '/movers',
                        params={'direction': direction, 'change': change},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()

"""
direction options: # To return movers with the specified directions of up or down
"up", "down" 
change options: # To return movers with the specified change types of percent or value
"value", "percent"
"""