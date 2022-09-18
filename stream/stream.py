import asyncio
import json
import urllib
from datetime import datetime
import websockets

from apis import userInfoAndPreferences
from variables import globals
from window_terminal import WindowTerminal


global ws, streamOutput


def setupStream():
    globals.streamerSubscriptionKey = userInfoAndPreferences.getStreamerSubscriptionKeys().get('keys')[0].get('key')
    globals.streamerConnectionInfo = userInfoAndPreferences.getUserPrincipals(fields="streamerConnectionInfo").get(
        'streamerInfo')
    globals.userPrincipals = userInfoAndPreferences.getUserPrincipals()


async def clientStart():
    global ws, streamOutput
    if globals.streamerSubscriptionKey is None or globals.streamerConnectionInfo == {} or globals.userPrincipals == {}:
        setupStream()
    if globals.terminalOutput:
        streamOutput = WindowTerminal.create_window()
        streamOutput.open()
    websocketUrl = "wss://" + globals.streamerConnectionInfo.get('streamerSocketUrl') + "/ws"
    async with websockets.connect(websocketUrl) as ws:
        await ws.send(loginRequest(2))
        if globals.terminalOutput:
            streamOutput.print(await ws.recv())
        while True:
            received = await ws.recv()
            if globals.terminalOutput:
                streamOutput.print(received)


async def clientSend(toSend):
    global ws
    await ws.send(toSend)


def loginRequest(qosLevel):
    globals.requestId += 1
    credentialsDictionary = {
        "userid": globals.userPrincipals.get("accounts")[0].get("accountId"),
        "token": globals.streamerConnectionInfo.get("token"),
        "company": globals.userPrincipals.get("accounts")[0].get("company"),
        "segment": globals.userPrincipals.get("accounts")[0].get("segment"),
        "cddomain": globals.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
        "usergroup": globals.streamerConnectionInfo.get("userGroup"),
        "accesslevel": globals.streamerConnectionInfo.get("accessLevel"),
        "authorized": "Y",
        "acl": globals.streamerConnectionInfo.get("acl"),
        "timestamp": int(datetime.timestamp(
            datetime.strptime(globals.streamerConnectionInfo.get('tokenTimestamp'), "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
        "appid": globals.streamerConnectionInfo.get("appId")
    }
    parameters = {"credential": urllib.parse.urlencode(credentialsDictionary),
                  "token": globals.streamerConnectionInfo.get("token"),
                  "version": "1.0",
                  "qoslevel": qosLevel
                  }
    request = {"requests": [basicRequest(service="ADMIN", command="LOGIN", parameters=parameters)]}
    return json.dumps(request)


def logoutRequest():
    globals.requestId += 1
    request = {
        "requests": [basicRequest(service="ADMIN", command="LOGOUT", parameters={})]}
    return json.dumps(request)


def basicRequest(**kwargs):
    globals.requestId += 1
    args = ["service", "requestid", "command", "account", "source", "parameters"]
    request = {"requestid": globals.requestId, "account": globals.userPrincipals.get("accounts")[0].get("accountId"),
               "source": globals.streamerConnectionInfo.get("appId")}
    for key, value in kwargs.items():
        if key in args: request[key] = value
    return request


def start():
    asyncio.run(clientStart())


def send(toSend):
    asyncio.run(clientSend(toSend))
