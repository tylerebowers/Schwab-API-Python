"""
This file contains functions to stream data
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import asyncio
import threading
import websockets
from time import sleep
from . import color_print
import websockets.exceptions
from datetime import datetime, time


class Stream:

    def __init__(self, client):
        self._websocket = None
        self._streamer_info = None
        self._start_timestamp = None
        self._request_id = 0  # a counter for the request id
        self._queue = []  # a queue of requests to be sent
        self.active = False
        self._client = client  # so we can get streamer info

    async def _start_streamer(self, receiver_func="default"):
        # get streamer info
        response = self._client.preferences()
        if response.ok:
            self._streamer_info = response.json().get('streamerInfo', None)[0]
        else:
            color_print.error("Could not get streamerInfo")

        # specify receiver (what do we do with received data)
        if receiver_func == "default":
            receiver_func = print

        # start the stream
        while True:
            try:
                self._start_timestamp = datetime.now()
                color_print.info("Connecting to streaming server -> ", end="")
                async with websockets.connect(self._streamer_info.get('streamerSocketUrl'), ping_interval=None) as self._websocket:
                    print("Connected.")
                    login_payload = self.basic_request(service="ADMIN", command="LOGIN", parameters={"Authorization": self._client.access_token, "SchwabClientChannel": self._streamer_info.get("schwabClientChannel"), "SchwabClientFunctionId": self._streamer_info.get("schwabClientFunctionId")})
                    await self._websocket.send(json.dumps(login_payload))
                    receiver_func(await self._websocket.recv())
                    self.active = True
                    # send queued requests
                    while self._queue:
                        await self._websocket.send(json.dumps({"requests": self._queue.pop(0)}))
                        receiver_func(await self._websocket.recv())
                    # TODO: send logout request atexit (when the program closes)
                    # TODO: resend requests if the stream crashes
                    while True:
                        receiver_func(await self._websocket.recv())
            except Exception as e:
                self.active = False
                if e is websockets.exceptions.ConnectionClosedOK or str(e) == "received 1000 (OK); then sent 1000 (OK)":
                    color_print.info("Stream has closed.")
                    break
                elif (datetime.now() - self._start_timestamp).seconds < 60:
                    color_print.error(f"{e}")
                    color_print.error("Stream not alive for more than 1 minute, exiting...")
                    break
                else:
                    color_print.error(f"{e}")
                    color_print.warning("Connection lost to server, reconnecting...")

    def start(self, receiver="default"):
        def _start_async():
            asyncio.run(self._start_streamer(receiver))

        threading.Thread(target=_start_async, daemon=False).start()
        sleep(1) # if the thread does not start in time then the main program may close before the streamer starts

    def start_automatic(self, after_hours=False, pre_hours=False):
        start = time(9, 29, 0)  # market opens at 9:30
        end = time(16, 0, 0)  # market closes at 4:00
        if pre_hours:
            start = time(7, 59, 0)
        if after_hours:
            end = time(20, 0, 0)

        def checker():

            while True:
                in_hours = (start <= datetime.now().time() <= end) and (0 <= datetime.now().weekday() <= 4)
                if in_hours and not self.active:
                    self.start()
                elif not in_hours and self.active:
                    color_print.info("Stopping Stream.")
                    self.stop()
                sleep(60)

        threading.Thread(target=checker).start()

        if not start <= datetime.now().time() <= end:
            color_print.info("Stream was started outside of active hours and will launch when in hours.")


    def send(self, requests):
        async def _send(to_send):
            await self._websocket.send(to_send)
        if type(requests) is not list:
            requests = [requests]
        if self.active:
            to_send = json.dumps({"requests": requests})
            asyncio.run(_send(to_send))
        else:
            color_print.warning("Stream is not active, request queued.")
            self._queue.append(requests)

    # TODO: Fix this (wont properly close)
    def stop(self):
        self._request_id += 1
        self.send(self.basic_request(service="ADMIN", command="LOGOUT"))
        self.active = False

    def basic_request(self, service, command, parameters=None):
        if self._streamer_info is None:
            response = self._client.preferences()
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
            color_print.error("Could not get streamerInfo")
            return None

    @staticmethod
    def _list_to_string(ls):
        if type(ls) is str: return ls
        elif type(ls) is list: return ",".join(map(str, ls))

    def level_one_equities(self, keys, fields, command="ADD"):
        return self.basic_request("LEVELONE_EQUITIES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_options(self, keys, fields, command="ADD"):
        return self.basic_request("LEVELONE_OPTIONS", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures(self, keys, fields, command="ADD"):
        return self.basic_request("LEVELONE_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures_options(self, keys, fields, command="ADD"):
        return self.basic_request("LEVELONE_FUTURES_OPTIONS", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_forex(self, keys, fields, command="ADD"):
        return self.basic_request("LEVELONE_FOREX", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def nyse_book(self, keys, fields, command="ADD"):
        return self.basic_request("NYSE_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def nasdaq_book(self, keys, fields, command="ADD"):
        return self.basic_request("NASDAQ_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def options_book(self, keys, fields, command="ADD"):
        return self.basic_request("OPTIONS_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def chart_equity(self, keys, fields, command="ADD"):
        return self.basic_request("CHART_EQUITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def chart_futures(self, keys, fields, command="ADD"):
        return self.basic_request("CHART_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def screener_equity(self, keys, fields, command="ADD"):
        return self.basic_request("SCREENER_EQUITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def screener_option(self, keys, fields, command="ADD"):
        return self.basic_request("SCREENER_OPTION", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def account_activity(self, keys="Account Activity", fields="0,1,2,3", command="SUBS"): # can only use SUBS or UNSUBS
        return self.basic_request("ACCT_ACTIVITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})
