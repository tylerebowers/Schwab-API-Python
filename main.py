"""
This file is where all other apis are called
Questions? You can find my contact info at tylerebowers.com
__author__ = Tyler Bowers
"""
from apis import accountsAndTrading, authentication, instruments, marketHours, movers, optionChains, priceHistory, \
    quotes, transactionHistory, userInfoAndPreferences, watchlist
from modules import globals, utilities, user
from streaming import stream, levelOne, admin
from threading import Thread
from time import sleep


def main():
    
    # These are api examples:
    print(instruments.getInstrument('AMD'))
    print(instruments.getInstrument('007903107'))
    print(movers.getMovers("$DJI", direction="up", change="percent"))
    print(optionChains.getOptionChain(symbol="AMD", contractType="CALL", includeQuotes="TRUE", range="ITM", toDate="2022-11-7"))
    print(priceHistory.getPriceHistory('AMD', periodType='day', period='1', frequencyType='minute', frequency='30', needExtendedHoursData='false'))
    print(quotes.getQuote('AMD'))
    print(quotes.getQuotes(['AMD', "INTC"]))
    stream.send(levelOne.quote(["META"], [0, 1, 2, 8])) #<--- whenever you send a stream sub you must always send 0.
    stream.send(levelOne.quote(["AMD", "INTC"], [0, 1, 2, 8]))   #<--- this sub overrides the one above it.
    stream.send(levelOne.futures(["/ES"], [0, 1, 2, 8])) #<-- futures/forex/options do not override orther types of subs.
    stream.send(levelOne.forex(["EUR/USD"], [0, 1, 2, 8]))
    stream.send(levelOne.option(["AMD"], [0, 2, 3, 8])) #Options dont work yet for some reason, maybe you can fix it?
    
    # This is an example of an order It is commented out so you dont accidentally run it!
    """
    order = {'orderType': 'LIMIT', 'session': 'NORMAL', 'duration': 'DAY', 'orderStrategyType': 'SINGLE', 'price': '30.00',
                 'orderLegCollection': [{'instruction': 'Buy', 'quantity': 1, 'instrument': {'symbol': 'NDAQ', 'assetType': 'EQUITY'}}]}
    print(accountsAndTrading.placeOrder(order))

    print(accountsAndTrading.getOrdersByPath())

    print(accountsAndTrading.cancelOrder("Order Number"))
    """
    """
    # if you want to enter your own commands while the stream is running
    while True:
        entered = input("Enter something to execute:\n")
        try:
            exec(entered)
            print("Succeeded")
        except Exception as error:
            print(error)
            print("There was an error in the command that you entered.")
    """      


if __name__ == '__main__':
    api.initialize()  # checks tokens & loads variables
    if universe.preferences.usingDatabase: database.DBConnect() # database code is incomplete
    api._checkTokensDaemon()  # thread that automatically updates tokens
    stream.startAutomatic() # this starts the stream during market hours and stops it during non-market hours.
    # stream.startManual() # this starts the stream immediately (only use one type of stream start)
    globals.threads.append(threading.Thread(target=main)) # add the main thread to the list of threads to start
    for thread in globals.threads:
        thread.start()
    for thread in globals.threads:
        thread.join()
