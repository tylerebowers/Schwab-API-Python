import requests
from datetime import datetime
from variables import credentials


def dateToEpoch(date):  # in format 'day/month/year hour/minute/second'
    return int((datetime.strptime(date, '%d/%m/%y %H:%M:%S') - datetime(1970, 1, 1)).seconds * 1000)


def getPriceHistory(ticker, periodType, period, frequencyType, frequency, needExtendedHoursData):
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/pricehistory',
                        params={'apikey': credentials.consumerKey,
                                'periodType': periodType,  # day, month, year, or ytd
                                'period': period,  # number of what you selected for periodType
                                'frequencyType': frequencyType,
                                # minute, weekly, monthly !! only periodType 'day' can do minute
                                'frequency': frequency,  # frequencyType minute can do 1,5,10,15,30; others only do 1
                                'needExtendedHoursData': needExtendedHoursData},  # boolean
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()


def getPriceHistoryDate(ticker, periodType, frequencyType, frequency, endDate, startDate, needExtendedHoursData):
    return requests.get('https://api.tdameritrade.com/v1/marketdata/' + str(ticker) + '/pricehistory',
                        params={'apikey': credentials.consumerKey,
                                'periodType': periodType,  # day, month, year, or ytd
                                'frequencyType': frequencyType,
                                # day: minute*, month: daily, weekly*, year: daily, weekly, monthly*, ytd: daily, weekly*
                                'frequency': frequency,  #
                                'endDate': dateToEpoch(endDate),  # end date in 'day/month/year hour/minute/second'
                                'startDate': dateToEpoch(startDate),
                                # start date in 'day/month/year hour/minute/second'
                                'needExtendedHoursData': needExtendedHoursData},  # boolean
                        headers={'Authorization': 'Bearer ' + credentials.accessToken}).json()


def candlestickFromCSV(csv):  # not finished
    csv


def candlestickListToCSV(data):  # not finished
    candleList = data.get('candles')
    for dict in candleList:
        dict


def help():
    return "https://developer.tdameritrade.com/price-history/apis/get/marketdata/%7Bsymbol%7D/pricehistory"
