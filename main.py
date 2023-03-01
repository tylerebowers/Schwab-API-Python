"""
This file is where all other apis and stream functions are called
"""
from apis import quotes, instruments, movers, optionChains, priceHistory
from modules import api, stream, database, universe
from streaming import levelOne
import threading 


def main():
    
    # These are api examples:
    print(instruments.getInstrument('AMD'))
    print(instruments.getInstrument('007903107'))
    print(movers.getMovers("$DJI", direction="up", change="percent"))
    print(optionChains.getOptionChain(symbol="AMD", contractType="CALL", includeQuotes="TRUE", range="ITM", toDate="2022-11-7"))
    print(priceHistory.getPriceHistory('AMD', periodType='day', period='1', frequencyType='minute', frequency='30', needExtendedHoursData='false'))
    print(quotes.getQuote('AMD'))
    print(quotes.getQuotes(['AMD', "INTC"]))
    stream.send(levelOne.quote(["AMD", "INTC"], [0, 1, 2, 3, 4, 5, 8, 9, 24]))   #<--- you must ALWAYS send 0 in fields
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
    prev = ""
    history = []
    while True:
        try:
            entered = input("[INPUT]: Enter something to execute:\n")
            if entered == "":
                exec(prev)
                history.append(prev)
            else:
                exec(entered)
                prev = entered
                history.append(entered)
            print("Succeeded")
        except Exception as error:
            print(error)
            print("There was an error in the command that you entered.")
    """      


if __name__ == '__main__':
    api.initialize()  # checks tokens & loads variables
    if universe.preferences.usingDatabase: database.DBConnect() # database code is incomplete
    api._checkTokensDaemon()  # thread that automatically updates tokens
    stream._startAutomatic() # this starts the stream during market hours and stops it during non-market hours.
    #stream._startManual() # this starts the stream immediately (only use one type of stream start)
    universe.threads.append(threading.Thread(target=main)) # add the main thread to the list of threads to start
    for thread in universe.threads:
        thread.start()
    for thread in universe.threads:
        thread.join()
