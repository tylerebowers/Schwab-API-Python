"""
The "fields" variable is sent as a list

"""


import json
from streaming import utilities
from modules import globals


def quoteRequest(ticker, fields):
    globals.requestId += 1
    request = {
        "requests": [utilities.basicRequest(service="QUOTE", command="SUBS", parameters={"keys": ticker, "fields": utilities.listToString(fields)})]}
    return json.dumps(request)


def optionRequest(ticker, fields):
    globals.requestId += 1
    request = {
        "requests": [utilities.basicRequest(service="OPTION", command="SUBS", parameters={"keys": ticker, "fields": utilities.listToString(fields)})]}
    return json.dumps(request)


def levelOne_FuturesRequest(ticker, fields):
    globals.requestId += 1
    request = {
        "requests": [utilities.basicRequest(service="OPTION", command="SUBS", parameters={"keys": ticker, "fields": utilities.listToString(fields)})]}
    return json.dumps(request)