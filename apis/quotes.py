import requests
from variables import credentials


def getQuotes(tickerList):  # Pass in a list
    return requests.get('https://api.tdameritrade.com/v1/marketdata/quotes',
                        params={'apikey': credentials.consumerKey, 'symbol': tickerList},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()


def getQuote(ticker):  # Pass in a single ticker
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                        params={'apikey': credentials.consumerKey},
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()


def delayedQuote(ticker):  # Pass in a single ticker, this one is unauthenticated and is delayed ~15min
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                        params={'apikey': credentials.consumerKey}).json()
