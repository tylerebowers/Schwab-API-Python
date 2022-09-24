"""
APIs for Quotes
https://developer.tdameritrade.com/quotes/apis
"""

import requests
from variables import credentials


def getQuotes(tickerList):  # pass in a list tickerList=["AMD","APPL"] and receive a real-time quote on the tickers in the list.
    return requests.get('https://api.tdameritrade.com/v1/marketdata/quotes',
                        params={'apikey': globals.consumerKey, 'symbol': tickerList},
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getQuote(ticker):  # pass in a single ticker="AMD" and receive a real-time quote.
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                        params={'apikey': globals.consumerKey},
                        headers={'Authorization': 'Bearer ' + globals.accessToken}).json()


def getDelayedQuote(ticker):  # pass in a single ticker="AMD" and receive a ~15min delayed quote.
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                        params={'apikey': globals.consumerKey}).json()


def examples():
    print('-----------------------------')
    print("Examples for: api-quotes")
    print('-----------------------------')
    print('getQuotes(tickerlist)')
    print('getQuotes(["AMD", "APPL"])')
    print(getQuotes(["AMD", "APPL"]))
    print('-----------------------------')
    print('getQuote(ticker)')
    print('getQuote("AMD")')
    print(getQuote("AMD"))
    print('-----------------------------')
    print('getDelayedQuote(ticker)')
    print('getDelayedQuote("AMD")')
    print(getDelayedQuote("AMD"))
    print('-----------------------------')
    return
