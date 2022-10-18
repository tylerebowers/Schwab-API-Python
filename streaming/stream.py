import asyncio
import json
import urllib
import websockets
import websockets.exceptions
from modules import globals
from datetime import datetime
from apis import userInfoAndPreferences
from window_terminal import WindowTerminal
from streaming import admin, utilities

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
    startTimeStamp = datetime.now()
    while True:
        try:
            startTimeStamp = datetime.now()
            async with websockets.connect(websocketUrl, ping_interval=None) as ws:
                streamOutput.print("INFO: Connecting to server...")
                await ws.send(admin.loginRequest(2))
                if globals.terminalOutput:
                    streamOutput.print(await ws.recv())
                while True:
                    received = await ws.recv()
                    if globals.terminalOutput:
                        streamOutput.print(received)
        except:
            # need to add something that resends all commands sent
            if (datetime.now() - startTimeStamp).seconds < 30:
                print("Stream not alive for more than 30 seconds, this would result in a forever loop, exiting...")
                quit()
            streamOutput.print("WARNING: Connection lost to server, reconnecting...")


async def clientSend(toSend):
    global ws
    await ws.send(toSend)


def start():
    asyncio.run(clientStart())


def send(toSend):
    asyncio.run(clientSend(toSend))
