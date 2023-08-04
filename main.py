"""
This file is where all other apis and stream functions are called
"""
from modules import api, stream, database, universe
import threading 


def main():
    
    # These are api examples:
    print(api.instruments.getInstrument('AMD'))
    print(api.instruments.getInstrument('007903107'))
    print(api.movers.getMovers("$DJI", direction="up", change="percent"))
    print(api.optionChains.getOptionChain(symbol="AMD", contractType="CALL", includeQuotes="TRUE", range="ITM", toDate="2022-11-7"))
    print(api.priceHistory.getPriceHistory('AMD', periodType='day', period='1', frequencyType='minute', frequency='30', needExtendedHoursData='false'))
    print(api.quotes.getQuote('AMD'))
    print(api.quotes.getQuotes(['AMD', "INTC"]))
    stream.send(stream.levelOne.quote(["AMD", "INTC"], [0, 1, 2, 3, 4, 5, 8, 9, 24]))   #<--- you must ALWAYS send 0 in fields
    stream.send(stream.levelOne.futures(["/ES"], [0, 1, 2, 8])) #<-- futures/forex/options do not override orther types of subs.
    stream.send(stream.levelOne.forex(["EUR/USD"], [0, 1, 2, 8]))
    stream.send(stream.levelOne.option(["AMD"], [0, 2, 3, 8])) #Options dont work yet for some reason, maybe you can fix it?
    
    """
    # This is an example of a dynamically built order, It is commented out so you dont accidentally run it!
    ord = order.Order(orderType="LIMIT", session="NORMAL", duration="DAY", orderStrategyType="SINGLE", price=90)

    leg = order.Leg(instruction="Buy", quantity=1)
    ord.addLeg(leg)

    ins = order.Instrument(assetType="EQUITY", symbol="AMD", optionMultiplier="This is not included in compliation")
    leg.addInstrument(ins)
    
    ord.submit()
    
    
    # This is an example of a preset order, It is commented out so you dont accidentally run it!
    
    order.submit(order.presets.equity.buyLimited("AMD", 1, 90))
    
    # To cancel an order:
    
    accountsAndTrading.cancelOrder("Order Number")
    
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
    universe.threads.append(threading.Thread(target=api._checkTokensDaemon, daemon=True))  # thread that automatically updates tokens
    stream.startAutomatic(streamPreHours=False, streamAfterHours=False) # this starts the stream during market hours and stops it during non-market hours.
    #stream.startManual() # this starts the stream immediately (only use one type of stream start)
    universe.threads.append(threading.Thread(target=main)) # add the main thread to the list of threads to start
    for thread in universe.threads:
        thread.start()
    for thread in universe.threads:
        thread.join()
