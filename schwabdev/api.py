import json
import base64
import requests
import threading
import urllib.parse
from . import color_print
from .stream import Stream
from datetime import datetime


class Client:

    def __init__(self, app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", timeout=5, show_linked=True):
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
        self._access_token_issued = None  # datetime of access token issue
        self._refresh_token_issued = None  # datetime of refresh token issue
        self._access_token_timeout = 1800  # in seconds (from schwab)
        self._refresh_token_timeout = 7  # in days (from schwab)
        self._tokens_file = tokens_file  # path to tokens file
        self.timeout = timeout
        self.stream = Stream(self)

        # Try to load tokens from the tokens file
        at_issued, rt_issued, token_dictionary = self._read_tokens_file()
        if None not in [at_issued, rt_issued, token_dictionary]:
            # show user when tokens were last updated and when they will expire
            self.access_token = token_dictionary.get("access_token")
            self.refresh_token = token_dictionary.get("refresh_token")
            self.id_token = token_dictionary.get("id_token")
            self._access_token_issued = at_issued
            self._refresh_token_issued = rt_issued
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
        if show_linked:
            resp = self.account_linked()
            if resp.ok:
                d = resp.json()
                color_print.info(f"Linked Accounts: {d}")
            else:  # app might not be "Ready For Use"
                color_print.error("Could not get linked accounts.")
                color_print.error("Please make sure that your app status is \"Ready For Use\" and that the app key and app secret are valid.")
                color_print.error(resp.json())
            resp.close()

        color_print.info("Initialization Complete")

    def update_tokens(self):
        if (datetime.now() - self._refresh_token_issued).days >= (
                self._refresh_token_timeout - 1):  # check if we need to update refresh (and access) token
            for i in range(5):  color_print.user("The refresh token has expired, please update!")
            self._update_refresh_token()
        elif ((datetime.now() - self._access_token_issued).days >= 1) or (
                (datetime.now() - self._access_token_issued).seconds > (
                self._access_token_timeout - 60)):  # check if we need to update access token
            color_print.info("The access token has expired, updating automatically.")
            self._update_access_token()
        # else: color_print.info("Token check passed")

    def update_tokens_auto(self):
        def checker():
            import time
            while True:
                self.update_tokens()
                time.sleep(60)

        threading.Thread(target=checker, daemon=True).start()

    # "refresh" the access token using the refresh token
    def _update_access_token(self):
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
                color_print.info(f"Access token updated: {self._access_token_issued}")
                break
            else:
                color_print.error(f"Could not get new access token ({i+1} of 3).")

    # get new access and refresh tokens using authorization code.
    def _update_refresh_token(self):
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
        # update tokens file
        try:
            with open(self._tokens_file, 'w') as f:
                toWrite = {"access_token_issued": atIssued.isoformat(), "refresh_token_issued": rtIssued.isoformat(),
                           "token_dictionary": tokenDictionary}
                json.dump(toWrite, f, ensure_ascii=False, indent=4)
                f.flush()
        except Exception as e:
            color_print.error(e)


    def _read_tokens_file(self):
        try:
            with open(self._tokens_file, 'r') as f:
                d = json.load(f)
                return datetime.fromisoformat(d.get("access_token_issued")), datetime.fromisoformat(d.get("refresh_token_issued")), d.get("token_dictionary")
        except Exception as e:
            color_print.error(e)
            return None, None, None

    # params_parser removed None (null) values
    def _params_parser(self, params):
        for key in list(params.keys()):
            if params[key] is None: del params[key]
        return params

    # convert time to the correct format, passthrough if a string, preserve None if None for params parser
    def _time_convert(self, dt=None, form="8601"):
        if dt is None:
            return None
        elif isinstance(dt, str):
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

    # Get account numbers and account hashes for linked accounts
    def account_linked(self):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/accountNumbers',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    # Get account details for all linked accounts, details such as balance, positions, buying power, etc.
    def account_details_all(self, fields=None):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    # Get account details for one linked account, uses default account.
    def account_details(self, accountHash, fields=None):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    # Get all orders for one linked account, uses default account.
    def account_orders(self, accountHash, maxResults, fromEnteredTime, toEnteredTime, status=None):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'maxResults': maxResults, 'fromEnteredTime': self._time_convert(fromEnteredTime, "8601"),
                                 'toEnteredTime': self._time_convert(toEnteredTime, "8601"), 'status': status}),
                            timeout=self.timeout)

    # place an order for one linked account (uses default account)
    def order_place(self, accountHash, order):
        return requests.post(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders',
                             headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}',
                                      "Content-Type": "application/json"},
                             json=order,
                             timeout=self.timeout)

    # get order details using order id (uses default account)
    def order_details(self, accountHash, orderId):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    # cancel order using order id (uses default account)
    def order_cancel(self, accountHash, orderId):
        return requests.delete(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                               headers={'Authorization': f'Bearer {self.access_token}'},
                               timeout=self.timeout)

    # replace order using order id (uses default account)
    def order_replace(self, accountHash, orderId, order):
        return requests.put(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/orders/{orderId}',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}',
                                     "Content-Type": "application/json"},
                            json=order,
                            timeout=self.timeout)

    # get all orders across all linked accounts
    def account_orders_all(self, maxResults, fromEnteredTime, toEnteredTime, status=None):
        return requests.get(f'{self._base_api_url}/trader/v1/orders',
                            headers={"Accept": "application/json", 'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'maxResults': maxResults, 'fromEnteredTime': self._time_convert(fromEnteredTime, "8601"),
                                 'toEnteredTime': self._time_convert(toEnteredTime, "8601"), 'status': status}),
                            timeout=self.timeout)

    """ #COMING SOON (waiting on Schwab)
      # /accounts/{accountHash}/previewOrder
    def order_preview(accountHash, orderObject):
        
        return requests.post(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/previewOrder',
                             headers={'Authorization': f'Bearer {self.access_token}',
                                      "Content-Type": "application.json"}, data=orderObject)

    """

    # get all transactions (has maximums) for one linked account (uses default account)
    def transactions(self, accountHash, startDate, endDate, types, symbol=None):
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/transactions',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'accountNumber': accountHash, 'startDate': self._time_convert(startDate, "8601"),
                                 'endDate': self._time_convert(endDate, "8601"), 'symbol': symbol, 'types': types}),
                            timeout=self.timeout)

    # get transaction details using transaction id (uses default account)
    def transaction_details(self, accountHash, transactionId):
        """
        :param accountHash:
        :param transactionId:
        :return:
        """
        return requests.get(f'{self._base_api_url}/trader/v1/accounts/{accountHash}/transactions/{transactionId}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params={'accountNumber': accountHash, 'transactionId': transactionId},
                            timeout=self.timeout)

    # get user preferences, includes streaming info
    def preferences(self):
        return requests.get(f'{self._base_api_url}/trader/v1/userPreference',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)

    """
    Market Data
    """
    
    # get quotes for a list of tickers
    def quotes(self, symbols=None, fields=None, indicative=False):
        return requests.get(f'{self._base_api_url}/marketdata/v1/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'symbols': self._format_list(symbols), 'fields': fields, 'indicative': indicative}),
                            timeout=self.timeout)

    # get a single quote for a ticker
    def quote(self, symbol_id, fields=None):
        return requests.get(f'{self._base_api_url}/marketdata/v1/{urllib.parse.quote(symbol_id)}/quotes',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'fields': fields}),
                            timeout=self.timeout)

    # get option chains for a ticker
    def option_chains(self, symbol, contractType=None, strikeCount=None, includeUnderlyingQuote=None, strategy=None,
               interval=None, strike=None, range=None, fromDate=None, toDate=None, volatility=None, underlyingPrice=None,
               interestRate=None, daysToExpiration=None, expMonth=None, optionType=None, entitlement=None):
        return requests.get(f'{self._base_api_url}/marketdata/v1/chains',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'symbol': symbol, 'contractType': contractType, 'strikeCount': strikeCount,
                                 'includeUnderlyingQuote': includeUnderlyingQuote, 'strategy': strategy,
                                 'interval': interval, 'strike': strike, 'range': range, 'fromDate': fromDate,
                                 'toDate': toDate, 'volatility': volatility, 'underlyingPrice': underlyingPrice,
                                 'interestRate': interestRate, 'daysToExpiration': daysToExpiration,
                                 'expMonth': expMonth, 'optionType': optionType, 'entitlement': entitlement}),
                            timeout=self.timeout)

    # get an option expiration chain for a ticker
    def option_expiration_chain(self, symbol):
        return requests.get(f'{self._base_api_url}/marketdata/v1/expirationchain',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'symbol': symbol}),
                            timeout=self.timeout)

    # get price history for a ticker
    def price_history(self, symbol, periodType=None, period=None, frequencyType=None, frequency=None, startDate=None,
                      endDate=None, needExtendedHoursData=None, needPreviousClose=None):
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
        return requests.get(f'{self._base_api_url}/marketdata/v1/movers/{symbol}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'sort': sort, 'frequency': frequency}),
                            timeout=self.timeout)

    # get market hours for a list of markets
    def market_hours(self, symbols, date=None):
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser(
                                {'markets': symbols, #self._format_list(symbols),
                                 'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    # get market hours for a single market
    def market_hour(self, market_id, date=None):
        return requests.get(f'{self._base_api_url}/marketdata/v1/markets/{market_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params=self._params_parser({'date': self._time_convert(date, 'YYYY-MM-DD')}),
                            timeout=self.timeout)

    # get instruments for a list of symbols
    def instruments(self, symbol, projection):
        return requests.get(f'{self._base_api_url}/marketdata/v1/instruments',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            params={'symbol': symbol, 'projection': projection},
                            timeout=self.timeout)

    # get instruments for a single cusip
    def instrument_cusip(self, cusip_id):
        return requests.get(f'{self._base_api_url}/marketdata/v1/instruments/{cusip_id}',
                            headers={'Authorization': f'Bearer {self.access_token}'},
                            timeout=self.timeout)
