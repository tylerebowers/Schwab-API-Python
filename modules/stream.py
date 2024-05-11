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
from modules import terminal, api


class streamVars:
    webSocket = None
    streamerInfo = None
    startTimeStamp = None
    terminal = None
    active = False
    requestId = 0
    subscriptions = {}


async def _Start():
    response = api.userPreference.userPreference()
    if response.ok:
        streamVars.streamerInfo = response.json().get('streamerInfo', None)[0]
    else:
        terminal.colorPrint.error("Could not get streamerInfo")
        exit(1)
    if streamVars.terminal is None:
        streamVars.terminal = terminal.multiTerminal(title="Stream output")
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
            async with websockets.connect(streamVars.streamerInfo.get('streamerSocketUrl'),
                                          ping_interval=None) as streamVars.webSocket:
                streamVars.terminal.print("[INFO]: Connecting to server...")
                await streamVars.webSocket.send(json.dumps(login))
                streamVars.terminal.print(f"[Login]: {await streamVars.webSocket.recv()}")
                streamVars.active = True
                # TODO: resend requests if the stream crashes
                while True:
                    received = await streamVars.webSocket.recv()
                    streamVars.terminal.print(received)
                    # TODO: make something that the user can work with
                    # _streamResponseHandler(received)
        except Exception as e:
            streamVars.active = False
            terminal.colorPrint.error(f"{e}")
            if e is websockets.exceptions.ConnectionClosedOK:
                terminal.colorPrint.info("Stream has closed.")
                break
            elif e is RuntimeError:
                terminal.colorPrint.warning("Streaming window has beeen closed.")
                break
            else:
                if (datetime.now() - streamVars.startTimeStamp).seconds < 70:
                    terminal.colorPrint.error("Stream not alive for more than 1 minute, exiting...")
                    break
                else:
                    streamVars.terminal.print("[WARNING]: Connection lost to server, reconnecting...")


def startManual():
    def start():
        asyncio.run(_Start())

    thread = threading.Thread(target=start).start()


def startAutomatic(streamAfterHours=False, streamPreHours=False):
    start = time(9, 30, 0)  # market opens at 9:30
    end = time(16, 0, 0)  # market closes at 4:00
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
                terminal.colorPrint.info("Stopping Stream.")
                stop()
            sleep(60)

    threading.Thread(target=checker).start()

    if not start <= datetime.now().time() <= end:
        terminal.colorPrint.info("Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    async def _send(toSend):
        await streamVars.webSocket.send(toSend)

    if type(listOfRequests) is not list:
        listOfRequests = [listOfRequests]
    if streamVars.active:
        toSend = json.dumps({"requests": listOfRequests})
        asyncio.run(_send(toSend))
    else:
        terminal.colorPrint.warning("Stream is not active, nothing sent.")


def stop():
    streamVars.requestId += 1
    send(utilities.basicRequest("ADMIN", "LOGOUT"))
    streamVars.active = False


"""
{
    "requests":
    [
        {
            "service": "LEVELONE_FOREX",
            "requestid": 1,
            "command": "SUBS",
            "SchwabClientCustomerId": "<streamerInfo[0].schwabClientCustomerId>",
            "SchwabClientCorrelId": "<streamerInfo[0].schwabClientCorrelId>",
            "parameters":
            {
                "keys": "EUR/USD",
                "fields": "0,1,2,3,4,5,6,8,9,10,11,12,16,17,18,19,20,33,35,39,40,41,42"
            }
        }
    ]
}


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
"""


class utilities:
    @staticmethod
    def basicRequest(service, command, parameters=None):
        streamVars.requestId += 1
        request = {"service": service.upper(),
                   "command": command.upper(),
                   "requestid": streamVars.requestId,
                   "SchwabClientCustomerId": streamVars.streamerInfo.get("schwabClientCustomerId"),
                   "SchwabClientCorrelId": streamVars.streamerInfo.get("schwabClientCorrelId")}
        if parameters is not None: request["parameters"] = parameters
        print(request)
        return request


"""
    @staticmethod
    def listToString(ls):
        if type(ls) != list: ls = [ls]
        return ",".join(map(str, ls))

    @staticmethod
    def stringToList(ls):
        if type(ls) != list: ls = [ls]
        # if type(ls) != list: return ls.replace(" ", "").split(",")
        return ls

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
