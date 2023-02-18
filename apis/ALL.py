import requests
from modules import universe
from apis import utilities


class _AccountsAndTrading:
    """
    Orders
    """

    def cancelOrder(self, orderId):
        return utilities.apiResponseHandler(
            requests.delete(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getOrder(self, orderId):
        return utilities.apiResponseHandler(
            requests.get(
                'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
                headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getOrdersByPath(self, **kwargs):  # times are entered as "yyyy-MM-dd"
        args = ["maxResults", "fromEnteredTime", "toEnteredTime", "status"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getOrdersByQuery(self, **kwargs):
        args = ["accountId", "maxResults", "fromEnteredTime", "toEnteredTime", "status"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/orders/',
                                                         params=params,
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def placeOrder(self, data):
        return utilities.apiResponseHandler(
            requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                          json=data,
                          headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def replaceOrder(self, orderId, data):
        return utilities.apiResponseHandler(requests.put(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders/' + orderId,
            json=data,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    Saved Orders THESE ARE GETTING REMOVED
    """

    def createSavedOrder(self, data):  # FIX
        return utilities.apiResponseHandler(
            requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders',
                          json=data,
                          headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def deleteSavedOrder(self, savedOrderId):
        return utilities.apiResponseHandler(requests.delete(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getSavedOrder(self, savedOrderId):
        return utilities.apiResponseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getSavedOrdersByPath(self):
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/',
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    # not tested
    def replaceSavedOrder(self, savedOrderId, data):  # FIX
        return utilities.apiResponseHandler(requests.put(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/savedorders/' + savedOrderId,
            params=data,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    Accounts
    """

    # not tested
    def getAccount(self, **kwargs):
        args = ["fields"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber,
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    # not tested
    def getAccounts(self, **kwargs):
        args = ["fields"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/',
                                                         params=params,
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def examples(self):
        print("------------------------------------")
        print("Examples for: api-accountsAndTrading")
        print("------------------------------------")
        print("Orders do not have examples yet")
        print("------------------------------------")
        print("Saved Orders have not been tested an do not have examples")
        print("------------------------------------")
        print("accountsAndTrading.getAccount()")
        print(self.getAccount())
        print("------------------------------------")
        print("accountsAndTrading.getAccounts()")
        print(self.getAccounts())
        print("------------------------------------")
        return


class _Authentication:
    def postAccessToken(self, data):
        return utilities.apiResponseHandler(requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                                                          headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                                          data=data))


class _Instruments:
    def searchInstruments(self, symbol, projection):
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/instruments',
                                                         params={'symbol': symbol, 'projection': projection},
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    Options for projection
    symbol-search: Retrieve instrument data of a specific symbol or cusip
    symbol-regex: Retrieve instrument data for all symbols matching regex. Example: symbol=XYZ.* will return all symbols beginning with XYZ
    desc-search: Retrieve instrument data for instruments whose description contains the word supplied. Example: symbol=FakeCompany will return all instruments with FakeCompany in the description.
    desc-regex: Search description with full regex support. Example: symbol=XYZ.[A-C] returns all instruments whose descriptions contain a word beginning with XYZ followed by a character A through C.
    fundamental: Returns fundamental data for a single instrument specified by exact symbol.'
    """

    def getInstrument(self, ticker):
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/instruments/' + ticker,
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class _MarketHours:
    def getHoursForMultipleMarkets(self, markets, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/hours',
                                                         params={'apikey': universe.credentials.consumerKey, 'markets': markets,
                                                                 'date': date},
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getHoursForASingleMarkets(self, market, date):  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + market + '/hours',
                         params={'apikey': universe.credentials.consumerKey, 'date': date},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class _Movers:
    def getMovers(self, index, **kwargs):  # Working
        args = ["direction", "change"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + index + '/movers',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    """
    direction options: # To return movers with the specified directions of up or down
    "up", "down" 
    change options: # To return movers with the specified change types of percent or value
    "value", "percent"
    """


class _OptionChains:
    def getOptionChain(self, **kwargs):
        args = ["symbol", "contractType", "strikeCount", "includeQuotes", "strategy", "interval", "strike", "range",
                "fromDate", "toDate", "volatility", "underlyingPrice", "interestRate", "daysToExpiration", "expMonth",
                "optionType"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/chains',
                                                         params=params,
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class _PriceHistory:
    def getPriceHistory(self, ticker, **kwargs):
        args = ["periodType", "period", "frequencyType", "frequency", "endDate", "startDate", "needExtendedHoursData"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + ticker + '/pricehistory',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class _Quotes:
    def getQuotes(self, tickerList):  # pass in a list tickerList=["AMD","APPL"] and receive a real-time quote on the tickers in the list.
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/marketdata/quotes',
                                                         params={'apikey': universe.credentials.consumerKey,
                                                                 'symbol': utilities.listToString(tickerList)},
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getQuote(self, ticker):  # pass in a single ticker="AMD" and receive a real-time quote.
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                         params={'apikey': universe.credentials.consumerKey},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getDelayedQuote(self, ticker):  # pass in a single ticker="AMD" and receive a ~15min delayed quote.
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/quotes',
                         params={'apikey': universe.credentials.consumerKey}))

    def examples(self):
        print('-----------------------------')
        print("Examples for: api-quotes")
        print('-----------------------------')
        print('getQuotes(tickerlist)')
        print('getQuotes(["AMD", "APPL"])')
        print(self.getQuotes(["AMD", "APPL"]))
        print('-----------------------------')
        print('getQuote(ticker)')
        print('getQuote("AMD")')
        print(self.getQuote("AMD"))
        print('-----------------------------')
        print('getDelayedQuote(ticker)')
        print('getDelayedQuote("AMD")')
        print(self.getDelayedQuote("AMD"))
        print('-----------------------------')
        return


class _TransactionHistory:
    def getTransaction(self, transactionId):
        return utilities.apiResponseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions/' + transactionId,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getTransactions(self, **kwargs):
        args = ["type", "symbol", "startDate", "endDate"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/transactions',
                         params=params,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


class _UserInfoAndPreferences:
    def getPreferences(self):
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/preferences',
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getStreamerSubscriptionKeys(self):
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/userprincipals/streamersubscriptionkeys',
                         params={'accountIds': universe.credentials.accountNumber},
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))
        # example of what is returned: {"keys": [{"key": "c7fb2_this_is_not_a_real_key_6c169b"}]}

    def getUserPrincipals(self, **kwargs):  # fields is a list of what to return; options are: streamerSubscriptionKeys, streamerConnectionInfo, preferences, surrogateIds
        args = ["fields"]
        params = utilities.kwargsHandler(args, kwargs)
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/userprincipals',
                                                         params=params,
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def updatePreferences(self, data):  # I could only get this to work through the dev website for some reason
        return utilities.apiResponseHandler(
            requests.put('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/preferences',
                         json=data,
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken,
                                  'Content-Type': 'application/json'}))

    """  # these are what could be put for "updatePreferences" in the dictionary
    {
        "expressTrading": false,
        "directOptionsRouting": false,
        "directEquityRouting": false,
        "defaultEquityOrderLegInstruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'NONE'",
        "defaultEquityOrderType": "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'NONE'",
        "defaultEquityOrderPriceLinkType": "'VALUE' or 'PERCENT' or 'NONE'",
        "defaultEquityOrderDuration": "'DAY' or 'GOOD_TILL_CANCEL' or 'NONE'",
        "defaultEquityOrderMarketSession": "'AM' or 'PM' or 'NORMAL' or 'SEAMLESS' or 'NONE'",
        "defaultEquityQuantity": 0,
        "mutualFundTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
        "optionTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
        "equityTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
        "defaultAdvancedToolLaunch": "'TA' or 'N' or 'Y' or 'TOS' or 'NONE' or 'CC2'",
        "authTokenTimeout": "'FIFTY_FIVE_MINUTES' or 'TWO_HOURS' or 'FOUR_HOURS' or 'EIGHT_HOURS'"
    }
                # these are what you will probably have as your values (authTokenTimeout has been changed from 55m to 8h)
                # as arguments: ("false","false","false","NONE","LIMIT","NONE","DAY","NORMAL",0,"FIFO","FIFO","FIFO","NONE","EIGHT_HOURS")
    {
        "expressTrading": false,
        "directOptionsRouting": false,
        "directEquityRouting": false,
        "defaultEquityOrderLegInstruction": "NONE",
        "defaultEquityOrderType": "LIMIT",
        "defaultEquityOrderPriceLinkType": "NONE",
        "defaultEquityOrderDuration": "DAY",
        "defaultEquityOrderMarketSession": "NORMAL",
        "defaultEquityQuantity": 0,
        "mutualFundTaxLotMethod": "FIFO",
        "optionTaxLotMethod": "FIFO",
        "equityTaxLotMethod": "FIFO",
        "defaultAdvancedToolLaunch": "NONE",
        "authTokenTimeout": "EIGHT_HOURS"
    }
    """


#class _utilities:

class _Watchlist:
    def createWatchlist(self, data):  # FIX
        return utilities.apiResponseHandler(
            requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists',
                          json=data,
                          headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def deleteWatchlist(self, watchListId):  # FIX
        return utilities.apiResponseHandler(requests.delete(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/' + watchListId,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getWatchlist(self, watchListId):  # FIX
        return utilities.apiResponseHandler(requests.get(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/' + watchListId,
            headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getWatchlistsForMultipleAccounts(self):  # FIX
        return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/watchlists',
                                                         headers={
                                                             'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def getWatchlistsForSingleAccount(self):  # FIX
        return utilities.apiResponseHandler(
            requests.get('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists',
                         headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def replaceWatchlist(self, watchListId, data):  # FIX
        return utilities.apiResponseHandler(requests.post(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/' + watchListId,
            json=data, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    def updateWatchlist(self, watchListId, data):  # FIX
        return utilities.apiResponseHandler(requests.patch(
            'https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/watchlists/' + watchListId,
            json=data, headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))

    '''
    # data for watchlists
    {
        "name": "string",
        "watchlistItems": [
            {
                "quantity": 0,
                "averagePrice": 0,
                "commission": 0,
                "purchasedDate": "DateParam\"",
                "instrument": {
                    "symbol": "string",
                    "assetType": "'EQUITY' or 'OPTION' or 'MUTUAL_FUND' or 'FIXED_INCOME' or 'INDEX'"
                }
            }
        ]
    }
    '''

accountsAndTrading = _AccountsAndTrading()
authentication = _Authentication()
instruments = _Instruments()
marketHours = _MarketHours()
movers = _Movers()
optionChains = _OptionChains()
priceHistory = _PriceHistory()
quotes = _Quotes()
transactionHistory = _TransactionHistory()
userInfoAndPreferences = _UserInfoAndPreferences()
watchlist = _Watchlist()