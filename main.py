from modules import api, stream
from datetime import datetime, timedelta


def main():
    # get accounts numbers for linked accounts
    print(api.accounts.accountNumbers().json())

    # get positions for linked accounts
    print(api.accounts.getAllAccounts().json())

    # get specific account positions
    print(api.accounts.getAccount(fields="positions").json())

    # get up to 3000 orders for an account for the past week
    print(api.orders.getOrders(3000, datetime.now() - timedelta(days=7), datetime.now()).json())

    """
    # place an order (uncomment to test)
    order = {"orderType": "LIMIT", "session": "NORMAL", "duration": "DAY", "orderStrategyType": "SINGLE", "price": '10.00',
         "orderLegCollection": [
             {"instruction": "BUY", "quantity": 1, "instrument": {"symbol": "INTC", "assetType": "EQUITY"}}]}
    resp = api.orders.placeOrder(order)
    print(f"Place order response: {resp}")
    orderID = resp.headers.get('location', '/').split('/')[-1]
    print(f"OrderID: {orderID}")

    # get a specific order
    print(api.orders.getOrder(orderID).json())

    # cancel specific order
    print(api.orders.cancelOrder(orderID))
    """

    # replace specific order
    # api.orders.replaceOrder(orderID, order)

    # get up to 3000 orders for all accounts for the past week
    print(api.orders.getAllOrders(3000, datetime.now() - timedelta(days=7), datetime.now()).json())

    # preview order (not implemented by Schwab yet
    # api.orders.previewOrder(orderObject)

    # get all transactions for an account
    print(api.transactions.transactions(datetime.now() - timedelta(days=7), datetime.now(), "TRADE").json())

    # get details for a specific transaction
    # print(api.transactions.details(transactionId).json())

    # get user preferences for an account
    print(api.userPreference.userPreference().json())

    # get a list of quotes
    print(api.quotes.getList(["AAPL", "AMD"]).json())

    # get a single quote
    print(api.quotes.getSingle("INTC").json())

    # get a option chains
    # print(api.options.chains("AAPL").json()) # there are a lot to print

    # get an option expiration chain
    print(api.options.expirationChain("AAPL").json())

    # get price history for a symbol
    # print(api.priceHistory.bySymbol("AAPL").json()) # there is a lot to print

    # get movers for an index
    print(api.movers.getMovers("$DJI").json())

    # get marketHours for a symbol
    print(api.marketHours.byMarkets("equity,option").json())

    # get marketHours for a market
    print(api.marketHours.byMarket("equity").json())

    # get instruments for a symbol
    print(api.instruments.bySymbol("AAPL", "search").json())

    # get instruments for a cusip
    print(api.instruments.byCusip("037833100").json())  # 037833100 = AAPL

    """
    # send a subscription request to the stream (uncomment if you start the stream below)
    stream.send(stream.utilities.basicRequest("CHART_EQUITY", "SUBS", parameters={"keys": "AMD,INTC", "fields": "0,1,2,3,4,5,6,7,8"}))
    
    # stop the stream
    stream.stop()
    """



if __name__ == '__main__':
    print("Welcome to the unofficial Schwab api interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    api.initialize()  # checks tokens & loads variables
    api.updateTokensAutomatic()  # starts thread to update tokens automatically
    #stream.startManual()  # start the stream manually
    main()  # call the user code above
