import json
from stream.stream import basicRequest
from variables import globals


def quoteRequest(ticker, fields):   # FIX
    globals.requestId += 1
    request = {
        "requests": [basicRequest(service="QUOTE", command="SUBS", parameters={"keys": ticker, "fields": "0,3"})]}
    return json.dumps(request)


def optionRequest(ticker, fields):   # FIX
    globals.requestId += 1
    request = {
        "requests": [basicRequest(service="OPTION", command="SUBS", parameters={"keys": ticker, "fields": "0,3"})]}
    return json.dumps(request)


def levelOne_FuturesRequest(ticker, fields):   # FIX
    globals.requestId += 1
    request = {
        "requests": [basicRequest(service="OPTION", command="SUBS", parameters={"keys": ticker, "fields": "0,3"})]}
    return json.dumps(request)
  
