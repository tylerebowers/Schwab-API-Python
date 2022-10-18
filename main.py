from apis import accountsAndTrading, authentication, instruments, marketHours, movers, optionChains, priceHistory, \
    quotes, transactionHistory, userInfoAndPreferences, watchlist
from modules import globals, utilities, user
from streaming import stream, levelOne, admin
from threading import Thread
from time import sleep


def main():

    print(instruments.getInstrument('AMD'))
    print(instruments.getInstrument('007903107'))
    print(movers.getMovers("$DJI", direction="up", change="percent"))
    print(optionChains.getOptionChain(symbol="AMD", contractType="CALL", includeQuotes="TRUE", range="ITM", toDate="2022-11-7"))
    print(priceHistory.getPriceHistory('AMD', periodType='day', period='1', frequencyType='minute', frequency='30', needExtendedHoursData='false'))
    print(quotes.getQuote('AMD'))
    print(quotes.getQuotes(['AMD', "INTC"]))
    """
    order = {'orderType': 'LIMIT', 'session': 'NORMAL', 'duration': 'DAY', 'orderStrategyType': 'SINGLE', 'price': '40.00',
                 'orderLegCollection': [{'instruction': 'Buy', 'quantity': 1, 'instrument': {'symbol': 'NDAQ', 'assetType': 'EQUITY'}}]}
    print(accountsAndTrading.placeOrder(order))
    
    sleep(1)

    print(accountsAndTrading.getOrdersByPath())

    print(accountsAndTrading.cancelOrder("Order Number"))
    """

    #for streaming
    #stream.send(levelOne.quoteRequest("AMD", [0, 3, 8]))
    #stream.send(levelOne.optionRequest("AMD", [0, 4, 8, 10]))
    #sleep(30)
    #stream.send(admin.logoutRequest())


if __name__ == '__main__':
    streaming = False
    user.login()
    mainThread = Thread(target=main)
    if streaming:
        streamThread = Thread(target=stream.start)
        streamThread.start()
        sleep(2)
    mainThread.start()
    if streaming:
        streamThread.join()
    mainThread.join()
