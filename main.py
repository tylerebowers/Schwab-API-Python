from apis import client, accountsAndTrading, authentication, instruments, marketHours, movers, optionChains, priceHistory, quotes, transactionHistory, userInfoAndPreferences, watchlist
from stream import stream, levelOne
from variables import globals
from threading import Thread
from time import sleep


def main():  # these are some examples to get you started; remember to fill in globals.py
    print(quotes.getQuote('AMD'))
    print(priceHistory.getPriceHistory('AMD', periodType='day', period='1', frequencyType='minute', frequency='30', needExtendedHoursData='false'))
    stream.send(levelOne.quoteRequest("AMD", "3"))
    sleep(30)
    stream.send(stream.logoutRequest())


if __name__ == '__main__':
    client.login()
    mainThread = Thread(target=main)
    streamThread = Thread(target=stream.start)
    streamThread.start()
    sleep(2)
    mainThread.start()
    streamThread.join()
    mainThread.join()
