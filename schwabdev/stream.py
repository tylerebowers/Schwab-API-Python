"""
This file contains functions to stream data
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import asyncio
import atexit
import datetime
import json
import logging
import threading
from time import sleep

import websockets
import websockets.exceptions
import zoneinfo


class Stream:
    def __init__(self, client):
        """
        Initialize the stream object to stream data from Schwab Streamer.

        Args:
            client (Client): Client object.
        """
        self._websocket = None  # the websocket
        self._streamer_info = None  # streamer info from api call
        self._request_id = 0  # a counter for the request id
        self.active = False  # whether the stream is active
        self._thread = None  # the thread that runs the stream
        self._client = client  # so we can get streamer info
        self.subscriptions = {}  # a dictionary of subscriptions
        self._logger = logging.getLogger('Schwabdev.Stream')  # init the logger
        self.backoff_time = 2.0  # default backoff time (time to wait before retrying)

        # register atexit to stop the stream (if active)
        def stop_atexit():
            if self.active:
                self.stop()

        atexit.register(stop_atexit)

    async def _start_streamer(self, receiver_func=print, **kwargs):
        """
        Start the streamer.

        Args:
            receiver_func (function): Function to call when data is received.
        """
        # get streamer info
        response = self._client.preferences()
        if response.ok:
            self._streamer_info = response.json().get('streamerInfo', None)[0]
        else:
            self._logger.error('Could not get streamerInfo')
            return

        # start the stream
        start_time = datetime.datetime.now(datetime.timezone.utc)
        while True:
            try:
                start_time = datetime.datetime.now(datetime.timezone.utc)
                self._logger.info('Connecting to streaming server...')
                async with websockets.connect(
                    self._streamer_info.get('streamerSocketUrl'), ping_interval=20
                ) as self._websocket:
                    self._logger.info('Connected to streaming server.')
                    # send login payload
                    login_payload = self.basic_request(
                        service='ADMIN',
                        command='LOGIN',
                        parameters={
                            'Authorization': self._client.tokens.access_token,
                            'SchwabClientChannel': self._streamer_info.get('schwabClientChannel'),
                            'SchwabClientFunctionId': self._streamer_info.get(
                                'schwabClientFunctionId'
                            ),
                        },
                    )
                    await self._websocket.send(json.dumps(login_payload))
                    receiver_func(await self._websocket.recv(), **kwargs)
                    self.active = True

                    # send subscriptions (that are queued or previously sent)
                    for service, subs in self.subscriptions.items():
                        grouped = {}  # group subscriptions by fields for more efficient requests
                        for key, fields in subs.items():
                            grouped.setdefault(self._list_to_string(fields), []).append(key)
                        reqs = []  # list of requests to send for this service
                        for fields, keys in grouped.items():
                            reqs.append(
                                self.basic_request(
                                    service=service,
                                    command='ADD',
                                    parameters={
                                        'keys': self._list_to_string(keys),
                                        'fields': fields,
                                    },
                                )
                            )
                        if reqs:
                            self._logger.debug(f'Sending subscriptions: {reqs}')
                            await self._websocket.send(json.dumps({'requests': reqs}))
                            receiver_func(await self._websocket.recv(), **kwargs)

                    # main listener loop
                    while True:
                        receiver_func(await self._websocket.recv(), **kwargs)

            except (
                websockets.exceptions.ConnectionClosedOK
            ):  # "received 1000 (OK); then sent 1000 (OK)"
                self.active = False
                self._logger.info('Stream connection closed.')
                break
            except websockets.exceptions.ConnectionClosedError as e:  # lost internet connection
                self.active = False
                self._logger.error(e)
                if (
                    datetime.datetime.now(datetime.timezone.utc).timestamp()
                    - start_time.timestamp()
                ) <= 90:
                    self._logger.warning(
                        'Stream has crashed within 90 seconds, likely no subscriptions, invalid login, or lost connection (not restarting).'
                    )
                    break
                self._logger.error(
                    f'Stream connection Error. Reconnecting in {self.backoff_time} seconds...'
                )
                self._wait_for_backoff()
            except Exception as e:  # stream has quit unexpectedly, try to reconnect
                self.active = False
                self._logger.error(e)
                self._logger.warning('Stream connection lost to server, reconnecting...')
                self._wait_for_backoff()

    def _wait_for_backoff(self):
        """
        Wait for the backoff time.
        """
        sleep(self.backoff_time)
        # exponential backoff and cap at 128s
        self.backoff_time = min(self.backoff_time * 2, 128)

    def start(self, receiver=print, daemon: bool = True, **kwargs):
        """
        Start the stream.

        Args:
            receiver (function): Function to call when data is received.
            daemon (bool): Whether to run the thread in the background (as a daemon).
        """
        if not self.active:

            def _start_async():
                asyncio.run(self._start_streamer(receiver, **kwargs))

            self._thread = threading.Thread(target=_start_async, daemon=daemon)
            self._thread.start()
            # if the thread does not start in time then the main program may close before the streamer starts
        else:
            self._logger.warning('Stream already active.')

    def start_auto(
        self,
        receiver=print,
        start_time: datetime.time = datetime.time(9, 29, 0),
        stop_time: datetime.time = datetime.time(16, 0, 0),
        on_days: list[int] = (0, 1, 2, 3, 4),
        now_timezone: zoneinfo.ZoneInfo = zoneinfo.ZoneInfo('America/New_York'),
        daemon: bool = True,
        **kwargs,
    ):
        """
        Start the stream automatically at market open and close, will NOT erase subscriptions.

        Args:
            receiver (function): Function to call when data is received.
            start_time (datetime.time): Time to start the stream, must be later than datetime.time.min, default 9:30 (for EST).
            stop_time (datetime.time): Time to stop the stream, must be earlier than datetime.time.max, default 4:00 (for EST).
            on_days (list[int]): Day(s) to start the stream default: (0,1,2,3,4) = Mon-Fri, (0 = Monday, ..., 6 = Sunday).
            now_timezone (zoneinfo.ZoneInfo): Timezone to use for now, default: ZoneInfo("America/New_York").
            daemon (bool): Whether to run the thread as a daemon.
        """

        def checker():
            while True:
                now = datetime.datetime.now(now_timezone)
                in_hours = (start_time <= now.time() <= stop_time) and (now.weekday() in on_days)
                if in_hours and not self.active:
                    if len(self.subscriptions) == 0:
                        self._logger.warning('No subscriptions, starting stream anyways.')
                    self.start(receiver=receiver, daemon=daemon, **kwargs)
                elif not in_hours and self.active:
                    self._logger.info('Stopping Stream.')
                    self.stop(clear_subscriptions=False)
                sleep(30)

        threading.Thread(target=checker, daemon=daemon).start()

        if not start_time <= datetime.datetime.now(now_timezone).time() <= stop_time:
            self._logger.info(
                'Stream was started outside of active hours and will launch when in hours.'
            )

    def _record_request(self, request: dict):
        """
        Record the request into self.subscriptions (for the event of crashes).

        Args:
            request (dict): Request.
        """

        def str_to_list(st):
            if type(st) is str:
                return st.split(',')
            elif type(st) is list:
                return st

        service = request.get('service', None)
        command = request.get('command', None)
        parameters = request.get('parameters', None)
        if parameters is not None and service is not None:
            keys = str_to_list(parameters.get('keys', []))
            fields = str_to_list(parameters.get('fields', []))
            # add service to subscriptions if not already there
            if service not in self.subscriptions:
                self.subscriptions[service] = {}
            if command == 'ADD':
                for key in keys:
                    if key not in self.subscriptions[service]:
                        self.subscriptions[service][key] = fields
                    else:
                        self.subscriptions[service][key] = list(
                            set(fields) | set(self.subscriptions[service][key])
                        )
            elif command == 'SUBS':
                self.subscriptions[service] = {}
                for key in keys:
                    self.subscriptions[service][key] = fields
            elif command == 'UNSUBS':
                for key in keys:
                    if key in self.subscriptions[service]:
                        self.subscriptions[service].pop(key)
            elif command == 'VIEW':  # not sure if this is even working on Schwab's end :/
                for key in self.subscriptions[service].keys():
                    self.subscriptions[service][key] = fields

    def send(self, requests: list | dict):
        """
        Send a request to the stream.

        Args:
            requests (list | dict): List of requests or a single request.
        """
        # send the request using the async function
        asyncio.run(self.send_async(requests))

    async def send_async(self, requests: list | dict):
        """
        Send an async (must be awaited) request to the stream (functionally equivalent to send).

        Args:
            requests (list | dict): List of requests or a single request.
        """

        # make sure requests is a list
        if type(requests) is not list:
            requests = [requests]

        # add requests to list of subscriptions (acts as a queue before stream started)
        for request in requests:
            self._record_request(request)

        # send the request if the stream is active, queue otherwise
        if self.active:
            to_send = json.dumps({'requests': requests})
            await self._websocket.send(to_send)
        else:
            self._logger.info('Stream is not active, request queued.')

    def stop(self, clear_subscriptions: bool = True):
        """
        Stop the stream.

        Args:
            clear_subscriptions (bool): Clear records.
        """
        if clear_subscriptions:
            self.subscriptions = {}
        self.send(self.basic_request(service='ADMIN', command='LOGOUT'))
        self.active = False

    def basic_request(self, service: str, command: str, parameters: dict = None):
        """
        Create a basic request (all requests follow this format).

        Args:
            service (str): Service to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW"|"LOGIN"|"LOGOUT").
            parameters (dict): Parameters to use.

        Returns:
            dict: Stream request.
        """
        if self._streamer_info is None:
            response = self._client.preferences()
            if response.ok:
                self._streamer_info = response.json().get('streamerInfo', None)[0]
            else:
                self._logger.error('Could not use/get streamerInfo')
                return {}

        # remove None parameters
        if parameters is not None:
            for key in parameters.keys():
                if parameters[key] is None:
                    del parameters[key]

        self._request_id += 1
        request = {
            'service': service.upper(),
            'command': command.upper(),
            'requestid': self._request_id,
            'SchwabClientCustomerId': self._streamer_info.get('schwabClientCustomerId'),
            'SchwabClientCorrelId': self._streamer_info.get('schwabClientCorrelId'),
        }
        if parameters is not None and len(parameters) > 0:
            request['parameters'] = parameters
        return request

    @staticmethod
    def _list_to_string(ls: list | str | tuple | set):
        """
        Convert a list to a string (e.g. [1, "B", 3] -> "1,B,3"), or passthrough if already a string.

        Args:
            ls (list | str | tuple | set): List to convert.

        Returns:
            str: Converted string.
        """
        if isinstance(ls, str):
            return ls
        elif hasattr(ls, '__iter__'):
            return ','.join(
                map(str, ls)
            )  # yes, this is true for string too but those are caught first
        else:
            return str(ls)

    def level_one_equities(
        self, keys: str | list, fields: str | list, command: str = 'ADD'
    ) -> dict:
        """
        Level one equities.

        Args:
            keys (list | str): List of keys to use (e.g. ["AMD", "INTC"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'LEVELONE_EQUITIES',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def level_one_options(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Level one options.

        Args:
            keys (list | str): List of keys to use (e.g. ["GOOG  240809C00095000", "AAPL  240517P00190000"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'LEVELONE_OPTIONS',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def level_one_futures(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Level one futures.

        Args:
            keys (list | str): List of keys to use (e.g. ["/ESF24", "/GCG24"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'LEVELONE_FUTURES',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def level_one_futures_options(
        self, keys: str | list, fields: str | list, command: str = 'ADD'
    ) -> dict:
        """
        Level one futures options.

        Args:
            keys (list | str): List of keys to use (e.g. ["./OZCZ23C565"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'LEVELONE_FUTURES_OPTIONS',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def level_one_forex(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Level one forex.

        Args:
            keys (list | str): List of keys to use (e.g. ["EUR/USD", "JPY/USD"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'LEVELONE_FOREX',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def nyse_book(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        NYSE book orders.

        Args:
            keys (list | str): List of keys to use (e.g. ["NIO", "F"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'NYSE_BOOK',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def nasdaq_book(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        NASDAQ book orders.

        Args:
            keys (list | str): List of keys to use (e.g. ["AMD", "CRWD"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'NASDAQ_BOOK',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def options_book(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Options book orders.

        Args:
            keys (list | str): List of keys to use (e.g. ["GOOG  240809C00095000", "AAPL  240517P00190000"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'OPTIONS_BOOK',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def chart_equity(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Chart equity.

        Args:
            keys (list | str): List of keys to use (e.g. ["GOOG", "AAPL"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'CHART_EQUITY',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def chart_futures(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Chart futures.

        Args:
            keys (list | str): List of keys to use (e.g. ["/ESF24", "/GCG24"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'CHART_FUTURES',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def screener_equity(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Screener equity.

        Args:
            keys (list | str): List of keys to use (e.g. ["$DJI_PERCENT_CHANGE_UP_60", "NASDAQ_VOLUME_30"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'SCREENER_EQUITY',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def screener_options(self, keys: str | list, fields: str | list, command: str = 'ADD') -> dict:
        """
        Screener options.

        Args:
            keys (list | str): List of keys to use (e.g. ["OPTION_PUT_PERCENT_CHANGE_UP_60", "OPTION_CALL_TRADES_30"]).
            fields (list | str): List of fields to use.
            command (str): Command to use ("SUBS"|"ADD"|"UNSUBS"|"VIEW").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'SCREENER_OPTION',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )

    def account_activity(
        self, keys='Account Activity', fields='0,1,2,3', command: str = 'SUBS'
    ) -> dict:
        """
        Account activity.

        Args:
            keys (list | str): List of keys to use (e.g. ["Account Activity"]).
            fields (list | str): List of fields to use (e.g. ["0,1,2,3"]).
            command (str): Command to use ("SUBS"|"UNSUBS").

        Returns:
            dict: Stream request.
        """
        return self.basic_request(
            'ACCT_ACTIVITY',
            command,
            parameters={
                'keys': Stream._list_to_string(keys),
                'fields': Stream._list_to_string(fields),
            },
        )
