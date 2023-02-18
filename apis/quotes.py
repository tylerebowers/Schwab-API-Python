"""
APIs for Quotes
https://developer.tdameritrade.com/quotes/apis
"""

import requests
from modules import universe, api
from apis import utilities


def getQuotes(tickerList):  # pass in a list tickerList=["AMD","APPL"] and receive a real-time quote on the tickers in the list.
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/quotes',
                                                     params={'apikey': universe.credentials.consumerKey, 'symbol': utilities.listToString(tickerList)},
                                                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getQuote(ticker):  # pass in a single ticker="AMD" and receive a real-time quote.
    return utilities.apiResponseHandler(
        requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                     params={'apikey': universe.credentials.consumerKey},
                     headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def getDelayedQuote(ticker):  # pass in a single ticker="AMD" and receive a ~15min delayed quote.
    return utilities.apiResponseHandler(
        requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                     params={'apikey': universe.credentials.consumerKey}))


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
