"""
Utilities
"""
import json.decoder
from datetime import datetime
import csv


def responseHandler(response):
    print(response)
    try:
        if response.ok:
            return response.json()
    except json.decoder.JSONDecodeError:
        return "[INFO] Nothing Returned"
    except AttributeError:
        return "[ERROR] Something else has been returned"


def kwargsHandler(args, kwargs):
    params = {}
    for key, value in kwargs.items():
        if key in args: params[key] = value
    return params


def listToString(ls):
    return ",".join(map(str, ls))


"""
functions below here are not used yet
"""

def log(requestId, sentData, receivedData):  # NOT WORKING nor used
    with open(str(datetime.now().date()) + '.csv', 'w') as file:
        writeToCsv = csv.writer(file)
        if requestId == 0:
            header = ['requestId', 'time', 'sentData', 'receivedData']
            writeToCsv.writerow(header)
        writeToCsv.writerow([requestId, datetime.now(), sentData, receivedData])


#def ISO8601


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
