import json
import time
import asyncio
import pycron
import threading
import websockets
import websockets.exceptions
from datetime import datetime
from modules import globals, api
from streaming import admin, utilities
from apis import userInfoAndPreferences
from window_terminal import WindowTerminal

global ws


def _setupStream():
    #if globals.streamerSubscriptionKey is None or globals.streamerConnectionInfo == {} or globals.userPrincipals == {}:
    globals.streamerSubscriptionKey = userInfoAndPreferences.getStreamerSubscriptionKeys().get('keys')[0].get('key')
    globals.streamerConnectionInfo = userInfoAndPreferences.getUserPrincipals(fields="streamerConnectionInfo").get(
        'streamerInfo')
    globals.userPrincipals = userInfoAndPreferences.getUserPrincipals()


async def _clientStart(qos=2):
    global ws
    _setupStream()
    websocketUrl = "wss://" + globals.streamerConnectionInfo.get('streamerSocketUrl') + "/ws"
    startTimeStamp = datetime.now()
    while True:
        try:
            startTimeStamp = datetime.now()
            async with websockets.connect(websocketUrl, ping_interval=None) as ws:
                globals.streamTerminal.print("INFO: Connecting to server...")
                await ws.send(json.dumps({"requests": [admin.login(qos)]}))
                globals.streamTerminal.print(await ws.recv())
                globals.streamIsActive = True
                for subType in globals.streamSubscriptions:  # this resends what you have already sent (if the stream crashes).
                    subList = []
                    for key in globals.streamSubscriptions[subType]:
                        subList.append(utilities.basicRequest(service=subType, command="SUBS", parameters={"keys": key, "fields": utilities.listToString(globals.streamSubscriptions[subType][key])}))
                    if len(subList):
                        await ws.send(json.dumps({"requests": subList}))
                        received = await ws.recv()
                        globals.streamTerminal.print(received)
                while True:
                    received = await ws.recv()
                    globals.streamTerminal.print(received)
                    # eventually there will be a utils decoder here

        except websockets.exceptions.ConnectionClosedOK as info:
            globals.streamIsActive = False
            print("INFO: ", info)
            print("INFO: Stream has properly closed.")
            break
        except Exception as error:
            globals.streamIsActive = False
            print("ERROR: ", end="")
            print(error)
            if (datetime.now() - startTimeStamp).seconds < 30:
                print("ERROR: Stream not alive for more than 30 seconds, exiting...")
                break
            else:
                globals.streamTerminal.print("WARNING: Connection lost to server, reconnecting...")


async def _send(toSend):
    global ws
    await ws.send(toSend)


def startManual():
    globals.streamTerminal = WindowTerminal.create_window()
    globals.streamTerminal.open()
    def _manStart():
        asyncio.run(_clientStart())

    globals.threads.append(threading.Thread(target=_manStart, daemon=True))


def startAutomatic():
    globals.streamTerminal = WindowTerminal.create_window()
    globals.streamTerminal.open()
    def _autoStart():
        while True:
            if pycron.is_now('* 9-19 * * mon-fri') and not globals.streamIsActive:
                globals.streamIsActive = True
                asyncio.run(_clientStart())
            time.sleep(60)

    globals.threads.append(threading.Thread(target=_autoStart, daemon=True))

    def _autoStop():
        while True:
            if (pycron.is_now('* 0-8,20-24 * * *') or pycron.is_now('* * * * sat-sun')) and globals.streamIsActive:
                send(admin.logout())
                globals.streamIsActive = False
            time.sleep(60)

    globals.threads.append(threading.Thread(target=_autoStop, daemon=True))
    if pycron.is_now('* 0-8,20-24 * * *') or pycron.is_now('* * * * sat-sun'):
        print("INFO: Stream was started outside of active hours and will launch when in hours.")


def send(listOfRequests):
    if globals.streamIsActive:
        toSend = json.dumps({"requests": utilities.stringToList(listOfRequests)})
        asyncio.run(_send(toSend))
    else:
        print("WARNING: Stream is not active, nothing sent.")


def stop():
    send(admin.logout())
