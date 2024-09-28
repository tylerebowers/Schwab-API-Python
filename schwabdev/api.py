"""
This file contains functions access the Schwab api
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

import json
import time
import base64
import datetime
import requests
import threading
import webbrowser
import urllib.parse
from .stream import Stream


class Client:

    def __init__(self, app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", timeout=5, verbose=False, update_tokens_auto=True):
        """
        Initialize a client to access the Schwab API.
        :param app_key: app key credentials
        :type app_key: str
        :param app_secret: app secret credentials
        :type app_secret: str
        :param callback_url: url for callback
        :type callback_url: str
        :param tokens_file: path to tokens file
        :type tokens_file: str
        :param timeout: request timeout
        :type timeout: int
        :param verbose: print extra information
        :type verbose: bool
        :param show_linked: print linked accounts
        :type show_linked: bool
        """

        if app_key is None:
            raise Exception("app_key cannot be None.")
        elif app_secret is None:
            raise Exception("app_secret cannot be None.")
        elif callback_url is None:
            raise Exception("callback_url cannot be None.")
        elif tokens_file is None:
            raise Exception("tokens_file cannot be None.")
        elif len(app_key) != 32 or len(app_secret) != 16:
            raise Exception("App key or app secret invalid length.")
        elif callback_url[0:5] != "https":
            raise Exception("callback_url must be https.")
        elif callback_url[-1] == "/":
            raise Exception("callback_url cannot be path (ends with \"/\").")
        elif tokens_file[-1] == '/':
            raise Exception("Tokens file cannot be path.")
        elif timeout <= 0:
            raise Exception("Timeout must be greater than 0 and is recomended to be 5 seconds or more.")

        self.version = "2.2.6"
        self._app_key = app_key                   # app key credential
        self._app_secret = app_secret             # app secret credential
        self._callback_url = callback_url         # callback url to use
        self.access_token = None                  # access token from auth
        self.refresh_token = None                 # refresh token from auth
        self.id_token = None                      # id token from auth
        self._access_token_issued = None          # datetime of access token issue
        self._refresh_token_issued = None         # datetime of refresh token issue
        self._access_token_timeout = 1800         # in seconds (from schwab)
        self._refresh_token_timeout = 7*24*60*60  # in seconds (from schwab)
        self._tokens_file = tokens_file           # path to tokens file
        self.timeout = timeout                    # timeout to use in requests
        self.verbose = verbose                    # verbose mode
        self.stream = Stream(self)                # init the streaming object
        self.awaiting_input = False               # whether we are awaiting user input

        # Try to load tokens from the tokens file
        at_issued, rt_issued, token_dictionary = self._read_tokens_file()
        if None not in [at_issued, rt_issued, token_dictionary]:
            # show user when tokens were last updated and when they will expire
            self.access_token = token_dictionary.get("access_token")
            self.refresh_token = token_dictionary.get("refresh_token")
            self.id_token = token_dictionary.get("id_token")
            self._access_token_issued = at_issued
            self._refresh_token_issued = rt_issued
            if self.verbose:
                at_delta = self._access_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._access_token_issued).total_seconds()
                print(f"[Schwabdev] Access token expires in {'-' if at_delta < 0 else ''}{int(abs(at_delta) / 3600):02}H:{int((abs(at_delta) % 3600) / 60):02}M:{int((abs(at_delta) % 60)):02}S")
                rt_delta = self._refresh_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._refresh_token_issued).total_seconds()
                print(f"[Schwabdev] Refresh token expires in {'-' if rt_delta < 0 else ''}{int(abs(rt_delta) / 3600):02}H:{int((abs(rt_delta) % 3600) / 60):02}M:{int((abs(rt_delta) % 60)):02}S")
            # check if tokens need to be updated and update if needed
            self.update_tokens()
        else:
            # The tokens file doesn't exist, so create it.
            if self.verbose:
                print(f"[Schwabdev] Token file does not exist or invalid formatting, creating \"{str(tokens_file)}\"")
            open(self._tokens_file, 'w').close()
            # Tokens must be updated.
            self._update_refresh_token()

        # Spawns a thread to check the access token and update if necessary
        if update_tokens_auto:
            def checker():
                while True:
                    self.update_tokens()
                    time.sleep(30)
            threading.Thread(target=checker, daemon=True).start()
        elif self.verbose:
            print("[Schwabdev] Warning: Tokens will not be updated automatically.")

        if self.verbose:
            print("[Schwabdev] Client Initialization Complete")

    def update_tokens(self, force=False):
        """
        Checks if tokens need to be updated and updates if needed (only access token is automatically updated)
        :param force: force update of refresh token (also updates access token)
        :type force: bool
        """
        # refresh token notification
        rt_delta = self._refresh_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._refresh_token_issued).total_seconds()
        if rt_delta < 43200: # Start to ware the user if the refresh token will expire in less than 43200 = 12 hours
            print(f"[Schwabdev] The refresh token will expire soon! ({'-' if rt_delta < 0 else ''}{int(abs(rt_delta) / 3600):02}H:{int((abs(rt_delta) % 3600) / 60):02}M:{int((abs(rt_delta) % 60)):02}S remaining)")

        if (rt_delta < 3600) or force:  # check if we need to update refresh (and access) token
            print("[Schwabdev] The refresh token has expired!")
            self._update_refresh_token()
        elif (self._access_token_timeout - (datetime.datetime.now(datetime.timezone.utc) - self._access_token_issued).total_seconds()) < 61:  # check if we need to update access token
            if self.verbose: print("[Schwabdev] The access token has expired, updating automatically.")
            self._update_access_token()

    def update_tokens_auto(self):
        import warnings
        warnings.warn("update_tokens_auto() is deprecated and is now started by default when the client is created (if update_tokens_auto=True (default)).", DeprecationWarning, stacklevel=2)

    def _update_access_token(self):
        """
        "refresh" the access token using the refresh token
        """
        # get the token dictionary (we will need to rewrite the file)
        access_token_time_old, refresh_token_issued, token_dictionary_old = self._read_tokens_file()
        # get new tokens
        for i in range(3):
            response = self._post_oauth_token('refresh_token', token_dictionary_old.get("refresh_token"))
            if response.ok:
                # get and update to the new access token
                self._access_token_issued = datetime.datetime.now(datetime.timezone.utc)
                self._refresh_token_issued = refresh_token_issued
                new_td = response.json()
                self.access_token = new_td.get("access_token")
                self.refresh_token = new_td.get("refresh_token")
                self.id_token = new_td.get("id_token")
                self._write_tokens_file(self._access_token_issued, refresh_token_issued, new_td)
                if self.verbose: # show user that we have updated the access token
                    print(f"[Schwabdev] Access token updated: {self._access_token_issued}")
                break
            else:
                print(response.text)
                print(f"[Schwabdev] Could not get new access token ({i+1} of 3).")
                time.sleep(10)

    def _update_refresh_token(self):
        """
        Get new access and refresh tokens using authorization code.
        """
        self.awaiting_input = True # set flag since we are waiting for user input
        # get authorization code (requires user to authorize)
        #print("[Schwabdev] Please authorize this program to access your schwab account.")
        auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={self._app_key}&redirect_uri={self._callback_url}'
        print(f"[Schwabdev] Open to authenticate: {auth_url}")
        webbrowser.open(auth_url)
        response_url = input("After authorizing, paste the address bar url here: ")
        code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"  # session = responseURL[responseURL.index("session=")+8:]
        # get new access and refresh tokens
        response = self._post_oauth_token('authorization_code', code)
        if response.ok:
            # update token file and variables
            self._access_token_issued = self._refresh_token_issued = datetime.datetime.now(datetime.timezone.utc)
            new_td = response.json()
            self.access_token = new_td.get("access_token")
            self.refresh_token = new_td.get("refresh_token")
            self.awaiting_input = False  # reset flag since tokens have been updated
            self.id_token = new_td.get("id_token")
            self._write_tokens_file(self._access_token_issued, self._refresh_token_issued, new_td)
            if self.verbose: print("[Schwabdev] Refresh and Access tokens updated")
        else:
            print(response.text)
            print("[Schwabdev] Could not get new refresh and access tokens, check these:\n    1. App status is "
                  "\"Ready For Use\".\n    2. App key and app secret are valid.\n    3. You pasted the "
                  "whole url within 30 seconds. (it has a quick expiration)")

    def _post_oauth_token(self, grant_type: str, code: str):
        """
        Makes API calls for auth code and refresh tokens
        :param grant_type: 'authorization_code' or 'refresh_token'
        :type grant_type: str
        :param code: authorization code
        :type code: str
        :return: response
        :rtype: requests.Response
        """
        headers = {
            'Authorization': f'Basic {base64.b64encode(bytes(f"{self._app_key}:{self._app_secret}", "utf-8")).decode("utf-8")}',
            'Content-Type': 'application/x-www-form-urlencoded'}
        if grant_type == 'authorization_code':  # gets access and refresh tokens using authorization code
            data = {'grant_type': 'authorization_code', 'code': code,
                    'redirect_uri': self._callback_url}
        elif grant_type == 'refresh_token':  # refreshes the access token
            data = {'grant_type': 'refresh_token', 'refresh_token': code}
        else:
            raise Exception("Invalid grant type; options are 'authorization_code' or 'refresh_token'")
        return requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

    def _write_tokens_file(self, at_issued: datetime, rt_issued: datetime, token_dictionary: dict):
        """
        Writes token file
        :param at_issued: access token issued
        :type at_issued: datetime.pyi
        :param rt_issued: refresh token issued
        :type rt_issued: datetime.pyi
        :param token_dictionary: token dictionary
        :type token_dictionary: dict
        """
        try:
            with open(self._tokens_file, 'w') as f:
                toWrite = {"access_token_issued": at_issued.isoformat(), "refresh_token_issued": rt_issued.isoformat(),
                           "token_dictionary": token_dictionary}
                json.dump(toWrite, f, ensure_ascii=False, indent=4)
                f.flush()
        except Exception as e:
            print(e)


    def _read_tokens_file(self):
        """
        Reads token file
        :return: access token issued, refresh token issued, token dictionary
        :rtype: datetime.pyi, datetime.pyi, dict
        """
        try:
            with open(self._tokens_file, 'r') as f:
                d = json.load(f)
                return datetime.datetime.fromisoformat(d.get("access_token_issued")), datetime.datetime.fromisoformat(d.get("refresh_token_issued")), d.get("token_dictionary")
        except Exception as e:
            print(e)
            return None, None, None

    def _params_parser(self, params: dict):
        """
        Removes None (null) values
        :param params: params to remove None values from
        :type params: dict
        :return: params without None values
        :rtype: dict
        """
        for key in list(params.keys()):
            if params[key] is None: del params[key]
        return params

    def _time_convert(self, dt = None, form="8601"):
        """
        Convert time to the correct format, passthrough if a string, preserve None if None for params parser
        :param dt: datetime.pyi object to convert
        :type dt: datetime.pyi | str | None
        :param form: what to convert input to
        :type form: str
        :return: converted time or passthrough
        :rtype: str | None
        """
        if dt is None or isinstance(dt, str):
            return dt
        elif form == "8601":  # assume datetime object from here on
            return f'{dt.isoformat()[:-9]}Z'
        elif form == "epoch":
            return int(dt.timestamp())
        elif form == "epoch_ms":
            return int(dt.timestamp() * 1000)
        elif form == "YYYY-MM-DD":
            return dt.strftime("%Y-%m-%d")
        else:
            return dt

    def _format_list(self, l: list | str | None):
        """
        Convert python list to string or passthough if already a string i.e ["a", "b"] -> "a,b"
        :param l: list to convert
        :type l: list | str | None
        :return: converted string or passthrough
        :rtype: str | None
        """
        if l is None:
            return None
        elif type(l) is list:
            return ",".join(l)
        else:
            return l
        
    _base_api_url = "https://api.schwabapi.com"

    """
    Accounts and Trading Production
    """

    def account_linked(self) -> requests.Response:
        """
        Account numbers in plain text cannot be used outside of headers or request/response bodies. As the first step consumers must invoke this service to retrieve the list of plain text/encrypted value pairs, and use encrypted account values for all subsequent calls for any accountNumber request.
        :return: All linked account numbers and hashes
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/accountNumbers',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    def account_details_all(self, fields: str = None) -> requests.Response:
        """
        All the linked account information for the user logged in. The balances on these accounts are displayed by default however the positions on these accounts will be displayed based on the "positions" flag.
        :param fields: fields to return (options: "positions")
        :type fields: str | None
        :return: details for all linked accounts
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    def account_details(self, accountHash: str, fields: str = None) -> requests.Response:
        """
        Specific account information with balances and positions. The balance information on these accounts is displayed by default but Positions will be returned based on the "positions" flag.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param fields: fields to return
        :type fields: str | None
        :return: details for one linked account
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    def account_orders(self, accountHash: str, fromEnteredTime: datetime.datetime | str, toEnteredTime: datetime.datetime | str, maxResults: int = None, status: str = None) -> requests.Response:
        """
        All orders for a specific account. Orders retrieved can be filtered based on input parameters below. Maximum date range is 1 year.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param fromEnteredTime: from entered time
        :type fromEnteredTime: datetime.pyi | str
        :param toEnteredTime: to entered time
        :type toEnteredTime: datetime.pyi | str
        :param maxResults: maximum number of results
        :type maxResults: int| None
        :param status: status ("AWAITING_PARENT_ORDER"|"AWAITING_CONDITION"|"AWAITING_STOP_CONDITION"|"AWAITING_MANUAL_REVIEW"|"ACCEPTED"|"AWAITING_UR_OUT"|"PENDING_ACTIVATION"|"QUEUED"|"WORKING"|"REJECTED"|"PENDING_CANCEL"|"CANCELED"|"PENDING_REPLACE"|"REPLACED"|"FILLED"|"EXPIRED"|"NEW"|"AWAITING_RELEASE_TIME"|"PENDING_ACKNOWLEDGEMENT"|"PENDING_RECALL"|"UNKNOWN")
        :type status: str| None
        :return: orders for one linked account hash
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'maxResults': maxResults, 'fromEnteredTime': self._time_convert(fromEnteredTime, "8601"),
                                 'toEnteredTime': self._time_convert(toEnteredTime, "8601"), 'status': status}),
                            timeout=self.timeout)

    def order_place(self, accountHash: str, order: dict) -> requests.Response:
        """
        Place an order for a specific account.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param order: order dictionary, examples in Schwab docs
        :type order: dict
        :return: order number in response header (if immediately filled then order number not returned)
        :rtype: request.Response
        """
        return requests.post(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders',
                             headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}',
                                      "Content-Type": "application/json"},
                             json=order,
                             timeout=self.timeout)

    def order_details(self, accountHash: str, orderId: int | str) -> requests.Response:
        """
        Get a specific order by its ID, for a specific account
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: int | str
        :return: order details
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    def order_cancel(self, accountHash: str, orderId: int | str) -> requests.Response:
        """
        Cancel a specific order by its ID, for a specific account
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: str|int
        :return: response code
        :rtype: request.Response
        """
        return requests.delete(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                               headers={'Authorization': f'Bearer {self.access_token}'},
                               timeout=self.timeout)

    def order_replace(self, accountHash: str, orderId: int | str, order: dict) -> requests.Response:
        """
        Replace an existing order for an account. The existing order will be replaced by the new order. Once replaced, the old order will be canceled and a new order will be created.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: str|int
        :param order: order dictionary, examples in Schwab docs
        :type order: dict
        :return: response code
        :rtype: request.Response
        """
        return requests.put(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}',
                                     "Content-Type": "application/json"},
                            json=order,
                            timeout=self.timeout)

    def account_orders_all(self, fromEnteredTime: datetime.datetime | str, toEnteredTime: datetime.datetime | str, maxResults: int = None, status: str = None) -> requests.Response:
        """
        Get all orders for all accounts
        :param fromEnteredTime: start date
        :type fromEnteredTime: datetime.pyi | str
        :param toEnteredTime: end date
        :type toEnteredTime: datetime.pyi | str
        :param maxResults: maximum number of results (set to None for default 3000)
        :type maxResults: int | None
        :param status: status ("AWAITING_PARENT_ORDER"|"AWAITING_CONDITION"|"AWAITING_STOP_CONDITION"|"AWAITING_MANUAL_REVIEW"|"ACCEPTED"|"AWAITING_UR_OUT"|"PENDING_ACTIVATION"|"QUEUED"|"WORKING"|"REJECTED"|"PENDING_CANCEL"|"CANCELED"|"PENDING_REPLACE"|"REPLACED"|"FILLED"|"EXPIRED"|"NEW"|"AWAITING_RELEASE_TIME"|"PENDING_ACKNOWLEDGEMENT"|"PENDING_RECALL"|"UNKNOWN")
        :type status: str | None
        :return: all orders
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'maxResults': maxResults, 'fromEnteredTime': self._time_convert(fromEnteredTime, "8601"),
                                 'toEnteredTime': self._time_convert(toEnteredTime, "8601"), 'status': status}),
                            timeout=self.timeout)

    """
    def order_preview(self, accountHash, orderObject) -> requests.Response:
        #COMING SOON (waiting on Schwab)
        return requests.post(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/previewOrder',
                             headers={'Authorization': f'Bearer {self.access_token}',
                                      "Content-Type": "application.json"}, data=orderObject)
    """

    def transactions(self, accountHash: str, startDate: datetime.datetime | str, endDate: datetime.datetime | str, types: str, symbol: str = None) -> requests.Response:
        """
        All transactions for a specific account. Maximum number of transactions in response is 3000. Maximum date range is 1 year.
        :param accountHash: account hash number
        :type accountHash: str
        :param startDate: start date
        :type startDate: datetime.pyi | str
        :param endDate: end date
        :type endDate: datetime.pyi | str
        :param types: transaction type ("TRADE, RECEIVE_AND_DELIVER, DIVIDEND_OR_INTEREST, ACH_RECEIPT, ACH_DISBURSEMENT, CASH_RECEIPT, CASH_DISBURSEMENT, ELECTRONIC_FUND, WIRE_OUT, WIRE_IN, JOURNAL, MEMORANDUM, MARGIN_CALL, MONEY_MARKET, SMA_ADJUSTMENT")
        :type types: str
        :param symbol: symbol
        :return: list of transactions for a specific account
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/transactions',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'accountNumber': accountHash, 'startDate': self._time_convert(startDate, "8601"),
                                 'endDate': self._time_convert(endDate, "8601"), 'symbol': symbol, 'types': types}),
                            timeout=self.timeout)

    def transaction_details(self, accountHash: str, transactionId: str | int) -> requests.Response:
        """
        Get specific transaction information for a specific account
        :param accountHash: account hash number
        :type accountHash: str
        :param transactionId: transaction id
        :type transactionId: str|int
        :return: transaction details of transaction id using accountHash
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/transactions/{transactionId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params={'accountNumber': accountHash, 'transactionId': transactionId},
                            timeout=self.timeout)

    def preferences(self) -> requests.Response:
        """
        Get user preference information for the logged in user.
        :return: User Preferences and Streaming Info
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/userPreference',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    """
    Market Data
    """
    
    def quotes(self, symbols : list[str] | str, fields: str = None, indicative: bool = False) -> requests.Response:
        """
        Get quotes for a list of tickers
        :param symbols: list of symbols strings (e.g. "AMD,INTC" or ["AMD", "INTC"])
        :type symbols: [str] | str
        :param fields: string of fields to get ("all", "quote", "fundamental")
        :type fields: str | None
        :param indicative: whether to get indicative quotes (True/False)
        :type indicative: boolean | None
        :return: list of quotes
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'symbols': self._format_list(symbols), 'fields': fields, 'indicative': indicative}),
                            timeout=self.timeout)

    def quote(self, symbol_id: str, fields: str = None) -> requests.Response:
        """
        Get quote for a single symbol
        :param symbol_id: ticker symbol
        :type symbol_id: str (e.g. "AAPL", "/ES", "USD/EUR")
        :param fields: string of fields to get ("all", "quote", "fundamental")
        :type fields: str | None
        :return: quote for a single symbol
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/{urllib.parse.quote_plus(symbol_id)}/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    def option_chains(self, symbol: str, contractType: str = None, strikeCount: any = None, includeUnderlyingQuote: bool = None, strategy: str = None,
               interval: any = None, strike: any = None, range: str = None, fromDate: datetime.datetime | str = None, toDate: datetime.datetime | str = None, volatility: any = None, underlyingPrice: any = None,
               interestRate: any = None, daysToExpiration: any = None, expMonth: str = None, optionType: str = None, entitlement: str = None) -> requests.Response:
        """
        Get Option Chain including information on options contracts associated with each expiration for a ticker.
        :param symbol: ticker symbol
        :type symbol: str
        :param contractType: contract type ("CALL"|"PUT"|"ALL")
        :type contractType: str
        :param strikeCount: strike count
        :type strikeCount: int
        :param includeUnderlyingQuote: include underlying quote (True|False)
        :type includeUnderlyingQuote: boolean
        :param strategy: strategy ("SINGLE"|"ANALYTICAL"|"COVERED"|"VERTICAL"|"CALENDAR"|"STRANGLE"|"STRADDLE"|"BUTTERFLY"|"CONDOR"|"DIAGONAL"|"COLLAR"|"ROLL)
        :type strategy: str
        :param interval: Strike interval
        :type interval: str
        :param strike: Strike price
        :type strike: float
        :param range: range ("ITM"|"NTM"|"OTM"...)
        :type range: str
        :param fromDate: from date
        :type fromDate: datetime.pyi | str
        :param toDate: to date
        :type toDate: datetime.pyi | str
        :param volatility: volatility
        :type volatility: float
        :param underlyingPrice: underlying price
        :type underlyingPrice: float
        :param interestRate: interest rate
        :type interestRate: float
        :param daysToExpiration: days to expiration
        :type daysToExpiration: int
        :param expMonth: expiration month ("JAN"|"FEB"|"MAR"|"APR"|"MAY"|"JUN"|"JUL"|"AUG"|"SEP"|"OCT"|"NOV"|"DEC"|"ALL")
        :type expMonth: str
        :param optionType: option type ("CALL"|"PUT")
        :type optionType: str
        :param entitlement: entitlement ("PN"|"NP"|"PP")
        :type entitlement: str
        :return: list of option chains
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/chains',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'symbol': symbol, 'contractType': contractType, 'strikeCount': strikeCount,
                                 'includeUnderlyingQuote': includeUnderlyingQuote, 'strategy': strategy,
                                 'interval': interval, 'strike': strike, 'range': range, 'fromDate': self._time_convert(fromDate, "YYYY-MM-DD"),
                                 'toDate': self._time_convert(toDate, "YYYY-MM-DD"), 'volatility': volatility, 'underlyingPrice': underlyingPrice,
                                 'interestRate': interestRate, 'daysToExpiration': daysToExpiration,
                                 'expMonth': expMonth, 'optionType': optionType, 'entitlement': entitlement}),
                            timeout=self.timeout)

    def option_expiration_chain(self, symbol: str) -> requests.Response:
        """
        Get an option expiration chain for a ticker
        :param symbol: ticker symbol
        :type symbol: str
        :return: option expiration chain
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/expirationchain',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'symbol': symbol}),
                            timeout=self.timeout)

    def price_history(self, symbol: str, periodType: str = None, period: any = None, frequencyType: str = None, frequency: any = None, startDate: datetime.datetime | str = None,
                      endDate: any = None, needExtendedHoursData: bool = None, needPreviousClose: bool = None) -> requests.Response:
        """
        Get price history for a ticker
        :param symbol: ticker symbol
        :type symbol: str
        :param periodType: period type ("day"|"month"|"year"|"ytd")
        :type periodType: str
        :param period: period
        :type period: int
        :param frequencyType: frequency type ("minute"|"daily"|"weekly"|"monthly")
        :type frequencyType: str
        :param frequency: frequency (1|5|10|15|30)
        :type frequency: int
        :param startDate: start date
        :type startDate: datetime.pyi | str
        :param endDate: end date
        :type endDate: datetime.pyi | str
        :param needExtendedHoursData: need extended hours data (True|False)
        :type needExtendedHoursData: boolean
        :param needPreviousClose: need previous close (True|False)
        :type needPreviousClose: boolean
        :return: dictionary of containing candle history
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/pricehistory',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'symbol': symbol, 'periodType': periodType, 'period': period,
                                                        'frequencyType': frequencyType, 'frequency': frequency,
                                                        'startDate': self._time_convert(startDate, 'epoch_ms'),
                                                        'endDate': self._time_convert(endDate, 'epoch_ms'),
                                                        'needExtendedHoursData': needExtendedHoursData,
                                                        'needPreviousClose': needPreviousClose}),
                            timeout=self.timeout)

    def movers(self, symbol: str, sort: str = None, frequency: any = None) -> requests.Response:
        """
        Get movers in a specific index and direction
        :param symbol: symbol ("$DJI"|"$COMPX"|"$SPX"|"NYSE"|"NASDAQ"|"OTCBB"|"INDEX_ALL"|"EQUITY_ALL"|"OPTION_ALL"|"OPTION_PUT"|"OPTION_CALL")
        :type symbol: str
        :param sort: sort ("VOLUME"|"TRADES"|"PERCENT_CHANGE_UP"|"PERCENT_CHANGE_DOWN")
        :type sort: str
        :param frequency: frequency (0|1|5|10|30|60)
        :type frequency: int
        :return: movers
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/movers/{symbol}',
                            headers={"accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'sort': sort, 'frequency': frequency}),
                            timeout=self.timeout)

    def market_hours(self, symbols: list[str], date: datetime.datetime | str = None) -> requests.Response:
        """
        Get Market Hours for dates in the future across different markets.
        :param symbols: list of market symbols ("equity", "option", "bond", "future", "forex")
        :type symbols: list
        :param date: date
        :type date: datetime.pyi | str
        :return: market hours
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'markets': symbols, #self._format_list(symbols),
                                 'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    def market_hour(self, market_id: str, date: datetime.datetime | str = None) -> requests.Response:
        """
        Get Market Hours for dates in the future for a single market.
        :param market_id: market id ("equity"|"option"|"bond"|"future"|"forex")
        :type market_id: str
        :param date: date
        :type date: datetime.pyi | str
        :return: market hours
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets/{market_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    def instruments(self, symbol: str, projection: str) -> requests.Response:
        """
        Get instruments for a list of symbols
        :param symbol: symbol
        :type symbol: str
        :param projection: projection ("symbol-search"|"symbol-regex"|"desc-search"|"desc-regex"|"search"|"fundamental")
        :type projection: str
        :return: instruments
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/instruments',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params={'symbol': symbol, 'projection': projection},
                            timeout=self.timeout)

    def instrument_cusip(self, cusip_id: str | int) -> requests.Response:
        """
        Get instrument for a single cusip
        :param cusip_id: cusip id
        :type cusip_id: str|int
        :return: instrument
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/instruments/{cusip_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)
