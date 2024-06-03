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
from schwabdev import terminal


class Stream:

    def __init__(self, client):
        self._websocket = None
        self._streamer_info = None
        self._start_timestamp = None
        self._terminal = None
        self._request_id = 0  # a counter for the request id
        self._queue = []  # a queue of requests to be sent
        self.active = False
        self.client = client  # so we can get streamer info

    async def _start_streamer(self, receiver_func="default"):
        # get streamer info
        response = self.client.preferences()
        if response.ok:
            self._streamer_info = response.json().get('streamerInfo', None)[0]
        else:
            terminal.color_print.error("Could not get streamerInfo")

        # specify receiver (what do we do with received data)
        if receiver_func == "default":
            if self._terminal is None:
                self._terminal = terminal.multiTerminal(title="Stream output")

            def default_receiver(data):
                self._terminal.print(data)
            receiver_func = default_receiver

        # start the stream
        while True:
            try:
                self._start_timestamp = datetime.now()
                terminal.color_print.info("Connecting to streaming server -> ", end="")
                async with websockets.connect(self._streamer_info.get('streamerSocketUrl'), ping_interval=None) as self._websocket:
                    print("Connected.")
                    login_payload = self.basic_request(service="ADMIN", command="LOGIN", parameters={"Authorization": self.client.access_token, "SchwabClientChannel": self._streamer_info.get("schwabClientChannel"), "SchwabClientFunctionId": self._streamer_info.get("schwabClientFunctionId")})
                    await self._websocket.send(json.dumps(login_payload))
                    receiver_func(await self._websocket.recv())
                    self.active = True
                    # send queued requests
                    while self._queue:
                        await self._websocket.send(json.dumps({"requests": self._queue.pop(0)}))
                        receiver_func(await self._websocket.recv())
                    # TODO: resend requests if the stream crashes
                    while True:
                        receiver_func(await self._websocket.recv())
            except Exception as e:
                self.active = False
                terminal.color_print.error(f"{e}")
                if e is websockets.exceptions.ConnectionClosedOK:
                    terminal.color_print.info("Stream has closed.")
                    break
                elif e is RuntimeError:
                    terminal.color_print.warning("Streaming window has closed.")
                    break
                elif (datetime.now() - self._start_timestamp).seconds < 60:
                    terminal.color_print.error("Stream not alive for more than 1 minute, exiting...")
                    break
                else:
                    terminal.color_print.warning("Connection lost to server, reconnecting...")

    def start(self, receiver="default"):
        def _start_async():
            asyncio.run(self._start_streamer(receiver))

        threading.Thread(target=_start_async).start()
        sleep(4)  # wait for thread/stream to start


    def start_automatic(self, after_hours=False, pre_hours=False):
        start = time(9, 30, 0)  # market opens at 9:30
        end = time(16, 0, 0)  # market closes at 4:00
        if pre_hours:
            start = time(8, 0, 0)
        if after_hours:
            end = time(20, 0, 0)

        def checker():

            while True:
                in_hours = (start <= datetime.now().time() <= end) and (0 <= datetime.now().weekday() <= 4)
                if in_hours and not self.active:
                    self.start()
                elif not in_hours and self.active:
                    terminal.color_print.info("Stopping Stream.")
                    self.stop()
                sleep(60)

        threading.Thread(target=checker).start()

        if not start <= datetime.now().time() <= end:
            terminal.color_print.info("Stream was started outside of active hours and will launch when in hours.")


    def send(self, requests):
        async def _send(toSend):
            await self._websocket.send(toSend)
        if type(requests) is not list:
            requests = [requests]
        if self.active:
            toSend = json.dumps({"requests": requests})
            asyncio.run(_send(toSend))
        else:
            terminal.color_print.warning("Stream is not active, request queued.")
            self._queue.append(requests)

    # TODO: Fix this (wont properly close)
    def stop(self):
        self._request_id += 1
        self.send(self.basic_request(service="ADMIN", command="LOGOUT"))
        self.active = False

    def basic_request(self, service, command, parameters=None):
        if self._streamer_info is None:
            response = self.client.preferences()
            if response.ok:
                self._streamer_info = response.json().get('streamerInfo', None)[0]

        if self._streamer_info is not None:
            request = {"service": service.upper(),
                       "command": command.upper(),
                       "requestid": self._request_id,
                       "SchwabClientCustomerId": self._streamer_info.get("schwabClientCustomerId"),
                       "SchwabClientCorrelId": self._streamer_info.get("schwabClientCorrelId")}
            if parameters is not None: request["parameters"] = parameters
            self._request_id += 1
            return request
        else:
            terminal.color_print.error("Could not get streamerInfo")
            return None

    @staticmethod
    def _list_to_string(ls):
        if type(ls) is str: return ls
        elif type(ls) is list: return ",".join(map(str, ls))


    # requests that can be sent to the stream
    def chart_equity(self, keys, fields, command="SUBS"):
        return self.basic_request("CHART_EQUITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def chart_futures(self, keys, fields, command="SUBS"):
        return self.basic_request("CHART_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_quote(self, keys, fields, command="SUBS"):  # Service not available or temporary down.
        return self.basic_request("QUOTE", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_option(self, keys, fields, command="SUBS"):
        return self.basic_request("OPTION", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures(self, keys, fields, command="SUBS"):
        return self.basic_request("LEVELONE_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_forex(self, keys, fields, command="SUBS"):
        return self.basic_request("LEVELONE_FOREX", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures_options(self, keys, fields, command="SUBS"):
        return self.basic_request("LEVELONE_FUTURES_OPTIONS", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})


    """
    
    class account:
        @staticmethod
        def activity(keys, fields, command="SUBS"):
            return Stream.request(command, "ACCT_ACTIVITY", keys, fields)
    
    
    class actives:
        @staticmethod
        def nasdaq(keys, fields, command="SUBS"):
            return Stream.request(command, "ACTIVES_NASDAQ", keys, fields)
    
        @staticmethod
        def nyse(keys, fields, command="SUBS"):
            return Stream.request(command, "ACTIVES_NYSE", keys, fields)
    
        @staticmethod
        def otcbb(keys, fields, command="SUBS"):
            return Stream.request(command, "ACTIVES_OTCBB", keys, fields)
    
        @staticmethod
        def options(keys, fields, command="SUBS"):
            return Stream.request(command, "ACTIVES_OPTIONS", keys, fields)
    
    
    
    class book:
        @staticmethod
        def forex(keys, fields, command="SUBS"):
            return Stream.request(command, "FOREX_BOOK", keys, fields)
    
        @staticmethod
        def futures(keys, fields, command="SUBS"):
            return Stream.request(command, "FUTURES_BOOK", keys, fields)
    
        @staticmethod
        def listed(keys, fields, command="SUBS"):
            return Stream.request(command, "LISTED_BOOK", keys, fields)
    
        @staticmethod
        def nasdaq(keys, fields, command="SUBS"):
            return Stream.request(command, "NASDAQ_BOOK", keys, fields)
    
        @staticmethod
        def options(keys, fields, command="SUBS"):
            return Stream.request(command, "OPTIONS_BOOK", keys, fields)
    
        @staticmethod
        def futures_options(keys, fields, command="SUBS"):
            return Stream.request(command, "FUTURES_OPTIONS_BOOK", keys, fields)
    
    
    class levelTwo:
        @staticmethod
        def _NA():
            print("Not Available")
    
    
    class news:
        @staticmethod
        def headline(keys, fields, command="SUBS"):
            return Stream.request(command, "NEWS_HEADLINE", keys, fields)
    
        @staticmethod
        def headlineList(keys, fields, command="SUBS"):
            return Stream.request(command, "NEWS_HEADLINELIST", keys, fields)
    
        @staticmethod
        def headlineStory(keys, fields, command="SUBS"):
            return Stream.request(command, "NEWS_STORY", keys, fields)
    
    
    class timeSale:
        @staticmethod
        def equity(keys, fields, command="SUBS"):
            return Stream.request(command, "TIMESALE_EQUITY", keys, fields)
    
        @staticmethod
        def forex(keys, fields, command="SUBS"):
            return Stream.request(command, "TIMESALE_FOREX", keys, fields)
    
        @staticmethod
        def futures(keys, fields, command="SUBS"):
            return Stream.request(command, "TIMESALE_FUTURES", keys, fields)
    
        @staticmethod
        def options(keys, fields, command="SUBS"):
            return Stream.request(command, "TIMESALE_OPTIONS", keys, fields)
            
    """

"""

def _streamResponseHandler(streamOut):
    try:
        parentDict = json.loads(streamOut)
        for key in parentDict.keys():
            match key:
                case "notify":
                    self._terminal.print(
                        f"[Heartbeat]: {Stream.epochMSToDate(parentDict['notify'][0]['heartbeat'])}")
                case "response":
                    for resp in parentDict.get('response'):
                        self._terminal.print(f"[Response]: {resp}")
                case "snapshot":
                    for snap in parentDict.get('snapshot'):
                        self._terminal.print(f"[Snapshot]: {snap}")
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
                                self._terminal.print(
                                    f"[Data]: {tempSnapshot.toPrettyString()}")  # to stream output
                case _:
                    self._terminal.print(f"[Unknown Response]: {streamOut}")
    except Exception as e:
        self._terminal.print(f"[ERROR]: There was an error in decoding the stream response: {streamOut}")
        self._terminal.print(f"[ERROR]: The error was: {e}")
"""