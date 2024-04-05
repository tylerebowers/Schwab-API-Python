from modules import api, universe
from datetime import datetime, timedelta
import threading


def main():
    #You now have access to the api 
    #The tokens are stored here:
    #universe.tokens.accessToken
    #universe.tokens.refreshToken
    
    # get accounts numbers for linked accounts
    accountNumbers = api.accounts.accountNumbers()
    universe.credentials.encryptedId = accountNumbers[0].get('hashValue') #set encryped id in universe to set for orders
    print(accountNumbers)

    # get positions for linked accounts
    print(api.accounts.getLinkedAccounts())

    # get apecific account positions
    print(api.accounts.getAccount())

    # get up to 3000 orders for an account for the past week
    print(api.orders.getOrders(3000, datetime.now()-timedelta(days=7), datetime.now()))

    # place an order (not being demonstrated for ovbious reasons)
    # api.orders.placeOrder(orderObject)

    # get a specific order
    # api.orders.getOrder(orderID)

    # cancel specific order
    # api.orders.cancelOrder(orderID)

    # replace specific order
    # api.orders.replaceOrder(orderID)

    # get up to 3000 orders for all accounts for the past week
    print(api.orders.getAllOrders(3000, datetime.now()-timedelta(days=7), datetime.now()))

    # preview order (not implemented by Schwab yet
    # api.orders.previewOrder(orderObject)

    # get all transactions for an account
    print(api.transactions.transactions(datetime.now()-timedelta(days=7), datetime.now()))

    # get details for a specific transaction
    # print(api.transactions.details(transactionId))

    # get user preferences for an account
    print(api.userPreference.userPreference())

    # get a list of quotes
    print(api.quotes.getList(["AAPL", "AMD"]))

    # get a single quote
    print(api.quotes.getSingle("INTC"))

    # get a option chains
    # print(api.options.chains("AAPL")) # there are a lot to print

    #get an option expiration chain
    print(api.options.expirationChain("AAPL"))

    # get price history for a symbol
    # print(api.pricehistory.getPriceHistory("AAPL")) # there are a lot to print

    #get movers for an index
    print(api.movers.getMovers("$DJI"))

    #get marketHours for a symbol
    print(api.marketHours.getHours("AAPL"))

    #get marketHours for a market
    print(api.marketHours.byMarket("equity"))

    #get instruments for a symbol
    print(api.instruments.get("AAPL", "search"))

    #get instruments for a cusip
    print(api.instruments.byCusip("037833100"))  # 037833100 = AAPL



if __name__ == '__main__':
    print("Welcome to the unofficial Schwab api interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    api.initialize() # checks tokens & loads variables
    threads = [threading.Thread(target=main), threading.Thread(target=api._CheckTokensDaemon)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
