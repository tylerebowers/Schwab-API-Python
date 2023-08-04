"""
This file contains functions to stream data
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Client
"""

import json
import urllib
import asyncio
import threading
import websockets
import websockets.exceptions
from time import sleep
from datetime import datetime, time
from modules.api import userInfoAndPreferences
from window_terminal import WindowTerminal
from modules import universe, database



class _StreamVars:
    webSocket = None
    subscriptionKey = None
    connectionInfo = {}
    userPrincipals = {}
    requestId = 0
    terminal = None
    active = False

    subscriptions = {"QUOTE": {"keys": [], "fields": []},
                     "OPTION": {"keys": [], "fields": []},
                     "LEVELONE_FUTURES": {"keys": [], "fields": []},
                     "LEVELONE_FOREX": {"keys": [], "fields": []},
                     "LEVELONE_FUTURES_OPTIONS": {"keys": [], "fields": []},
                     "ACCT_ACTIVITY": {"keys": [], "fields": []},
                     "ACTIVES_NYSE": {"keys": [], "fields": []},
                     "ACTIVES_OTCBB": {"keys": [], "fields": []},
                     "ACTIVES_OPTIONS": {"keys": [], "fields": []},
                     "FOREX_BOOK": {"keys": [], "fields": []},
                     "FUTURES_BOOK": {"keys": [], "fields": []},
                     "LISTED_BOOK": {"keys": [], "fields": []},
                     "NASDAQ_BOOK": {"keys": [], "fields": []},
                     "OPTIONS_BOOK": {"keys": [], "fields": []},
                     "FUTURES_OPTIONS_BOOK": {"keys": [], "fields": []},
                     "CHART_EQUITY": {"keys": [], "fields": []},
                     "CHART_FUTURES": {"keys": [], "fields": []},
                     "NEWS_HEADLINE": {"keys": [], "fields": []},
                     "NEWS_HEADLINELIST": {"keys": [], "fields": []},
                     "NEWS_STORY": {"keys": [], "fields": []},
                     "TIMESALE_EQUITY": {"keys": [], "fields": []},
                     "TIMESALE_FOREX": {"keys": [], "fields": []},
                     "TIMESALE_FUTURES": {"keys": [], "fields": []},
                     "TIMESALE_OPTIONS": {"keys": [], "fields": []}}


def getQOS(qos=2):
    try:
        return [0.5, 0.75, 1.0, 1.5, 3.0, 5.0][int(qos)]
    except:
        return -1


def _setupStream():
    # if _StreamVars.subscriptionKey is None or _StreamVars.connectionInfo == {} or _StreamVars.userPrincipals == {}:
    if not universe.credentials.accountNumber.isdigit(): universe.terminal.error(
        "You must enter your account number for streaming in modules/universe.py")
    _StreamVars.subscriptionKey = userInfoAndPreferences.getStreamerSubscriptionKeys().get('keys')[0].get(
        'key')
    _StreamVars.connectionInfo = userInfoAndPreferences.getUserPrincipals(
        fields="streamerConnectionInfo").get(
        'streamerInfo')
    _StreamVars.userPrincipals = userInfoAndPreferences.getUserPrincipals()


async def _clientStart(qos=2):
    startTimeStamp = datetime.now()
    while True:
        try:
            _setupStream()
            websocketUrl = "wss://" + _StreamVars.connectionInfo.get('streamerSocketUrl') + "/ws"
            startTimeStamp = datetime.now()
            async with websockets.connect(websocketUrl, ping_interval=None) as _StreamVars.webSocket:
                _StreamVars.terminal.print("[INFO]: Connecting to server...")
                await _StreamVars.webSocket.send(json.dumps({"requests": [admin.login(qos)]}))
                _StreamVars.terminal.print(f"[Login]: {await _StreamVars.webSocket.recv()}")
                _StreamVars.active = True
                for subType in _StreamVars.subscriptions:  # this resends what you have already sent (if the stream crashes).
                    if len(_StreamVars.subscriptions[subType]["keys"]) and len(
                            _StreamVars.subscriptions[subType]["fields"]):
                        await _StreamVars.webSocket.send(json.dumps({"requests": [utilities.basicRequest(service=subType, command="SUBS",
                                                                                      parameters={
                                                                                          "keys": utilities.listToString(
                                                                                              _StreamVars.subscriptions.get(
                                                                                                  subType).get("keys")),
                                                                                          "fields": utilities.listToString(
                                                                                              _StreamVars.subscriptions.get(
                                                                                                  subType).get(
                                                                                                  "fields"))})]}))
                        received = await _StreamVars.webSocket.recv()
                        _StreamVars.terminal.print(received)
                while True:
                    received = await _StreamVars.webSocket.recv()
                    # _StreamVars.terminal.print(received)
                    _streamResponseHandler(received)

        except websockets.exceptions.ConnectionClosedOK as info:
            _StreamVars.active = False
            universe.terminal.info(f"{info}")
            universe.terminal.info("Stream has closed.")
            break
        except Exception as error:
            _StreamVars.active = False
            universe.terminal.error(f"{error}")
            if (datetime.now() - startTimeStamp).seconds < 70:
                universe.terminal.error("Stream not alive for more than 1 minute, exiting...")
                break
            else:
                _StreamVars.terminal.print("[WARNING]: Connection lost to server, reconnecting...")


async def _send(toSend):
    await _StreamVars.webSocket.send(toSend)


def startManual(qos=2):
    _StreamVars.terminal = WindowTerminal.create_window()
    _StreamVars.terminal.open()

    def _manStart():
        asyncio.run(_clientStart(qos=qos))

    universe.threads.append(threading.Thread(target=_manStart, daemon=True))


def startAutomatic(qos=2, streamAfterHours=False, streamPreHours=False):
    _StreamVars.terminal = WindowTerminal.create_window()
    _StreamVars.terminal.open()

    start = time(9, 30, 0)
    end = time(16, 0, 0)
    if streamPreHours:
        start = time(8, 0, 0)
    if streamAfterHours:
        end = time(20, 0, 0)

    def _inHours():
        return (start <= datetime.now().time() <= end) and (0 <= datetime.now().weekday() <= 4)

    def _autoStart():
        while True:
            if _inHours() and not _StreamVars.active:
                asyncio.run(_clientStart(qos=qos))
            sleep(60)

    def _autoStop():
        while True:
            if not _inHours() and _StreamVars.active:
                universe.terminal.info("Stopping Stream.")
                send(admin.logout())
                _StreamVars.active = False
            sleep(60)

    universe.threads.append(threading.Thread(target=_autoStart, daemon=True))
    universe.threads.append(threading.Thread(target=_autoStop, daemon=True))
    if not start <= datetime.now().time() <= end:
        universe.terminal.info("Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    if type(listOfRequests) != list: listOfRequests = [listOfRequests]
    if _StreamVars.active:
        toSend = json.dumps({"requests": listOfRequests})
        asyncio.run(_send(toSend))
    else:
        universe.terminal.warning("Stream is not active, nothing sent.")


def stop():
    send(admin.logout())


def _streamResponseHandler(streamOut):
    try:
        parentDict = json.loads(streamOut)
        for key in parentDict.keys():
            match key:
                case "notify":
                    _StreamVars.terminal.print(
                        f"[Heartbeat]: {utilities.epochMSToDate(parentDict['notify'][0]['heartbeat'])}")
                case "response":
                    for resp in parentDict.get('response'):
                        _StreamVars.terminal.print(f"[Response]: {resp}")
                case "snapshot":
                    for snap in parentDict.get('snapshot'):
                        _StreamVars.terminal.print(f"[Snapshot]: {snap}")
                case "data":
                    for data in parentDict.get("data"):
                        if data.get('service').upper() in universe.streamFieldAliases:
                            service = data.get("service")
                            timestamp = data.get("timestamp")
                            for symbolData in data.get("content"):
                                tempSnapshot = database.Snapshot(service, symbolData.get("key"), timestamp, symbolData)
                                if universe.preferences.usingDatabase:
                                    database.DBAddSnapshot(tempSnapshot)  # add to database
                                if universe.preferences.usingDataframes:
                                    database.DFAddSnapshot(tempSnapshot)  # add to dataframes
                                _StreamVars.terminal.print(
                                    f"[Data]: {tempSnapshot.toPrettyString()}")  # to stream output
                case _:
                    _StreamVars.terminal.print(f"[Unknown Response]: {streamOut}")
    except Exception as e:
        _StreamVars.terminal.print(f"[ERROR]: There was an error in decoding the stream response: {streamOut}")
        _StreamVars.terminal.print(f"[ERROR]: The error was: {e}")

class utilities:
    @staticmethod
    def request(command, service, keys, fields, recordRequest=True, addTickerToDB=True, accumulateSUBS=True):
        command = command.upper()
        service = service.upper()
        if recordRequest:
            if command == "SUBS":
                if accumulateSUBS:
                    _StreamVars.subscriptions[service]["keys"] = list(
                        set(_StreamVars.subscriptions[service]["keys"] + keys))
                    _StreamVars.subscriptions[service]["fields"] = list(
                        set(_StreamVars.subscriptions[service]["fields"] + fields))
                    keys = _StreamVars.subscriptions[service]["keys"]
                    fields = _StreamVars.subscriptions[service]["fields"]
                else:
                    _StreamVars.subscriptions[service]["keys"] = keys
                    _StreamVars.subscriptions[service]["fields"] = fields
            elif command == "UNSUBS":
                for key in keys:
                    _StreamVars.subscriptions[service]["keys"].pop(key)
            elif command == "ADD":
                _StreamVars.subscriptions[service]["keys"] = list(
                    set(_StreamVars.subscriptions[service]["keys"] + keys))
                _StreamVars.subscriptions[service]["fields"] = list(
                    set(_StreamVars.subscriptions[service]["fields"] + fields))
        elif not recordRequest and accumulateSUBS and command == "SUBS":
            keys = list(set(_StreamVars.subscriptions[service]["keys"] + keys))
            fields = list(set(_StreamVars.subscriptions[service]["fields"] + fields))

        if universe.preferences.usingDataframes and service in universe.dataframes:
            for key in keys:
                database.DFCreateTable(service.upper(), key, fields)

        if universe.preferences.usingDatabase and addTickerToDB and service in universe.streamFieldAliases:
            database.DBCreateTable(service.upper(), keys, fields)

        if _StreamVars.active:
            return utilities.basicRequest(service=service, command=command,
                                           parameters={"keys": utilities.listToString(keys),
                                                       "fields": utilities.listToString(fields)})
        else:
            if recordRequest:
                universe.terminal.info("Request(s) saved to send on stream start.")
            else:
                universe.terminal.info("Stream is not running and request was not saved.")

    @staticmethod
    def basicRequest(**kwargs):
        _StreamVars.requestId += 1
        args = ("service", "requestid", "command", "account", "source", "parameters")
        request = {"requestid": _StreamVars.requestId,
                   "account": _StreamVars.userPrincipals.get("accounts")[0].get("accountId"),
                   "source": _StreamVars.connectionInfo.get("appId")}
        for key, value in kwargs.items():
            if key in args: request[key] = value
        return request

    @staticmethod
    def listToString(ls):
        if type(ls) != list: ls = [ls]
        return ",".join(map(str, ls))

    @staticmethod
    def stringToList(ls):
        if type(ls) != list: ls = [ls]
        # if type(ls) != list: return ls.replace(" ", "").split(",")
        return ls

    @staticmethod
    def _ClearAllSubscriptions(confirm=False):
        if confirm:
            for subType in _StreamVars.subscriptions:
                _StreamVars.subscriptions[subType]["keys"] = []
                _StreamVars.subscriptions[subType]["fields"] = []

    @staticmethod
    def epochMSToDate(epochms):
        return datetime.fromtimestamp(int(epochms) / 1000).strftime('%c')



class account:
    @staticmethod
    def activity(keys, fields, command="SUBS"):
        return utilities.request(command, "ACCT_ACTIVITY", keys, fields)


class actives:
    @staticmethod
    def nasdaq(keys, fields, command="SUBS"):
        return utilities.request(command, "ACTIVES_NASDAQ", keys, fields)

    @staticmethod
    def nyse(keys, fields, command="SUBS"):
        return utilities.request(command, "ACTIVES_NYSE", keys, fields)

    @staticmethod
    def otcbb(keys, fields, command="SUBS"):
        return utilities.request(command, "ACTIVES_OTCBB", keys, fields)

    @staticmethod
    def options(keys, fields, command="SUBS"):
        return utilities.request(command, "ACTIVES_OPTIONS", keys, fields)


class admin:
    @staticmethod
    def login(qosLevel=2):
        credentialsDictionary = {
            "userid": _StreamVars.userPrincipals.get("accounts")[0].get("accountId"),
            "token": _StreamVars.connectionInfo.get("token"),
            "company": _StreamVars.userPrincipals.get("accounts")[0].get("company"),
            "segment": _StreamVars.userPrincipals.get("accounts")[0].get("segment"),
            "cddomain": _StreamVars.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
            "usergroup": _StreamVars.connectionInfo.get("userGroup"),
            "accesslevel": _StreamVars.connectionInfo.get("accessLevel"),
            "authorized": "Y",
            "acl": _StreamVars.connectionInfo.get("acl"),
            "timestamp": int(datetime.timestamp(
                datetime.strptime(_StreamVars.connectionInfo.get('tokenTimestamp'),
                                  "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
            "appid": _StreamVars.connectionInfo.get("appId")
        }
        parameters = {"credential": urllib.parse.urlencode(credentialsDictionary),
                      "token": _StreamVars.connectionInfo.get("token"),
                      "version": "1.0",
                      "qoslevel": qosLevel
                      }
        return utilities.basicRequest(service="ADMIN", command="LOGIN", parameters=parameters)

    @staticmethod
    def logout():
        return utilities.basicRequest(service="ADMIN", command="LOGOUT")

    @staticmethod
    def qos(qosLevel):
        return utilities.basicRequest(service="ADMIN", command="QOS", parameters={"qoslevel": qosLevel})


class book:
    @staticmethod
    def forex(keys, fields, command="SUBS"):
        return utilities.request(command, "FOREX_BOOK", keys, fields)

    @staticmethod
    def futures(keys, fields, command="SUBS"):
        return utilities.request(command, "FUTURES_BOOK", keys, fields)

    @staticmethod
    def listed(keys, fields, command="SUBS"):
        return utilities.request(command, "LISTED_BOOK", keys, fields)

    @staticmethod
    def nasdaq(keys, fields, command="SUBS"):
        return utilities.request(command, "NASDAQ_BOOK", keys, fields)

    @staticmethod
    def options(keys, fields, command="SUBS"):
        return utilities.request(command, "OPTIONS_BOOK", keys, fields)

    @staticmethod
    def futures_options(keys, fields, command="SUBS"):
        return utilities.request(command, "FUTURES_OPTIONS_BOOK", keys, fields)


class chart:
    @staticmethod
    def equity(keys, fields, command="SUBS"):
        return utilities.request(command, "CHART_EQUITY", keys, fields)

    @staticmethod
    def futures(keys, fields, command="SUBS"):
        return utilities.request(command, "CHART_FUTURES", keys, fields)


class levelOne:
    @staticmethod
    def quote(keys, fields, command="SUBS"):
        return utilities.request(command, "QUOTE", keys, fields)

    @staticmethod
    def option(keys, fields, command="SUBS"):
        return utilities.request(command, "OPTION", keys, fields)

    @staticmethod
    def futures(keys, fields, command="SUBS"):
        return utilities.request(command, "LEVELONE_FUTURES", keys, fields)

    @staticmethod
    def forex(keys, fields, command="SUBS"):
        return utilities.request(command, "LEVELONE_FOREX", keys, fields)

    @staticmethod
    def futures_options(keys, fields, command="SUBS"):
        return utilities.request(command, "LEVELONE_FUTURES_OPTIONS", keys, fields)


class levelTwo:
    @staticmethod
    def _NA():
        print("Not Available")


class news:
    @staticmethod
    def headline(keys, fields, command="SUBS"):
        return utilities.request(command, "NEWS_HEADLINE", keys, fields)

    @staticmethod
    def headlineList(keys, fields, command="SUBS"):
        return utilities.request(command, "NEWS_HEADLINELIST", keys, fields)

    @staticmethod
    def headlineStory(keys, fields, command="SUBS"):
        return utilities.request(command, "NEWS_STORY", keys, fields)


class timeSale:
    @staticmethod
    def equity(keys, fields, command="SUBS"):
        return utilities.request(command, "TIMESALE_EQUITY", keys, fields)

    @staticmethod
    def forex(keys, fields, command="SUBS"):
        return utilities.request(command, "TIMESALE_FOREX", keys, fields)

    @staticmethod
    def futures(keys, fields, command="SUBS"):
        return utilities.request(command, "TIMESALE_FUTURES", keys, fields)

    @staticmethod
    def options(keys, fields, command="SUBS"):
        return utilities.request(command, "TIMESALE_OPTIONS", keys, fields)

