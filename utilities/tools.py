"""
Tools for usage in analysis
"""
from datetime import datetime


def dateToEpoch(date):  # in format 'day/month/year hour/minute/second'
    return int((datetime.strptime(date, '%d/%m/%y %H:%M:%S') - datetime(1970, 1, 1)).seconds * 1000)


def candlestickFromCSV(csv):  # not finished
    return


def candlestickListToCSV(data):  # not finished
    candleList = data.get('candles')
    for dictionary in candleList:
        # some more thinking to do.
        continue
    return
