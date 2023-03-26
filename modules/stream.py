"""
This file stores variables to be used between python files and functions
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Wrapper
"""

import json
import asyncio
import threading
import websockets
import websockets.exceptions
from time import sleep
from datetime import datetime, time
from streaming import admin, utilities
from apis import userInfoAndPreferences
from window_terminal import WindowTerminal
from modules import universe, database

global ws


def _setupStream():
    # if universe.stream.subscriptionKey is None or universe.stream.connectionInfo == {} or universe.stream.userPrincipals == {}:
    if not universe.credentials.accountNumber.isdigit(): universe.terminal.error("You must enter your account number for streaming in modules/universe.py")
    universe.stream.subscriptionKey = userInfoAndPreferences.getStreamerSubscriptionKeys().get('keys')[0].get(
        'key')
    universe.stream.connectionInfo = userInfoAndPreferences.getUserPrincipals(
        fields="streamerConnectionInfo").get(
        'streamerInfo')
    universe.stream.userPrincipals = userInfoAndPreferences.getUserPrincipals()


async def _clientStart(qos=universe.preferences.streamingQOSLevel):
    global ws
    startTimeStamp = datetime.now()
    while True:
        try:
            _setupStream()
            websocketUrl = "wss://" + universe.stream.connectionInfo.get('streamerSocketUrl') + "/ws"
            startTimeStamp = datetime.now()
            async with websockets.connect(websocketUrl, ping_interval=None) as ws:
                universe.stream.terminal.print("[INFO]: Connecting to server...")
                await ws.send(json.dumps({"requests": [admin.login(qos)]}))
                universe.stream.terminal.print(f"[Login]: {await ws.recv()}")
                universe.stream.active = True
                for subType in universe.stream.subscriptions:  # this resends what you have already sent (if the stream crashes).
                    if len(universe.stream.subscriptions[subType]["keys"]) and len(
                            universe.stream.subscriptions[subType]["fields"]):
                        await ws.send(json.dumps({"requests": [utilities.basicRequest(service=subType, command="SUBS",
                                                                                      parameters={
                                                                                          "keys": utilities.listToString(
                                                                                              universe.stream.subscriptions.get(
                                                                                                  subType).get("keys")),
                                                                                          "fields": utilities.listToString(
                                                                                              universe.stream.subscriptions.get(
                                                                                                  subType).get(
                                                                                                  "fields"))})]}))
                        received = await ws.recv()
                        universe.stream.terminal.print(received)
                while True:
                    received = await ws.recv()
                    # universe.stream.terminal.print(received)
                    _streamResponseHandler(received)

        except websockets.exceptions.ConnectionClosedOK as info:
            universe.stream.active = False
            universe.terminal.info(f"{info}")
            universe.terminal.info("Stream has closed.")
            break
        except Exception as error:
            universe.stream.active = False
            universe.terminal.error(f"{error}")
            if (datetime.now() - startTimeStamp).seconds < 70:
                universe.terminal.error("Stream not alive for more than 1 minute, exiting...")
                break
            else:
                universe.stream.terminal.print("[WARNING]: Connection lost to server, reconnecting...")


async def _send(toSend):
    global ws
    await ws.send(toSend)


def _startManual(qos=universe.preferences.streamingQOSLevel):
    universe.stream.terminal = WindowTerminal.create_window()
    universe.stream.terminal.open()

    def _manStart():
        asyncio.run(_clientStart(qos=qos))

    universe.threads.append(threading.Thread(target=_manStart, daemon=True))


def _startAutomatic(qos=universe.preferences.streamingQOSLevel):
    universe.stream.terminal = WindowTerminal.create_window()
    universe.stream.terminal.open()

    start = time(9, 30, 0)
    end = time(16, 0, 0)
    if universe.preferences.streamPreHours:
        start = time(8, 0, 0)
    if universe.preferences.streamAfterHours:
        end = time(20, 0, 0)

    def _inHours():
        return (start <= datetime.now().time() <= end) and (0 <= datetime.now().weekday() <=4)

    def _autoStart():
        while True:
            if _inHours() and not universe.stream.active:
                asyncio.run(_clientStart(qos=qos))
            sleep(60)

    def _autoStop():
        while True:
            if not _inHours() and universe.stream.active:
                universe.terminal.info("Stopping Stream.")
                send(admin.logout())
                universe.stream.active = False
            sleep(60)

    universe.threads.append(threading.Thread(target=_autoStart, daemon=True))
    universe.threads.append(threading.Thread(target=_autoStop, daemon=True))
    if not start <= datetime.now().time() <= end:
        universe.terminal.info("Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    if type(listOfRequests) != list: listOfRequests = [listOfRequests]
    if universe.stream.active:
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
                    universe.stream.terminal.print(
                        f"[Heartbeat]: {utilities.epochMSToDate(parentDict['notify'][0]['heartbeat'])}")
                case "response":
                    for resp in parentDict.get('response'):
                        universe.stream.terminal.print(f"[Response]: {resp}")
                case "snapshot":
                    for snap in parentDict.get('snapshot'):
                        universe.stream.terminal.print(f"[Snapshot]: {snap}")
                case "data":
                    for data in parentDict.get("data"):
                        if data.get('service').upper() in universe.stream.fieldAliases:
                            service = data.get("service")
                            timestamp = data.get("timestamp")
                            for symbolData in data.get("content"):
                                tempSnapshot = database.Snapshot(service, symbolData.get("key"), timestamp, symbolData)
                                if universe.preferences.usingDatabase: database.DBAddSnapshot(tempSnapshot)  # add to database
                                if universe.preferences.usingDataframes: database.DFAddSnapshot(tempSnapshot)  # add to capacitors
                                universe.stream.terminal.print(f"[Data]: {tempSnapshot.toPrettyString()}")  # to stream output
                case _:
                    universe.stream.terminal.print(f"[Unknown Response]: {streamOut}")
    except Exception as e:
        universe.stream.terminal.print(f"[ERROR]: There was an error in decoding the stream response: {streamOut}")
        universe.stream.terminal.print(f"[ERROR]: The error was: {e}")
        # universe.terminal.error(f"There was an error in decoding the stream response: {e}")
