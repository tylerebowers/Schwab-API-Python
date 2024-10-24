"""
This file contains functions to stream data
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import atexit
import asyncio
import datetime
import logging
import threading
import websockets
from time import sleep
import websockets.exceptions

class Stream:

    def __init__(self, client):
        """
        Initialize the stream object to stream data from Schwab Streamer
        :param client: Client object
        :type client: Client
        """
        self._websocket = None                                  # the websocket
        self._streamer_info = None                              # streamer info from api call
        self._request_id = 0                                    # a counter for the request id
        self.active = False                                     # whether the stream is active
        self._thread = None                                     # the thread that runs the stream
        self._client = client                                   # so we can get streamer info
        self.subscriptions = {}                                 # a dictionary of subscriptions
        self._logger = logging.getLogger('Schwabdev.Stream')    # init the logger
        self.backoff_time = 2.0                                 # default backoff time (time to wait before retrying)

        # register atexit to stop the stream (if active)
        def stop_atexit():
            if self.active:
                self.stop()
        atexit.register(stop_atexit)


    async def _start_streamer(self, receiver_func=print, **kwargs):
        """
        Start the streamer
        :param receiver_func: function to call when data is received
        :type receiver_func: function
        """
        # get streamer info
        response = self._client.preferences()
        if response.ok:
            self._streamer_info = response.json().get('streamerInfo', None)[0]
        else:
            self._logger.error("Could not get streamerInfo")
            return

        # start the stream
        start_time = datetime.datetime.now(datetime.timezone.utc)
        while True:
            try:
                start_time = datetime.datetime.now(datetime.timezone.utc)
                self._logger.info("Connecting to streaming server...")
                async with websockets.connect(self._streamer_info.get('streamerSocketUrl'), ping_interval=20) as self._websocket:
                    self._logger.debug("Connected to streaming server.")
                    # send login payload
                    login_payload = self.basic_request(service="ADMIN",
                                                       command="LOGIN",
                                                       parameters={"Authorization": self._client.tokens.access_token,
                                                                   "SchwabClientChannel": self._streamer_info.get("schwabClientChannel"),
                                                                   "SchwabClientFunctionId": self._streamer_info.get("schwabClientFunctionId")})
                    await self._websocket.send(json.dumps(login_payload))
                    receiver_func(await self._websocket.recv(), **kwargs)
                    self.active = True

                    # send subscriptions
                    for service, subs in self.subscriptions.items():
                        reqs = []
                        for key, fields in subs.items():
                            reqs.append(self.basic_request(service=service,
                                                           command="ADD",
                                                           parameters={"keys": key,
                                                                       "fields": Stream._list_to_string(fields)}))
                        if reqs:
                            await self._websocket.send(json.dumps({"requests": reqs}))
                            receiver_func(await self._websocket.recv(), **kwargs)

                    # main listener loop
                    while True:
                        receiver_func(await self._websocket.recv(), **kwargs)

            except websockets.exceptions.ConnectionClosedOK as e: # "received 1000 (OK); then sent 1000 (OK)"
                self.active = False
                self._logger.info("Stream connection closed.")
                break
            except websockets.exceptions.ConnectionClosedError as e: # lost internet connection
                self.active = False
                self._logger.error(e)
                if (datetime.datetime.now(datetime.timezone.utc).timestamp() - start_time.timestamp()) <= 90:
                    self._logger.warning(f"Stream has crashed within 90 seconds, likely no subscriptions, invalid login, or lost connection (not restarting).")
                    break
                self._logger.error(f"Stream connection Error. Reconnecting in {self.backoff_time} seconds...")
                self._wait_for_backoff()
            except Exception as e:  # stream has quit unexpectedly, try to reconnect
                self.active = False
                self._logger.error(e)
                self._logger.warning(f"Stream connection lost to server, reconnecting...")
                self._wait_for_backoff()


    def _wait_for_backoff(self):
        """
        Wait for the backoff time
        """
        sleep(self.backoff_time)
        # exponential backoff and cap at 128s
        self.backoff_time = min(self.backoff_time * 2, 128)

    def start(self, receiver=print, daemon: bool = True, **kwargs):
        """
        Start the stream
        :param receiver: function to call when data is received
        :type receiver: function
        :param daemon: whether to run the thread in the background (as a daemon)
        :type daemon: bool
        """
        if not self.active:
            def _start_async():
                asyncio.run(self._start_streamer(receiver, **kwargs))

            self._thread = threading.Thread(target=_start_async, daemon=daemon)
            self._thread.start()
            # if the thread does not start in time then the main program may close before the streamer starts
        else:
            self._logger.warning("Stream already active.")

    def start_auto(self, receiver=print, start_time: datetime.datetime.time = datetime.time(13, 29, 0, tzinfo=datetime.timezone.utc),
                   stop_time: datetime.datetime.time = datetime.time(20, 0, 0, tzinfo=datetime.timezone.utc), on_days: list[int] = (0,1,2,3,4), daemon: bool = True, **kwargs):
        """
        Start the stream automatically at market open and close, will NOT erase subscriptions
        :param receiver: function to call when data is received
        :type receiver: function
        :param start_time: time to start the stream in UTC, must be later than datetime.time.min
        :type start_time: bool
        :param stop_time: time to stop the stream in UTC, must be earlier than datetime.time.max
        :type stop_time: bool
        :param on_days: day(s) to start the stream default: (0,1,2,3,4) = Mon-Fri, (0 = Monday, ..., 6 = Sunday)
        :type on_days: list(int) | set(int)
        :param daemon: whether to run the thread as a daemon
        :type daemon: bool
        """
        #start_time = datetime.time(13, 29, 0, tzinfo=datetime.timezone.utc)  # market opens at 9:30 ET
        #stop_time = datetime.time(20, 0, 0, tzinfo=datetime.timezone.utc)  # market closes at 4:00 ET
        #pre_hours: start_time = datetime.time(10, 59, 0, tzinfo=datetime.timezone.utc)
        #after_hours: stop_time = datetime.time.max.replace(tzinfo=datetime.timezone.utc) # 23:59:59:999999
        start_time = start_time.replace(tzinfo=datetime.timezone.utc)
        stop_time = stop_time.replace(tzinfo=datetime.timezone.utc)
        def checker():

            while True:
                now = datetime.datetime.now(datetime.timezone.utc)
                in_hours = (start_time <= now.time().replace(tzinfo=datetime.timezone.utc) <= stop_time) and (now.weekday() in on_days)
                if in_hours and not self.active:
                    if len(self.subscriptions) == 0:
                        self._logger.warning("No subscriptions, starting stream anyways.")
                    self.start(receiver=receiver, daemon=daemon, **kwargs)
                elif not in_hours and self.active:
                    self._logger.info("Stopping Stream.")
                    self.stop(clear_subscriptions=False)
                sleep(30)

        threading.Thread(target=checker, daemon=daemon).start()

        if not start_time <= datetime.datetime.now(datetime.timezone.utc).time().replace(tzinfo=datetime.timezone.utc) <= stop_time:
            self._logger.info("Stream was started outside of active hours and will launch when in hours.")

    def _record_request(self, request: dict):
        """
        Record the request into self.subscriptions (for the event of crashes)
        :param request: request
        :type request: dict
        """
        def str_to_list(st):
            if type(st) is str: return st.split(",")
            elif type(st) is list: return st
        service = request.get("service", None)
        command = request.get("command", None)
        parameters = request.get("parameters", None)
        if parameters is not None:
            keys = str_to_list(parameters.get("keys", []))
            fields = str_to_list(parameters.get("fields", []))
            # add service to subscriptions if not already there
            if service not in self.subscriptions:
                self.subscriptions[service] = {}
            if command == "ADD":
                for key in keys:
                    if key not in self.subscriptions[service]:
                        self.subscriptions[service][key] = fields
                    else:
                        self.subscriptions[service][key] = list(set(fields) | set(self.subscriptions[service][key]))
            elif command == "SUBS":
                self.subscriptions[service] = {}
                for key in keys:
                    self.subscriptions[service][key] = fields
            elif command == "UNSUBS":
                for key in keys:
                    if key in self.subscriptions[service]:
                        self.subscriptions[service].pop(key)
            elif command == "VIEW":  # not sure if this is even working on Schwab's end :/
                for key in self.subscriptions[service].keys():
                    self.subscriptions[service][key] = fields



    def send(self, requests: list | dict):
        """
        Send a request to the stream
        :param requests: list of requests or a single request
        :type requests: list | dict
        """
        # send the request using the async function
        asyncio.run(self.send_async(requests))


    async def send_async(self, requests: list | dict):
        """
        Send an async (must be awaited) request to the stream (functionally equivalent to send)
        :param requests: list of requests or a single request
        :type requests: list | dict
        """

        # make sure requests is a list
        if type(requests) is not list:
            requests = [requests]

        # add requests to list of subscriptions (acts as a queue before stream started)
        for request in requests:
            self._record_request(request)

        # send the request if the stream is active, queue otherwise
        if self.active:
            to_send = json.dumps({"requests": requests})
            await self._websocket.send(to_send)
        else:
            self._logger.info("Stream is not active, request queued.")


    def stop(self, clear_subscriptions: bool = True):
        """
        Stop the stream
        :param clear_subscriptions: clear records
        :type clear_subscriptions: bool
        """
        if clear_subscriptions:
            self.subscriptions = {}
        self.send(self.basic_request(service="ADMIN", command="LOGOUT"))
        self.active = False

    def basic_request(self, service: str, command: str, parameters: dict = None):
        """
        Create a basic request (all requests follow this format)
        :param service: service to use
        :type service: str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW"|"LOGIN"|"LOGOUT")
        :type command: str
        :param parameters: parameters to use
        :type parameters: dict
        :return: stream request
        :rtype: dict
        """
        if self._streamer_info is None:
            response = self._client.preferences()
            if response.ok:
                self._streamer_info = response.json().get('streamerInfo', None)[0]
            else:
                self._logger.error("Could not use/get streamerInfo")
                return {}

        # remove None parameters
        if parameters is not None:
            for key in parameters.keys():
                if parameters[key] is None: del parameters[key]

        self._request_id += 1
        request = {"service": service.upper(),
                   "command": command.upper(),
                   "requestid": self._request_id,
                   "SchwabClientCustomerId": self._streamer_info.get("schwabClientCustomerId"),
                   "SchwabClientCorrelId": self._streamer_info.get("schwabClientCorrelId")}
        if parameters is not None and len(parameters) > 0: request["parameters"] = parameters
        return request

    @staticmethod
    def _list_to_string(ls: list | str | tuple | set):
        """
        Convert a list to a string (e.g. [1, "B", 3] -> "1,B,3"), or passthrough if already a string
        :param ls: list to convert
        :type ls: list | str | tuple | set
        :return: converted string
        :rtype: str
        """
        if isinstance(ls, str): return ls
        elif hasattr(ls, '__iter__'): return ",".join(map(str, ls)) # yes, this is true for string too but those are caught first
        else: return str(ls)

    def level_one_equities(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Level one equities
        :param keys: list of keys to use (e.g. ["AMD", "INTC"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("LEVELONE_EQUITIES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_options(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Level one options, key format: [Underlying Symbol (6 characters including spaces) | Expiration (6 characters) | Call/Put (1 character) | Strike Price (5+3=8 characters)]
        :param keys: list of keys to use (e.g. ["GOOG  240809C00095000", "AAPL  240517P00190000"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("LEVELONE_OPTIONS", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Level one futures, key format: '/' + 'root symbol' + 'month code' + 'year code'; month code is 1 character: (F: Jan, G: Feb, H: Mar, J: Apr, K: May, M: Jun, N: Jul, Q: Aug, U: Sep, V: Oct, X: Nov, Z: Dec), year code is 2 characters (i.e. 2024 = 24)
        :param keys: list of keys to use (e.g. ["/ESF24", "/GCG24"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("LEVELONE_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_futures_options(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Level one futures options, key format: '.' + '/' + 'root symbol' + 'month code' + 'year code' + 'Call/Put code' + 'Strike Price'
        :param keys: list of keys to use (e.g. ["./OZCZ23C565"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("LEVELONE_FUTURES_OPTIONS", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def level_one_forex(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Level one forex, key format: 'from currency' + '/' + 'to currency'
        :param keys: list of keys to use (e.g. ["EUR/USD", "JPY/USD"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("LEVELONE_FOREX", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def nyse_book(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        NYSE book orders
        :param keys: list of keys to use (e.g. ["NIO", "F"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("NYSE_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def nasdaq_book(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        NASDAQ book orders
        :param keys: list of keys to use (e.g. ["AMD", "CRWD"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("NASDAQ_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def options_book(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Options book orders
        :param keys: list of keys to use (e.g. ["GOOG  240809C00095000", "AAPL  240517P00190000"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("OPTIONS_BOOK", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def chart_equity(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Chart equity
        :param keys: list of keys to use (e.g. ["GOOG", "AAPL"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("CHART_EQUITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def chart_futures(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Chart futures, key format: '/' + 'root symbol' + 'month code' + 'year code'; month code is 1 character: (F: Jan, G: Feb, H: Mar, J: Apr, K: May, M: Jun, N: Jul, Q: Aug, U: Sep, V: Oct, X: Nov, Z: Dec), year code is 2 characters (i.e. 2024 = 24)
        :param keys: list of keys to use (e.g. ["/ESF24", "/GCG24"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("CHART_FUTURES", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def screener_equity(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Screener equity, key format: (PREFIX)_(SORTFIELD)_(FREQUENCY); Prefix: ($COMPX, $DJI, $SPX.X, INDEX_AL, NYSE, NASDAQ, OTCBB, EQUITY_ALL); Sortfield: (VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME), Frequency: (0 (all day), 1, 5, 10, 30 60)
        :param keys: list of keys to use (e.g. ["$DJI_PERCENT_CHANGE_UP_60", "NASDAQ_VOLUME_30"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("SCREENER_EQUITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def screener_options(self, keys: str | list, fields: str | list, command: str = "ADD") -> dict:
        """
        Screener option key format: (PREFIX)_(SORTFIELD)_(FREQUENCY); Prefix: (OPTION_PUT, OPTION_CALL, OPTION_ALL); Sortfield: (VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME), Frequency: (0 (all day), 1, 5, 10, 30 60)
        :param keys: list of keys to use (e.g. ["OPTION_PUT_PERCENT_CHANGE_UP_60", "OPTION_CALL_TRADES_30"])
        :type keys: list | str
        :param fields: list of fields to use
        :type fields: list | str
        :param command: command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("SCREENER_OPTION", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})

    def account_activity(self, keys="Account Activity", fields="0,1,2,3", command: str = "SUBS") -> dict:
        """
        Account activity
        :param keys: list of keys to use (e.g. ["Account Activity"])
        :type keys: list | str
        :param fields: list of fields to use (e.g. ["0,1,2,3"])
        :type fields: list | str
        :param command: command to use ("SUBS"|"UNSUBS")
        :type command: str
        :return: stream request
        :rtype: dict
        """
        return self.basic_request("ACCT_ACTIVITY", command, parameters={"keys": Stream._list_to_string(keys), "fields": Stream._list_to_string(fields)})
