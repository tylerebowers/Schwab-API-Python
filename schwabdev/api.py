import json
import base64
import requests
import threading
import urllib.parse
from . import color_print
from .stream import Stream
from datetime import datetime


class Client:

    def __init__(self, app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", timeout=5, verbose=True, show_linked=True):
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

        if app_key is None or app_secret is None or callback_url is None or tokens_file is None:
            raise Exception("app_key, app_secret, callback_url, and tokens_file cannot be None.")
        elif len(app_key) != 32 or len(app_secret) != 16:
            raise Exception("App key or app secret invalid length.")

        self._app_key = app_key
        self._app_secret = app_secret
        self._callback_url = callback_url
        self.access_token = None
        self.refresh_token = None
        self.id_token = None
        self._access_token_issued = None    # datetime of access token issue
        self._refresh_token_issued = None   # datetime of refresh token issue
        self._access_token_timeout = 1800   # in seconds (from schwab)
        self._refresh_token_timeout = 7     # in days (from schwab)
        self._tokens_file = tokens_file     # path to tokens file
        self.timeout = timeout
        self._verbose = verbose             # verbose mode
        self.stream = Stream(self)          # init the streaming object

        # Try to load tokens from the tokens file
        at_issued, rt_issued, token_dictionary = self._read_tokens_file()
        if None not in [at_issued, rt_issued, token_dictionary]:
            # show user when tokens were last updated and when they will expire
            self.access_token = token_dictionary.get("access_token")
            self.refresh_token = token_dictionary.get("refresh_token")
            self.id_token = token_dictionary.get("id_token")
            self._access_token_issued = at_issued
            self._refresh_token_issued = rt_issued
            if self._verbose:
                color_print.info(self._access_token_issued.strftime(
                    "Access token last updated: %Y-%m-%d %H:%M:%S") + f" (expires in {self._access_token_timeout - (datetime.now() - self._access_token_issued).seconds} seconds)")
                color_print.info(self._refresh_token_issued.strftime(
                    "Refresh token last updated: %Y-%m-%d %H:%M:%S") + f" (expires in {self._refresh_token_timeout - (datetime.now() - self._refresh_token_issued).days} days)")
            # check if tokens need to be updated and update if needed
            self.update_tokens()
        else:
            # The tokens file doesn't exist, so create it.
            color_print.warning(f"Token file does not exist or invalid formatting, creating \"{str(tokens_file)}\"")
            open(self._tokens_file, 'w').close()
            # Tokens must be updated.
            self._update_refresh_token()

        # get account numbers & hashes, this doubles as a checker to make sure that the appKey and appSecret are valid and that the app is ready for use
        if show_linked and self._verbose:
            resp = self.account_linked()
            if resp.ok:
                d = resp.json()
                color_print.info(f"Linked Accounts: {d}")
            else:  # app might not be "Ready For Use"
                color_print.error("Could not get linked accounts.")
                color_print.error("Please make sure that your app status is \"Ready For Use\" and that the app key and app secret are valid.")
                color_print.error(resp.json())
            resp.close()

        if self._verbose:
            color_print.info("Initialization Complete")

    def update_tokens(self):
        """
        Checks if tokens need to be updated and updates if needed (only access token is automatically updated)
        """
        if (datetime.now() - self._refresh_token_issued).days >= (self._refresh_token_timeout - 1):  # check if we need to update refresh (and access) token
            for i in range(3):  color_print.user("The refresh token has expired, please update!")
            self._update_refresh_token()
        elif ((datetime.now() - self._access_token_issued).days >= 1) or (
                (datetime.now() - self._access_token_issued).seconds > (self._access_token_timeout - 61)):  # check if we need to update access token
            if self._verbose:
                color_print.info("The access token has expired, updating automatically.")
            self._update_access_token()
        # else: color_print.info("Token check passed")

    def update_tokens_auto(self):
        """
        Spawns a thread to check the access token and update if necessary
        """
        def checker():
            import time
            while True:
                self.update_tokens()
                time.sleep(60)

        threading.Thread(target=checker, daemon=True).start()

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
                self._access_token_issued = datetime.now()
                self._refresh_token_issued = refresh_token_issued
                new_td = response.json()
                self.access_token = new_td.get("access_token")
                self.refresh_token = new_td.get("refresh_token")
                self.id_token = new_td.get("id_token")
                self._write_tokens_file(self._access_token_issued, refresh_token_issued, new_td)
                # show user that we have updated the access token
                if self._verbose:
                    color_print.info(f"Access token updated: {self._access_token_issued}")
                break
            else:
                color_print.error(f"Could not get new access token ({i+1} of 3).")

    def _update_refresh_token(self):
        """
        Get new access and refresh tokens using authorization code.
        """
        import webbrowser
        # get authorization code (requires user to authorize)
        color_print.user("Please authorize this program to access your schwab account.")
        auth_url = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={self._app_key}&redirect_uri={self._callback_url}'
        color_print.user(f"Click to authenticate: {auth_url}")
        color_print.user("Opening browser...")
        webbrowser.open(auth_url)
        response_url = color_print.user_input(
            "After authorizing, wait for it to load (<1min) and paste the WHOLE url here: ")
        code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"  # session = responseURL[responseURL.index("session=")+8:]
        # get new access and refresh tokens
        response = self._post_oauth_token('authorization_code', code)
        if response.ok:
            # update token file and variables
            self._access_token_issued = self._refresh_token_issued = datetime.now()
            new_td = response.json()
            self.access_token = new_td.get("access_token")
            self.refresh_token = new_td.get("refresh_token")
            self.id_token = new_td.get("id_token")
            self._write_tokens_file(self._access_token_issued, self._refresh_token_issued, new_td)
            color_print.info("Refresh and Access tokens updated")
        else:
            color_print.error("Could not get new refresh and access tokens, check these:\n    1. App status is "
                              "\"Ready For Use\".\n    2. App key and app secret are valid.\n    3. You pasted the "
                              "whole url within 30 seconds. (it has a quick expiration)")

    def _post_oauth_token(self, grant_type, code):
        """
        Makes API calls for auth code and refresh tokens
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
            color_print.error("Invalid grant type")
            return None
        return requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

    def _write_tokens_file(self, atIssued, rtIssued, tokenDictionary):
        """
        Writes token file
        :param atIssued: access token issued
        :type atIssued: datetime
        :param rtIssued: refresh token issued
        :type rtIssued: datetime
        :param tokenDictionary: token dictionary
        :type tokenDictionary: dict
        """
        try:
            with open(self._tokens_file, 'w') as f:
                toWrite = {"access_token_issued": atIssued.isoformat(), "refresh_token_issued": rtIssued.isoformat(),
                           "token_dictionary": tokenDictionary}
                json.dump(toWrite, f, ensure_ascii=False, indent=4)
                f.flush()
        except Exception as e:
            color_print.error(e)


    def _read_tokens_file(self):
        """
        Reads token file
        :return: access token issued, refresh token issued, token dictionary
        :rtype: datetime, datetime, dict
        """
        try:
            with open(self._tokens_file, 'r') as f:
                d = json.load(f)
                return datetime.fromisoformat(d.get("access_token_issued")), datetime.fromisoformat(d.get("refresh_token_issued")), d.get("token_dictionary")
        except Exception as e:
            color_print.error(e)
            return None, None, None

    def _params_parser(self, params):
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

    def _time_convert(self, dt=None, form="8601"):
        """
        Convert time to the correct format, passthrough if a string, preserve None if None for params parser
        :param dt: datetime object to convert
        :type dt: datetime
        :param form: what to convert input to
        :type form: str
        :return: converted time or passthrough
        :rtype: str | None
        """
        if dt is None or isinstance(dt, str):
            return dt
        elif form == "8601":  # assume datetime object from here on
            return f'{dt.isoformat()[:-3]}Z'
        elif form == "epoch":
            return int(dt.timestamp())
        elif form == "epoch_ms":
            return int(dt.timestamp() * 1000)
        elif form == "YYYY-MM-DD":
            return dt.strftime("%Y-%m-%d")
        else:
            return dt

    def _format_list(self, l):
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

    def account_linked(self):
        """
        Account numbers in plain text cannot be used outside of headers or request/response bodies. As the first step consumers must invoke this service to retrieve the list of plain text/encrypted value pairs, and use encrypted account values for all subsequent calls for any accountNumber request.
        :return: All linked account numbers and hashes
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/accountNumbers',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    def account_details_all(self, fields=None):
        """
        All the linked account information for the user logged in. The balances on these accounts are displayed by default however the positions on these accounts will be displayed based on the "positions" flag.
        :param fields: fields to return (options: "positions")
        :type fields: str
        :return: details for all linked accounts
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    def account_details(self, accountHash, fields=None):
        """
        Specific account information with balances and positions. The balance information on these accounts is displayed by default but Positions will be returned based on the "positions" flag.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param fields: fields to return
        :type fields: str
        :return: details for one linked account
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    def account_orders(self, accountHash, fromEnteredTime, toEnteredTime, maxResults=None, status=None):
        """
        All orders for a specific account. Orders retrieved can be filtered based on input parameters below. Maximum date range is 1 year.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param fromEnteredTime: from entered time
        :type fromEnteredTime: datetime | str
        :param toEnteredTime: to entered time
        :type toEnteredTime: datetime | str
        :param maxResults: maximum number of results
        :type maxResults: int
        :param status: status ("AWAITING_PARENT_ORDER"|"AWAITING_CONDITION"|"AWAITING_STOP_CONDITION"|"AWAITING_MANUAL_REVIEW"|"ACCEPTED"|"AWAITING_UR_OUT"|"PENDING_ACTIVATION"|"QUEUED"|"WORKING"|"REJECTED"|"PENDING_CANCEL"|"CANCELED"|"PENDING_REPLACE"|"REPLACED"|"FILLED"|"EXPIRED"|"NEW"|"AWAITING_RELEASE_TIME"|"PENDING_ACKNOWLEDGEMENT"|"PENDING_RECALL"|"UNKNOWN")
        :type status: str
        :return: orders for one linked account hash
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'maxResults': maxResults, 'fromEnteredTime': self._time_convert(fromEnteredTime, "8601"),
                                 'toEnteredTime': self._time_convert(toEnteredTime, "8601"), 'status': status}),
                            timeout=self.timeout)

    def order_place(self, accountHash, order):
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

    def order_details(self, accountHash, orderId):
        """
        Get a specific order by its ID, for a specific account
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: str
        :return: order details
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    def order_cancel(self, accountHash, orderId):
        """
        Cancel a specific order by its ID, for a specific account
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: str
        :return: response code
        :rtype: request.Response
        """
        return requests.delete(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                               headers={'Authorization': f'Bearer {self.access_token}'},
                               timeout=self.timeout)

    def order_replace(self, accountHash, orderId, order):
        """
        Replace an existing order for an account. The existing order will be replaced by the new order. Once replaced, the old order will be canceled and a new order will be created.
        :param accountHash: account hash from account_linked()
        :type accountHash: str
        :param orderId: order id
        :type orderId: str
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

    def account_orders_all(self, fromEnteredTime, toEnteredTime, maxResults=None, status=None):
        """
        Get all orders for all accounts
        :param fromEnteredTime: start date
        :type fromEnteredTime: datetime | str
        :param toEnteredTime: end date
        :type toEnteredTime: datetime | str
        :param maxResults: maximum number of results (set to None for default 3000)
        :type maxResults: int
        :param status: status ("AWAITING_PARENT_ORDER"|"AWAITING_CONDITION"|"AWAITING_STOP_CONDITION"|"AWAITING_MANUAL_REVIEW"|"ACCEPTED"|"AWAITING_UR_OUT"|"PENDING_ACTIVATION"|"QUEUED"|"WORKING"|"REJECTED"|"PENDING_CANCEL"|"CANCELED"|"PENDING_REPLACE"|"REPLACED"|"FILLED"|"EXPIRED"|"NEW"|"AWAITING_RELEASE_TIME"|"PENDING_ACKNOWLEDGEMENT"|"PENDING_RECALL"|"UNKNOWN")
        :type status: str
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
    def order_preview(self, accountHash, orderObject):
        #COMING SOON (waiting on Schwab)
        return requests.post(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/previewOrder',
                             headers={'Authorization': f'Bearer {self.access_token}',
                                      "Content-Type": "application.json"}, data=orderObject)
    """

    def transactions(self, accountHash, startDate, endDate, types, symbol=None):
        """
        All transactions for a specific account. Maximum number of transactions in response is 3000. Maximum date range is 1 year.
        :param accountHash: account hash number
        :type accountHash: str
        :param startDate: start date
        :type startDate: datetime | str
        :param endDate: end date
        :type endDate: datetime | str
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

    def transaction_details(self, accountHash, transactionId):
        """
        Get specific transaction information for a specific account
        :param accountHash: account hash number
        :type accountHash: str
        :param transactionId: transaction id
        :type transactionId: int
        :return: transaction details of transaction id using accountHash
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/transactions/{transactionId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params={'accountNumber': accountHash, 'transactionId': transactionId},
                            timeout=self.timeout)

    def preferences(self):
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
    
    def quotes(self, symbols=None, fields=None, indicative=False):
        """
        Get quotes for a list of tickers
        :param symbols: list of symbols strings (e.g. "AMD,INTC" or ["AMD", "INTC"])
        :type symbols: [str] | str
        :param fields: list of fields to get ("all", "quote", "fundamental")
        :type fields: list
        :param indicative: whether to get indicative quotes (True/False)
        :type indicative: boolean
        :return: list of quotes
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'symbols': self._format_list(symbols), 'fields': fields, 'indicative': indicative}),
                            timeout=self.timeout)

    def quote(self, symbol_id, fields=None):
        """
        Get quote for a single symbol
        :param symbol_id: ticker symbol
        :type symbol_id: str (e.g. "AAPL", "/ES", "USD/EUR")
        :param fields: list of fields to get ("all", "quote", "fundamental")
        :type fields: list
        :return: quote for a single symbol
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/{urllib.parse.quote(symbol_id)}/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    # get option chains for a ticker
    def option_chains(self, symbol, contractType=None, strikeCount=None, includeUnderlyingQuote=None, strategy=None,
               interval=None, strike=None, range=None, fromDate=None, toDate=None, volatility=None, underlyingPrice=None,
               interestRate=None, daysToExpiration=None, expMonth=None, optionType=None, entitlement=None):
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
        :type fromDate: datetime | str
        :param toDate: to date
        :type toDate: datetime | str
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

    # get an option expiration chain for a ticker
    def option_expiration_chain(self, symbol):
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

    # get price history for a ticker
    def price_history(self, symbol, periodType=None, period=None, frequencyType=None, frequency=None, startDate=None,
                      endDate=None, needExtendedHoursData=None, needPreviousClose=None):
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
        :type startDate: datetime | str
        :param endDate: end date
        :type endDate: datetime | str
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

    # get movers in a specific index and direction
    def movers(self, symbol, sort=None, frequency=None):
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
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'sort': sort, 'frequency': frequency}),
                            timeout=self.timeout)

    # get market hours for a list of markets
    def market_hours(self, symbols, date=None):
        """
        Get Market Hours for dates in the future across different markets.
        :param symbols: list of market symbols ("equity", "option", "bond", "future", "forex")
        :type symbols: list
        :param date: date
        :type date: datetime | str
        :return: market hours
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'markets': symbols, #self._format_list(symbols),
                                 'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    # get market hours for a single market
    def market_hour(self, market_id, date=None):
        """
        Get Market Hours for dates in the future for a single market.
        :param market_id: market id ("equity"|"option"|"bond"|"future"|"forex")
        :type market_id: str
        :param date: date
        :type date: datetime | str
        :return: market hours
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets/{market_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    # get instruments for a list of symbols
    def instruments(self, symbol, projection):
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

    # get instruments for a single cusip
    def instrument_cusip(self, cusip_id):
        """
        Get instrument for a single cusip
        :param cusip_id: cusip id
        :type cusip_id: str
        :return: instrument
        :rtype: request.Response
        """
        return requests.get(f'{self._base_api_url}/marketdata/v1/instruments/{cusip_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)
