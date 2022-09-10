"""
APIs for Price History
https://developer.tdameritrade.com/price-history/apis
"""
import requests
from datetime import datetime
from variables import credentials


def getPriceHistory(ticker, **kwargs):
    args = ["periodType", "period", "frequencyType", "frequency", "endDate", "startDate", "needExtendedHoursData"]
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + ticker + '/pricehistory',
                        params=params,
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()
