import json
from datetime import datetime
from modules import universe, database


def request(command, service, keys, fields, recordRequest=True, addTickerToDB=True, accumulateSUBS=True):
    command = command.upper()
    service = service.upper()
    if recordRequest:
        if command == "SUBS":
            if accumulateSUBS:
                universe.stream.subscriptions[service]["keys"] = list(set(universe.stream.subscriptions[service]["keys"]+keys))
                universe.stream.subscriptions[service]["fields"] = list(set(universe.stream.subscriptions[service]["fields"]+fields))
                keys = universe.stream.subscriptions[service]["keys"]
                fields = universe.stream.subscriptions[service]["fields"]
            else:
                universe.stream.subscriptions[service]["keys"] = keys
                universe.stream.subscriptions[service]["fields"] = fields
        elif command == "UNSUBS":
            for key in keys:
                universe.stream.subscriptions[service]["keys"].pop(key)
        elif command == "ADD":
            universe.stream.subscriptions[service]["keys"] = list(set(universe.stream.subscriptions[service]["keys"] + keys))
            universe.stream.subscriptions[service]["fields"] = list(set(universe.stream.subscriptions[service]["fields"] + fields))
    elif not recordRequest and accumulateSUBS and command == "SUBS":
        keys = list(set(universe.stream.subscriptions[service]["keys"] + keys))
        fields = list(set(universe.stream.subscriptions[service]["fields"] + fields))

    if universe.preferences.usingDataframes and service.upper() in universe.dataframes:
        for key in keys:
            database.DFCreateTable(service.upper(), key, fields)

    if universe.preferences.usingDatabase and addTickerToDB and service.upper() in universe.stream.fieldAliases:
        database.DBCreateTable(service.upper(), keys, fields)

    if universe.stream.active:
        return basicRequest(service=service, command=command,
                            parameters={"keys": listToString(keys), "fields": listToString(fields)})
    else:
        if recordRequest:
            print("[INFO]: Request(s) saved to send on stream start.")
        else:
            print("[INFO]: Stream is not running and request was not saved.")


def basicRequest(**kwargs):
    universe.stream.requestId += 1
    args = ["service", "requestid", "command", "account", "source", "parameters"]
    request = {"requestid": universe.stream.requestId, "account": universe.stream.userPrincipals.get("accounts")[0].get("accountId"),
               "source": universe.stream.connectionInfo.get("appId")}
    for key, value in kwargs.items():
        if key in args: request[key] = value
    return request


def listToString(ls):
    if type(ls) != list: ls = [ls]
    return ",".join(map(str, ls))


def stringToList(ls):
    if type(ls) != list: ls = [ls]
    #if type(ls) != list: return ls.replace(" ", "").split(",")
    return ls


def clearAllSubscriptions(confirm=False):
    if confirm:
        for subType in universe.stream.subscriptions:
            universe.stream.subscriptions[subType]["keys"] = []
            universe.stream.subscriptions[subType]["fields"] = []


def epochMSToDate(epochms):
    return datetime.fromtimestamp(int(epochms) / 1000).strftime('%c')