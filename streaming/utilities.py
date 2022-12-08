import json
from datetime import datetime
from modules import globals


def SUBS(service, keys, fields, log=True):
    if globals.streamIsActive:
        if log:
            for key in keys:
                globals.streamSubscriptions[service][key] = fields
        return basicRequest(service=service.upper(), command="SUBS",
                            parameters={"keys": listToString(keys),
                                        "fields": listToString(fields)})
    else:
        if log:
            for key in keys:
                globals.streamSubscriptions[service][key] = fields
            print("INFO: Request has been saved to be sent on stream start.")


def UNSUBS(service, keys):
    if globals.streamIsActive:
        for key in keys:
            globals.streamSubscriptions[service].pop(key)
        return basicRequest(service=service.upper(), command="UNSUBS",
                            parameters={"keys": listToString(keys)})
    else:
        print("WARNING: Stream is not active, nothing sent")


def ADD(service, keys, fields):
    if globals.streamIsActive:
        if type(keys) != list:
            keys = [keys]
        return basicRequest(service=service.upper(), command="ADD",
                            parameters={"keys": listToString(keys),
                                        "fields": listToString(fields)})
    else:
        print("WARNING: Stream is not active, nothing sent")


def basicRequest(**kwargs):
    globals.requestId += 1
    args = ["service", "requestid", "command", "account", "source", "parameters"]
    request = {"requestid": globals.requestId, "account": globals.userPrincipals.get("accounts")[0].get("accountId"),
               "source": globals.streamerConnectionInfo.get("appId")}
    for key, value in kwargs.items():
        if key in args: request[key] = value
    return request


def listToString(ls):
    if type(ls) != list: ls = [ls]
    return ",".join(map(str, ls))


def stringToList(ls):
    if type(ls) != list: ls = [ls]
    return ls


def clearSubscriptions():
    for subType in globals.streamSubscriptions:
        globals.streamSubscriptions[subType].clear()


def dateToEpochMS(date):  # in format 'day/month/year hour/minute/second'
    return int((datetime.strptime(date, '%d/%m/%y %H:%M:%S') - datetime(1970, 1, 1)).seconds * 1000)


def epochMSToDate(epochms):
    return datetime.fromtimestamp(int(epochms) / 1000).strftime('%c')


def logRequest(request):
    json.loads(request).get("requests")  # now you have a list of the requests
    return
    # make a variable for sub
    # remember that unsubs could cancel out subs
    # execute the log of this functon if stream crashes


def streamResponseHandler(streamOut):
    try:
        parentDict = json.loads(streamOut)
        for key in parentDict.keys():
            match key:
                case "notify":
                    print("[Heartbeat]: ", end="")
                    print(epochMSToDate(parentDict["notify"][0]["heartbeat"]))
                case "response":
                    print("do somthing")
                case "snapshot":
                    print("do a ton of stuff")
                case "data":
                    print("do a ton of stuff")
                case _:
                    print("bruh idk what happened")
    except Exception as e:
        print("[ERROR]: There was an error in decoding the stream output: ", end="")
        print(e)
    return
