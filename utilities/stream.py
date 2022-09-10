import asyncio
import csv
import json
import urllib
from datetime import datetime
import websockets
from variables import credentials
from threading import Thread
from window_terminal import WindowTerminal

requestId = 0
logging = True


def loginRequest(qosLevel):
    global requestId
    credentialsDictionary = {
        "userid": credentials.userPrincipals.get("accounts")[0].get("accountId"),
        "token": credentials.streamerConnectionInfo.get("token"),
        "company": credentials.userPrincipals.get("accounts")[0].get("company"),
        "segment": credentials.userPrincipals.get("accounts")[0].get("segment"),
        "cddomain": credentials.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
        "usergroup": credentials.streamerConnectionInfo.get("userGroup"),
        "accesslevel": credentials.streamerConnectionInfo.get("accessLevel"),
        "authorized": "Y",
        "acl": credentials.streamerConnectionInfo.get("acl"),
        "timestamp": int(datetime.timestamp(
            datetime.strptime(credentials.streamerConnectionInfo.get('tokenTimestamp'), "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
        "appid": credentials.streamerConnectionInfo.get("appId")
    }
    request = {
        "requests": [
            {
                "service": "ADMIN",
                "requestid": requestId,
                "command": "LOGIN",
                "account": credentials.userPrincipals.get("accounts")[0].get("accountId"),
                "source": credentials.streamerConnectionInfo.get("appId"),  # causing problems?
                "parameters": {
                    "credential": urllib.parse.urlencode(credentialsDictionary),  # causing problems?
                    "token": credentials.streamerConnectionInfo.get("token"),
                    "version": "1.0",
                    "qoslevel": qosLevel
                }
            }
        ]
    }
    requestId += 1
    return json.dumps(request)


def subscribeRequest(ticker):
    global requestId
    request = {
        "requests": [
            {
                "service": "QUOTE",
                "command": "SUBS",
                "requestid": requestId,
                "account": credentials.userPrincipals.get("accounts")[0].get("accountId"),
                "source": credentials.streamerConnectionInfo.get("appId"),
                "parameters": {
                    "keys": ticker,
                    "fields": "0,3"
                }
            }
        ]
    }
    requestId += 1
    return json.dumps(request)


def genericRequest(service, command, parameters):  # service & command are strings; parameters is a dictionary
    global requestId
    request = {
        "requests": [
            {
                "service": service,
                "command": command,
                "requestid": requestId,
                "account": credentials.userPrincipals.get("accounts")[0].get("accountId"),
                "source": credentials.streamerConnectionInfo.get("appId"),
                "parameters": parameters
            }
        ]
    }
    requestId += 1
    return json.dumps(request)


def log(requestId, sentData, receivedData):  # NOT WORKING
    with open(str(datetime.now().date()) + '.csv', 'w') as file:
        writeToCsv = csv.writer(file)
        if requestId == 0:
            header = ['requestId', 'time', 'sentData', 'receivedData']
            writeToCsv.writerow(header)
        writeToCsv.writerow([requestId, datetime.now(), sentData, receivedData])


async def startStream():
    websocketUrl = "wss://" + credentials.streamerConnectionInfo.get('streamerSocketUrl') + "/ws"
    streamOutput = WindowTerminal.create_window()
    streamOutput.open()
    try:
        async with websockets.connect(websocketUrl) as websocket:
            await websocket.send(loginRequest(2))
            streamOutput.print(await websocket.recv())
            await websocket.send(subscribeRequest("AMD"))
            while True:
                streamOutput.print(await websocket.recv())
    except KeyboardInterrupt:
        print("Interrupted execution by user.")
        websocket.stop_ws()  # change to send logout!
        exit(0)
    except Exception as excep:
        print("Exception: {}. continuing...".format(excep))
        pass

