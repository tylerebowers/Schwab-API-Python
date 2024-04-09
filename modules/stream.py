"""
This file contains functions to stream data
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import asyncio
import threading
import websockets
import websockets.exceptions
from time import sleep
from datetime import datetime, time
from window_terminal import WindowTerminal
from modules import universe, api

class streamVars:
    webSocket = None
    streamerInfo = None
    startTimeStamp = None
    terminal = None
    active = False
    requestId = 0
    streamURL = 'wss://streamer-api.schwab.com/ws'
    subscriptions = {}


async def _Start():
    streamVars.streamerInfo = api.userPreference.userPreference().get('streamerInfo', None)[0]
    if streamVars.streamerInfo is None:
        universe.terminal.error("could not get streamerInfo")
        exit(1)
    if streamVars.terminal is not None: streamVars.terminal.close()
    streamVars.terminal = WindowTerminal.create_window()
    streamVars.terminal.open()
    streamVars.requestId = 0
    login = {
        "service": "ADMIN",
        "requestid": streamVars.requestId,
        "command": "LOGIN",
        "SchwabClientCustomerId": streamVars.streamerInfo.get("schwabClientCustomerId"),
        "SchwabClientCorrelId": streamVars.streamerInfo.get("schwabClientCorrelId"),
        "parameters":
            {
                "Authorization": api.tokens.accessToken,
                "SchwabClientChannel": streamVars.streamerInfo.get("schwabClientChannel"),
                "SchwabClientFunctionId": streamVars.streamerInfo.get("schwabClientFunctionId")
            }
    }
    while True:
        try:
            streamVars.startTimeStamp = datetime.now()
            async with websockets.connect(streamVars.streamerInfo.get('streamerSocketUrl'), ping_interval=None) as streamVars.webSocket:
                streamVars.terminal.print("[INFO]: Connecting to server...")
                await streamVars.webSocket.send(json.dumps(login))
                streamVars.terminal.print(f"[Login]: {await streamVars.webSocket.recv()}")
                streamVars.active = True
                """
                for subType in streamVars.subscriptions:  # this resends what you have already sent (if the stream crashes).
                    if len(streamVars.subscriptions[subType]["keys"]) and len(
                            streamVars.subscriptions[subType]["fields"]):
                        await streamVars.webSocket.send(json.dumps({"requests": [utilities.basicRequest(service=subType, command="SUBS",
                                                                                      parameters={
                                                                                          "keys": utilities.listToString(
                                                                                              streamVars.subscriptions.get(
                                                                                                  subType).get("keys")),
                                                                                          "fields": utilities.listToString(
                                                                                              streamVars.subscriptions.get(
                                                                                                  subType).get(
                                                                                                  "fields"))})]}))
                        received = await streamVars.webSocket.recv()
                        streamVars.terminal.print(received)
                """
                while True:
                    received = await streamVars.webSocket.recv()
                    streamVars.terminal.print(received)
                    #_streamResponseHandler(received)
        except Exception as e:
            streamVars.active = False
            universe.terminal.error(f"{e}")
            if e is websockets.exceptions.ConnectionClosedOK:
                universe.terminal.info("Stream has closed.")
                break
            elif e is RuntimeError:
                universe.terminal.warning("Streaming window has beeen closed.")
                break
            else:
                if (datetime.now() - streamVars.startTimeStamp).seconds < 70:
                    universe.terminal.error("Stream not alive for more than 1 minute, exiting...")
                    break
                else:
                    streamVars.terminal.print("[WARNING]: Connection lost to server, reconnecting...")


def startManual():
    def start():
        asyncio.run(_Start())

    thread = threading.Thread(target=start)
    thread.start()


def startAutomatic(streamAfterHours=False, streamPreHours=False):
    start = time(9, 30, 0)
    end = time(16, 0, 0)
    if streamPreHours:
        start = time(8, 0, 0)
    if streamAfterHours:
        end = time(20, 0, 0)

    def checker():
        def _inHours():
            return (start <= datetime.now().time() <= end) and (0 <= datetime.now().weekday() <= 4)
        while True:
            if _inHours() and not streamVars.active:
                startManual()
            elif not _inHours() and streamVars.active:
                universe.terminal.info("Stopping Stream.")
                stop()
            sleep(60)
    threading.Thread(target=checker).start()

    if not start <= datetime.now().time() <= end:
        universe.terminal.info("Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    async def _send(toSend):
        await streamVars.webSocket.send(toSend)
    if type(listOfRequests) is not list:
        listOfRequests = [listOfRequests]
    if streamVars.active:
        toSend = json.dumps({"requests": listOfRequests})
        asyncio.run(_send(toSend))
    else:
        universe.terminal.warning("Stream is not active, nothing sent.")


def stop():
    streamVars.requestId += 1
    send({"service": "ADMIN", "requestid": streamVars.requestId, "command": "LOGOUT"})
    streamVars.active = False

"""

def _streamResponseHandler(streamOut):
    try:
        parentDict = json.loads(streamOut)
        for key in parentDict.keys():
            match key:
                case "notify":
                    streamVars.terminal.print(
                        f"[Heartbeat]: {utilities.epochMSToDate(parentDict['notify'][0]['heartbeat'])}")
                case "response":
                    for resp in parentDict.get('response'):
                        streamVars.terminal.print(f"[Response]: {resp}")
                case "snapshot":
                    for snap in parentDict.get('snapshot'):
                        streamVars.terminal.print(f"[Snapshot]: {snap}")
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
                                streamVars.terminal.print(
                                    f"[Data]: {tempSnapshot.toPrettyString()}")  # to stream output
                case _:
                    streamVars.terminal.print(f"[Unknown Response]: {streamOut}")
    except Exception as e:
        streamVars.terminal.print(f"[ERROR]: There was an error in decoding the stream response: {streamOut}")
        streamVars.terminal.print(f"[ERROR]: The error was: {e}")

class utilities:
    @staticmethod
    def request(command, service, keys, fields, recordRequest=True, addTickerToDB=True, accumulateSUBS=True):
        command = command.upper()
        service = service.upper()
        if recordRequest:
            if command == "SUBS":
                if accumulateSUBS:
                    streamVars.subscriptions[service]["keys"] = list(
                        set(streamVars.subscriptions[service]["keys"] + keys))
                    streamVars.subscriptions[service]["fields"] = list(
                        set(streamVars.subscriptions[service]["fields"] + fields))
                    keys = streamVars.subscriptions[service]["keys"]
                    fields = streamVars.subscriptions[service]["fields"]
                else:
                    streamVars.subscriptions[service]["keys"] = keys
                    streamVars.subscriptions[service]["fields"] = fields
            elif command == "UNSUBS":
                for key in keys:
                    streamVars.subscriptions[service]["keys"].pop(key)
            elif command == "ADD":
                streamVars.subscriptions[service]["keys"] = list(
                    set(streamVars.subscriptions[service]["keys"] + keys))
                streamVars.subscriptions[service]["fields"] = list(
                    set(streamVars.subscriptions[service]["fields"] + fields))
        elif not recordRequest and accumulateSUBS and command == "SUBS":
            keys = list(set(streamVars.subscriptions[service]["keys"] + keys))
            fields = list(set(streamVars.subscriptions[service]["fields"] + fields))

        if universe.preferences.usingDataframes and service in universe.dataframes:
            for key in keys:
                database.DFCreateTable(service.upper(), key, fields)

        if universe.preferences.usingDatabase and addTickerToDB and service in universe.streamFieldAliases:
            database.DBCreateTable(service.upper(), keys, fields)

        if streamVars.active:
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
        streamVars.requestId += 1
        args = ("service", "requestid", "command", "account", "source", "parameters")
        request = {"requestid": streamVars.requestId,
                   "account": streamVars.userPrincipals.get("accounts")[0].get("accountId"),
                   "source": streamVars.connectionInfo.get("appId")}
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
            for subType in streamVars.subscriptions:
                streamVars.subscriptions[subType]["keys"] = []
                streamVars.subscriptions[subType]["fields"] = []

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
            "userid": streamVars.userPrincipals.get("accounts")[0].get("accountId"),
            "token": streamVars.connectionInfo.get("token"),
            "company": streamVars.userPrincipals.get("accounts")[0].get("company"),
            "segment": streamVars.userPrincipals.get("accounts")[0].get("segment"),
            "cddomain": streamVars.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
            "usergroup": streamVars.connectionInfo.get("userGroup"),
            "accesslevel": streamVars.connectionInfo.get("accessLevel"),
            "authorized": "Y",
            "acl": streamVars.connectionInfo.get("acl"),
            "timestamp": int(datetime.timestamp(
                datetime.strptime(streamVars.connectionInfo.get('tokenTimestamp'),
                                  "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
            "appid": streamVars.connectionInfo.get("appId")
        }
        parameters = {"credential": urllib.parse.urlencode(credentialsDictionary),
                      "token": streamVars.connectionInfo.get("token"),
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
        
"""