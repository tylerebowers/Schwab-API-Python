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
    
    # This is an example of an order It is commented out so you dont accidentally run it!
    """
    order = {'orderType': 'LIMIT', 'session': 'NORMAL', 'duration': 'DAY', 'orderStrategyType': 'SINGLE', 'price': '30.00',
                 'orderLegCollection': [{'instruction': 'Buy', 'quantity': 1, 'instrument': {'symbol': 'NDAQ', 'assetType': 'EQUITY'}}]}
    print(accountsAndTrading.placeOrder(order))

    print(accountsAndTrading.getOrdersByPath())

    print(accountsAndTrading.cancelOrder("Order Number"))
    """
    """
    # These Commands are used for streaming (Keep in mind that the TD will close the stream if you arent subbed to anything)
    stream.send(levelOne.quote(["META"], [0, 1, 2, 8]))
    stream.send(levelOne.quote(["AMD", "INTC"], [0, 1, 2, 8]))
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
    # if globals.usingDatabase: database.initializeDatabase()
    api.checkTokensDaemon()  # thread that automatically updates tokens
    stream.startAutomatic()
    globals.threads.append(threading.Thread(target=main))
    for thread in globals.threads:
        thread.start()
    for thread in globals.threads:
        thread.join()
