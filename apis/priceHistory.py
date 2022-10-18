"""
APIs for Price History
https://developer.tdameritrade.com/price-history/apis
"""
import requests
from modules import globals, utilities, user


def getPriceHistory(ticker, **kwargs):
    user.checkTokens()
    args = ["periodType", "period", "frequencyType", "frequency", "endDate", "startDate", "needExtendedHoursData"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.responseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/' + ticker + '/pricehistory',
                        params=params,
                        headers={'Authorization': 'Bearer ' + globals.accessToken}))




