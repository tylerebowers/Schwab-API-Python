"""
APIs for Movers
https://developer.tdameritrade.com/movers/apis
"""
import requests
from modules import universe
from apis import utilities


def getMovers(index, **kwargs):  # Working
    args = ("direction", "change")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/' + index + '/movers',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


"""
direction options: # To return movers with the specified directions of up or down
"up", "down" 
change options: # To return movers with the specified change types of percent or value
"value", "percent"
"""