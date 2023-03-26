"""
APIs for Price History
https://developer.tdameritrade.com/price-history/apis
"""
import requests
from modules import universe, api
from apis import utilities


def getPriceHistory(ticker, **kwargs):
    args = ("periodType", "period", "frequencyType", "frequency", "endDate", "startDate", "needExtendedHoursData")
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/' + ticker + '/pricehistory',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))




