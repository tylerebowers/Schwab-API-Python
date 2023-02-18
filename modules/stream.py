"""
This file stores variables to be used between python files and functions
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Wrapper
"""

import json
import time
import asyncio
import pycron
import threading
import websockets
import websockets.exceptions
from datetime import datetime
from streaming import admin, utilities
from apis import userInfoAndPreferences
from window_terminal import WindowTerminal
from modules import universe, database

global ws


def _setupStream():
    # if universe.stream.subscriptionKey is None or universe.stream.connectionInfo == {} or universe.stream.userPrincipals == {}:
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
            print(f"[INFO]: {info}")
            print("[INFO]: Stream has closed.")
            break
        except Exception as error:
            universe.stream.active = False
            print(f"[ERROR]: {error}")
            if (datetime.now() - startTimeStamp).seconds < 70:
                print("[ERROR]: Stream not alive for more than 1 minute, exiting...")
                break
            else:
                universe.stream.terminal.print("[WARNING]: Connection lost to server, reconnecting...")


async def _send(toSend):
    global ws
    await ws.send(toSend)


def startManual(qos=universe.preferences.streamingQOSLevel):
    universe.stream.terminal = WindowTerminal.create_window()
    universe.stream.terminal.open()

    def _manStart():
        asyncio.run(_clientStart(qos=qos))

    universe.threads.append(threading.Thread(target=_manStart, daemon=True))


def startAutomatic(qos=universe.preferences.streamingQOSLevel):
    universe.stream.terminal = WindowTerminal.create_window()
    universe.stream.terminal.open()

    def _autoStart():
        while True:
            if pycron.is_now('* 9-19 * * mon-fri') and not universe.stream.active:
                asyncio.run(_clientStart(qos=qos))
            elif (pycron.is_now('* 0-8,20-24 * * *') or pycron.is_now('* * * * sat-sun')) and universe.stream.active:
                send(admin.logout())
                universe.stream.active = False
            time.sleep(60)

    universe.threads.append(threading.Thread(target=_autoStart, daemon=True))
    if pycron.is_now('* 0-8,20-24 * * *') or pycron.is_now('* * * * sat-sun'):
        print("[INFO]: Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    if type(listOfRequests) != list: listOfRequests = [listOfRequests]
    if universe.stream.active:
        toSend = json.dumps({"requests": listOfRequests})
        asyncio.run(_send(toSend))
    else:
        print("[WARNING]: Stream is not active, nothing sent.")


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
                                universe.stream.terminal.print(f"[Data]: {tempSnapshot.toStreamString()}")  # to stream output
                case _:
                    universe.stream.terminal.print(f"[Unknown Response]: {streamOut}")
    except Exception as e:
        universe.stream.terminal.print(f"[ERROR]: There was an error in decoding the stream response: {streamOut}")
        universe.stream.terminal.print(f"[ERROR]: The error was: {e}")
        # print(f"[ERROR]: There was an error in decoding the stream response: {e}")
