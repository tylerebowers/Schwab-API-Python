# Client API access

After making a client object i.e. `client = schwabdev.Client(...)` we are free to make api calls or start a stream. Below is a list of all possible calls that can be made with the api.
You can also reference the [schwab documentation](https://developer.schwab.com/products/trader-api--individual), each call is named similarly. 

### Notes:
* In order to use all api calls you must have both "APIs" added to your app, both "Accounts and Trading Production" and "Market Data Production"
* After making a call you will recive a response object, to get the data you can call .json(), however it is best to check if the response is good by calling .ok which returns a boolean of True if the response code is in the 200 range.
* In this documentation, parameters with ...=None are optional and can be left blank.
* All time/dates can either be strings or datetime objects.
* All lists can be passed as comma strings "a,b,c" or lists of strings ["a", "b", "c"].

## API Calls

<!---## Accounts and Trading - Accounts -->

### Get account number and hashes for linked accounts
> Syntax: `client.account_linked()`  
> * Returns(request.Response): list of dict containing account numbers and hashes   
> 
> Return_example: `[{'accountNumber': 'XXXX', 'hashValue': 'XXXX'}]`

### Get details for all linked accounts
> Syntax: `client.account_details_all(fields=None)`  
> * Param fields(str): Additional fields to get; Options: "positions" current positions.  
> 
> Returns(request.Response): list of dict containing details for all linked accounts (example output shortened)  
> Return_example: `[{'securitiesAccount': {'type': 'XXXX', 'accountNumber': 'XXXX', 'roundTrips': XXXX, 'isDayTrader': XXXX, ........}]`

### Get specific account positions
> Syntax: `client.account_details(account_hash, fields=None)`  
> * Param account_hash(str): account hash to get details of.  
> * Param fields(str): Additional fields to get; Options: "positions" current positions.  
> 
> Returns(request.Response):  dict containing details for all linked accounts (example output shortened)  
> Return_example: `{'securitiesAccount': {'type': 'XXXX', 'accountNumber': 'XXXX', 'roundTrips': XXXX, 'isDayTrader': XXXX, ........}`

<!---## Accounts and Trading - Orders -->

### Get orders for a linked account
> Syntax: `client.account_orders(accountHash, fromEnteredTime, toEnteredTime, maxResults=None, status=None)`  
> * Param account_hash(str): account hash to get details of.  
> * Param from_entered_time(datetime|str): from date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param to_entered_time(datetime|str): to date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param max_results(int): maximum number of orders to get (default 3000)  
> * Param status(str): status of orders; Options: ("AWAITING_PARENT_ORDER", "AWAITING_CONDITION", "AWAITING_STOP_CONDITION", "AWAITING_MANUAL_REVIEW", "ACCEPTED", "AWAITING_UR_OUT", "PENDING_ACTIVATION", "QUEUED", "WORKING", "REJECTED", "PENDING_CANCEL", "CANCELED", "PENDING_REPLACE", "REPLACED", "FILLED", "EXPIRED", "NEW", "AWAITING_RELEASE_TIME", "PENDING_ACKNOWLEDGEMENT", "PENDING_RECALL", "UNKNOWN")  
> 
> Returns(request.Response):  Returns up to [maxResults] orders from the account tied to account_hash from [from_entered_time] to [to_entered_time] with status [status].

### Place an order 
> Syntax: `client.order_place(account_hash, order)`  
> * Param account_hash(str): account hash to get place order on.  
> * Param order(dict): Order dict to place, there are examples in orders.md and in the Schwab documentation. 
> 
> Returns(request.Response):  Response object.  
>> Get the order id by checking the headers.  
>> `order_id = resp.headers.get('location', '/').split('/')[-1]`  
>> *If order is immediately filled then the id might not be returned*

### Get specific order details
> Syntax: `print(client.order_details(account_hash, order_id)`  
> * Param account_hash(str): account hash that order was placed on.  
> * Param order_id(int): order id to get details of.
> 
> Returns(request.Response):  Details of the order.

### Cancel a specific order
> Syntax: `client.order_cancel(account_hash, order_id)`  
> * Param account_hash(str): account hash that order was placed on.  
> * Param order_id(int): order id to cancel.  
> 
> Returns(request.Response): Empty if successful.  

### Replace a specific order
> Syntax: `client.order_replace(account_hash, orderID, order)`  
> * Param account_hash(str): account hash that order was placed on.  
> * Param orderID(int): order id to be replace.  
> * Param order(dict): Order dict to replace orderID with.   
> 
> Returns(request.Response):  Empty if successful.  

### Get account orders for all linked accounts
> Syntax: `client.account_orders_all(fromEnteredTime, toEnteredTime, maxResults=None, status=None)`  
> * Param account_hash(str): account hash to get details of.  
> * Param from_entered_time(datetime|str): from date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param to_entered_time(datetime|str): to date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param max_results(int): maximum number of orders to get (default 3000)  
> * Param status(str): status of orders; Options: ("AWAITING_PARENT_ORDER", "AWAITING_CONDITION", "AWAITING_STOP_CONDITION", "AWAITING_MANUAL_REVIEW", "ACCEPTED", "AWAITING_UR_OUT", "PENDING_ACTIVATION", "QUEUED", "WORKING", "REJECTED", "PENDING_CANCEL", "CANCELED", "PENDING_REPLACE", "REPLACED", "FILLED", "EXPIRED", "NEW", "AWAITING_RELEASE_TIME", "PENDING_ACKNOWLEDGEMENT", "PENDING_RECALL", "UNKNOWN")  
> 
> Returns(request.Response):  Returns up to [maxResults] orders from all linked accounts from [from_entered_time] to [to_entered_time] with status [status].  

### Preview order (not implemented by Schwab yet)
> Syntax: `client.order_preview(account_hash, orderObject)`
> * Param account_hash(str): account hash to get place order on.  
> * Param order_obj(dict): Order dict to place, there are examples in orders.md and in the Schwab documentation.  
> 
> Returns(request.Response):  A preview of the order.

<!---## Accounts and Trading - Transactions -->

### Get all transactions for an account
> Syntax: `client.transactions(accountHash, startDate, endDate, types, symbol=None)`  
> * Param account_hash(str): account hash to get transactions from.  
> * Param start_date(datetime|str): start date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param end_date(datetime|str): end date; Use datetime object or str format: yyyy-MM-dd'T'HH:mm:ss.SSSZ  
> * Param types(list|str): list of transaction types to get (TRADE, RECEIVE_AND_DELIVER, DIVIDEND_OR_INTEREST, ACH_RECEIPT, ACH_DISBURSEMENT, CASH_RECEIPT, CASH_DISBURSEMENT, ELECTRONIC_FUND, WIRE_OUT, WIRE_IN, JOURNAL, MEMORANDUM, MARGIN_CALL, MONEY_MARKET, SMA_ADJUSTMENT)  
> * Param symbol(str): only get transactions for this symbol, special symbols (i.e. "/" or "$") must be encoded
> 
> Returns(request.Response):  A list of transactions.

### Get details for a specific transaction
> Syntax: `client.transaction_details(account_hash, transactionId)`  
> * Param account_hash(str): account hash to get transactions from.  
> * Param transaction_id(str): transaction id to get details of. 
> 
> Returns(request.Response):  Details of the transaction.  

<!---## Accounts and Trading - UserPreference-->

### Get user preferences for accounts, includes streaming information
> Syntax: `client.preferences()`  
> Returns(request.Response):  User preferences for an accounts.  
> Return_example: `[{"accounts": [...], "streamerInfo": [...], "offers": [...]}]`

<!---## Market Data - Quotes-->

### Get a list of quotes
> Syntax: `client.quotes(symbols=None, fields=None, indicative=False)`  
> * Param symbols(list|str): list of symbols to get quotes for. i.e. ["AAPL", "AMD"] or "AAPL,AMD"  
> * Param fields(str): list of fields to get quotes for. Options "all"(default), "quote", "fundamental"  
> * Param indicative(bool): return indicative quotes. (default False)  
> 
> Returns(request.Response):  A list of quote dicts.

### Get a single quote
> Syntax: `client.quote(symbol_id, fields=None)`  
> * Param symbol_id(str): symbol id to get quote for. i.e. "AAPL"  
> * Param fields(str): list of fields to get quote for. Options "all"(default), "quote", "fundamental"  
> 
> Returns(request.Response):  A quote dict.  

<!---## Market Data - Options Chains-->

### Get an option chain
> Syntax: `client.option_chains(symbol, contractType=None, strikeCount=None, includeUnderlyingQuote=None, strategy=None,
               interval=None, strike=None, range=None, fromDate=None, toDate=None, volatility=None, underlyingPrice=None,
               interestRate=None, daysToExpiration=None, expMonth=None, optionType=None, entitlement=None)`  
> * Param symbol(str): symbol to get option chain for. i.e. "AAPL"   
> * Param contractType(str): contract type to get option chain for. Options "ALL", "CALL", "PUT"  
> * Param strikeCount(int): number of strikes to get option chain for.   
> * Param includeUnderlyingQuote(bool): include underlying quote in option chain.   
> * Param strategy(str): strategy to get option chain for. Options SINGLE(default), ANALYTICAL, COVERED, VERTICAL, CALENDAR, STRANGLE, STRADDLE, BUTTERFLY, CONDOR, DIAGONAL, COLLAR, ROLL  
> * Param interval(float): interval to get option chain for.  
> * Param strike(float): strike price.  
> * Param range(str): range to get option chain for. Options ITM, ATM, OTM, etc  
> * Param fromDate(datetime|str): start date; Use datetime object or str format: yyyy-MM-dd  
> * Param toDate(datetime|str): end date; Use datetime object or str format: yyyy-MM-dd  
> * Param volatility(float): volatility  
> * Param underlyingPrice(float): underlying price  
> * Param interestRate(float): interest rate  
> * Param daysToExpiration(int): days to expiration  
> * Param expMonth(str): expiration month, Options JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC  
> * Param optionType(str): option type  
> * Param entitlement(str): entitlement Options: PN, NP, PP  -> PP-PayingPro, NP-NonPro and PN-NonPayingPro  
> 
> Returns(request.Response):  A list of option chain dicts.  

<!---## Market Data - Options Expiration Chain-->

### Get an option expiration chain
> Syntax: `client.option_expiration_chain(symbol)`  
> * Param symbol(str): symbol to get option expiration chain for. i.e. "AAPL"
> 
> Returns(request.Response):  A list of option expiration chain dicts.

<!---## Market Data - PriceHistory -->

### Get price history for a symbol
> Syntax: `client.price_history(symbol, periodType=None, period=None, frequencyType=None, frequency=None, startDate=None,
                      endDate=None, needExtendedHoursData=None, needPreviousClose=None)`  
> * Param symbol(str): symbol to get price history for. i.e. "AAPL"   
> * Param periodType(str): period type to get price history for. Options "day", "month", "year", "ytd"   
> * Param period(int): period to get price history for. Options: periodType is day -> 1, 2, 3, 4, 5, 10; month -> 1, 2, 3, 6; year -> 1, 2, 3, 5, 10, 15, 20; ytd -> 1; default is 1 unless periodType is "day" then default is 10.  
> * Param frequencyType(str): frequency type to get price history for. Options: periodType is day -> minute; month -> daily, weekly; year -> daily, weekly, monthly; ytd -> daily, weekly; default is largest possible per periodType.  
> * Param frequency(int): frequency to get price history for. Options: periodType is day -> minute; month -> daily, weekly; year -> daily, weekly, monthly; ytd -> daily, weekly;   
> * Param startDate(datetime|int): start date; Use datetime object or UNIX epoch  
> * Param endDate(datetime|int): end date; Use datetime object or UNIX epoch   
> * Param needExtendedHoursData(bool): need extended hours data.   
> * Param needPreviousClose(bool): need previous close.
>
> Returns(request.Response):  A dict containing price history in candles.  

<!---## Market Data - Movers-->

### Get movers for an index
> Syntax: `client.movers(symbol, sort=None, frequency=None)`
> * Param symbol(str): index symbol to get movers for. Options: $DJI, $COMPX, $SPX, NYSE, NASDAQ, OTCBB, INDEX_ALL, EQUITY_ALL, OPTION_ALL, OPTION_PUT, OPTION_CALL
> * Param sort(str): sort to get movers for. Options: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN   
> * Param frequency(int): specified direction up or down. Options: 0(default), 1, 5, 10, 30, 60
> 
> Returns(request.Response):  A list of movers.

<!---## Market Data - MarketHours-->

### Get market hours for a symbol
> Syntax: `client.market_hours(symbols, date=None)`  
> * Param symbols(list|str): symbol to get market hours for. Options: equity, option, bond, future, forex  
> * Param date(datetime|str): date to get market hours for. Use datetime object or string in format yyyy-MM-dd, default is today 
> 
> Returns(request.Response):  A list of market hours.  

### Get market hours for a market
> Syntax: `client.market_hour(market_id, date=None)`    
> * Param market_id(str): market id to get market hours for. Options: equity, option, bond, future, forex  
> * Param date(datetime|str): date to get market hours for. Use datetime object or string in format yyyy-MM-dd, default is today 
> 
> Returns(request.Response):  market hours for market_id.  

<!---## Market Data - Instruments-->

### Get instruments for a symbol
> Syntax: `client.instruments(symbol, projection)`
> * Param symbol(str): symbol to get instruments for. i.e. "AAPL"
> * Param projection(str): projection to get instruments for. Options: "symbol-search", "symbol-regex"(symbol=XYZ.*), "desc-search", "desc-regex"(symbol=XYZ.[A-C]), "search", "fundamental"
> 
> Returns(request.Response):  A dict of instruments.

### Get instruments for a cusip
> Syntax: `client.instrument_cusip(cusip_id)`
> * Param cusip_id(str): cusip id to get instruments for. i.e. "AAPL"
> 
> Returns(request.Response):  An instrument.