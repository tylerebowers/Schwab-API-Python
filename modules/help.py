import time
from modules import api, stream

"""
def run():
    print("Welcome to the demo of this interface!")
    time.sleep(1)
"""


class apiHelp:
    class accountsAndTrading:
        """
        Orders
        """

        @staticmethod
        def cancelOrder():
            print('This function is used to cancel an order with the order number.')
            print("\torderId: type=int, required")
            print('accountsAndTrading.cancelOrder(orderId)')
            print('This function does not have a demo. (yet...)')

        @staticmethod
        def getOrder():
            print('This function is used to get order details with the order number.')
            print("\torderId: type=int, required")
            print('api.accountsAndTrading.getOrder(orderId)')
            print('This function does not have a demo. (yet...)')

        @staticmethod
        def getOrdersByPath():
            print('This function is used to get a list of orders for your account.')
            print("\tmaxResults: type=int, optional")
            print('\tfromEnteredTime: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('\ttoEnteredTime: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('\tstatus: type=string, optional, format="(no value)", "AWAITING_PARENT_ORDER", "AWAITING_CONDITION", "AWAITING_MANUAL_REVIEW", "ACCEPTED", "AWAITING_UR_OUT", "PENDING_ACTIVATION", "QUEUED", "WORKING", "REJECTED", "PENDING_CANCEL", "CANCELED", "PENDING_REPLACE", "REPLACED", "FILLED", "EXPIRED"')
            print('api.accountsAndTrading.getOrdersByPath()')
            print('This function does not have a demo. (yet...)')

        @staticmethod
        def getOrdersByQuery():
            print('This function is used to get a list of orders for the specified account id.')
            print("\taccountId: type=int, optional")
            print("\tmaxResults: type=int, optional")
            print('\tfromEnteredTime: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('\ttoEnteredTime: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('\tstatus: type=string, optional, format="(no value)", "AWAITING_PARENT_ORDER", "AWAITING_CONDITION", "AWAITING_MANUAL_REVIEW", "ACCEPTED", "AWAITING_UR_OUT", "PENDING_ACTIVATION", "QUEUED", "WORKING", "REJECTED", "PENDING_CANCEL", "CANCELED", "PENDING_REPLACE", "REPLACED", "FILLED", "EXPIRED"')
            print('api.accountsAndTrading.getOrdersByQuery(orderId)')
            print('This function does not have a demo. (yet...)')
        @staticmethod
        def placeOrder():
            print('This function is used to place orders. Please look at specific help for orders on using this function.')
            print("\tjson: type=json, required")
            print('api.accountsAndTrading.placeOrder(json)')
            print('This function does not have a demo.')
        @staticmethod
        def replaceOrder():
            print('This function is used to replace orders. Please look at specific help for orders on using this function.')
            print("\tjson: type=json, required")
            print('api.accountsAndTrading.replaceOrder(orderId)')
            print('This function does not have a demo.')

        """
        Saved Orders THESE ARE GETTING REMOVED
        """

        @staticmethod
        def createSavedOrder():
            print("This function is getting removed.")
        @staticmethod
        def deleteSavedOrder():
            print("This function is getting removed.")
        @staticmethod
        def getSavedOrder():
            print("This function is getting removed.")
        @staticmethod
        def getSavedOrdersByPath():
            print("This function is getting removed.")
        @staticmethod
        def replaceSavedOrder():
            print("This function is getting removed.")

        """
        Accounts
        """

        @staticmethod
        def getAccount():
            print('This function is used to get account data such as balances, positions, or orders.')
            print('\tfields: type=string, optional, format="positions", "orders"')
            print('api.accountsAndTrading.getAccount()')
            print(api.accountsAndTrading.getAccount())
        @staticmethod
        def getAccounts():
            print('This function is used to get data from all linked accounts such as balances, positions, or orders.')
            print('\tfields: type=string, optional, format="positions", "orders"')
            print('api.accountsAndTrading.getAccounts()')
            print(api.accountsAndTrading.getAccounts())


    class authentication:
        @staticmethod
        def postAccessToken():
            print('This function is used to update/get new access tokens and an optional refresh token.')
            print('It is NOT recommended to use this function since it is used for core functionality of this program.')
            print('\tgrant_type: type=string, required, format="authorization_code", "refresh_token"')
            print('\trefresh_token: type=string, optional(sometimes required)')
            print('\taccess_type: type=string, optional')
            print('\tcode: type=int, optional')
            print('\tclient_id: type=int, required')
            print('\tredirect_uri: type=string, optional')
            print('api.authentication.postAccessToken()')
            print('This function does not have a demo.')

    class instruments:
        @staticmethod
        def searchInstruments():
            print('This function is used to search through instruments.')
            print("\tsymbol: type=string, required")
            print('\tprojection: type=string, required, format="symbol-search", "symbol-regex"(symbol=XYZ.*), "desc-search", "desc-regex"(symbol=XYZ.[A-C]), "fundamental"')
            print('api.instruments.searchInstruments(symbol, projection)')
            print('This function does not have a demo.')

        """
        Options for projection
        symbol-search: Retrieve instrument data of a specific symbol or cusip
        symbol-regex: Retrieve instrument data for all symbols matching regex. Example: symbol=XYZ.* will
        desc-search: Retrieve instrument data for instruments whose description contains the word supplied. Example: symbol=FakeCompany will
        desc-regex: Search description with full regex support. Example: symbol=XYZ.[A-C]
        fundamental: Returns fundamental data for a single instrument specified by exact symbol.'
        """
        @staticmethod
        def getInstrument():
            print('This function is used to get instruments using a cusip')
            print("\tcusip: type=string, required")
            print('api.instruments.getInstrument(cusip); demo: cusip="007903107"')
            print(api.instruments.getInstrument("007903107"))

    class marketHours:
        @staticmethod
        def getHoursForMultipleMarkets():  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
            print("This function does not have a demo yet")

        @staticmethod
        def getHoursForASingleMarkets():  # date as "yyyy-MM-dd" OR "yyyy-MM-dd'T'HH:mm:ssz"
            print("This function does not have a demo yet")

    class movers:
        @staticmethod
        def getMovers():  # Working
            print('This function is used to get the top 10 movers for a specific market.')
            print('\tindex: type=string, required, format=$DJI')
            print('\tdirection: type=string, optional, format="up", "down"')
            print('\tchange: type=string, optional, format="value", "percent"')
            print('api.movers.getMovers(index); demo: index="$DJI", direction="up"')
            print(api.movers.getMovers("$DJI", direction="up"))
            print()

    class optionChains:
        @staticmethod
        def getOptionChain(**kwargs):
            print("This function does not have a demo yet")

    class priceHistory:
        @staticmethod
        def getPriceHistory(ticker, **kwargs):
            print("This function does not have a demo yet")

    class quotes:
        @staticmethod
        def getQuote():
            print('This function is used to a real-time quote for a single ticker.')
            print('Do NOT repeatably call this function for data, use streaming for continuous data.')
            print("\tticker: type=string, required")
            print('api.quotes.getQuote(ticker); demo: ticker="AMD"')
            print(api.quotes.getQuote("AMD"))

        @staticmethod
        def getQuotes():
            print('This function is used to a real-time quotes for a multiple ticker.')
            print('Do NOT repeatably call this function for data, use streaming for continuous data.')
            print("\ttickerList: type=list(string), required")
            print('api.quotes.getQuotes(tickerList); demo: ticker=["AMD","APPL"]')
            print(api.quotes.getQuotes(["AMD","APPL"]))

        @staticmethod
        def getDelayedQuote():
            print('This function is used to a ~15min DELAYED quote for a single ticker.')
            print('Do NOT repeatably call this function for data, use streaming for continuous data.')
            print("\tticker: type=string, required")
            print('api.quotes.getDelayedQuote(ticker); demo: ticker="AMD"')
            print(api.quotes.getDelayedQuote("AMD"))


    class transactionHistory:
        @staticmethod
        def getTransaction():
            print('This function is used to get details of a transaction from your account.')
            print("\ttransactionId: type=string/int, required")
            print('api.transactionHistory.getTransaction(transactionId)')
            print('This function does not have a demo.')

        @staticmethod
        def getTransactions(**kwargs):
            print('This function is used to get details of a transaction from your account.')
            print('\ttype: type=string, optional, format="ALL", "TRADE", "BUY_ONLY", "SELL_ONLY", "CASH_IN_OR_CASH_OUT", "CHECKING", "DIVIDEND", "INTEREST", "OTHER", "ADVISOR_FEES"')
            print('\tsymbol: type=string, optional')
            print('\tstartDate: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('\tendDate: type=string, optional, format="yyyy-MM-dd"(ISO-8601)')
            print('api.transactionHistory.getTransactions(**kwargs)')
            print('This function does not have a demo.')

    class userInfoAndPreferences:
        @staticmethod
        def getPreferences():
            print('This function is used to get preferences for accounts.')
            print('api.userInfoAndPreferences.getPreferences()')
            print(api.userInfoAndPreferences.getPreferences())

        @staticmethod
        def getStreamerSubscriptionKeys():
            print('This function is used to get subscription keys for streaming.')
            print('It is NOT recommended to use this function since it is used for core functionality of this program.')
            #print('\taccountIds: type=string, optional')
            print('api.userInfoAndPreferences.getStreamerSubscriptionKeys()')
            print('This function does not have a demo.')

        @staticmethod
        def getUserPrincipals():
            print('This function is used to get subscription keys for streaming.')
            print('\tfields: type=string, optional, format="streamerSubscriptionKeys", "streamerConnectionInfo", "preferences", "surrogateIds"')
            print('api.userInfoAndPreferences.getUserPrincipals(fields)')
            print(api.userInfoAndPreferences.getUserPrincipals())


        @staticmethod
        def updatePreferences():
            print('This function is used to update preferences for an account.')
            print('It is NOT recommended to use this function since you could change important settings.')
            print('\tdata: type=json, required')
            print('api.userInfoAndPreferences.updatePreferences(data)')
            print('This function does not have a demo.')

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


    class watchlist:
        @staticmethod
        def createWatchlist(data):  # FIX
            print("This function does not have a demo yet")

        @staticmethod
        def deleteWatchlist(watchListId):  # FIX
            print("This function does not have a demo yet")

        @staticmethod
        def getWatchlist(watchListId):  # FIX
            print("This function does not have a demo yet")


        @staticmethod
        def getWatchlistsForMultipleAccounts():  # FIX
            print("This function does not have a demo yet")


        @staticmethod
        def getWatchlistsForSingleAccount():  # FIX
            print("This function does not have a demo yet")

        @staticmethod
        def replaceWatchlist(watchListId, data):  # FIX
            print("This function does not have a demo yet")


        @staticmethod
        def updateWatchlist(watchListId, data):  # FIX
            print("This function does not have a demo yet")


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
