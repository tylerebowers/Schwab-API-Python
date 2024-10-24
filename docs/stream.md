# Using the Streamer
Examples can be found in `examples/stream_demo.py`, there is also a streamer guide for more details.

To first use the streamer we have to initialize the client as normal `client = schwabdev.Client(...)`, the initialization of the client object also initializes a streamer which can be accessed via `client.stream`. It is recommended to set a streamer variable such as `streamer = client.stream` for shorter code and readability, documentation will also reference this variable name.

```py
import schwabdev
client = schwabdev.Client(...)
streamer = client.stream
```
### Starting the stream
To start the streamer you simply call `streamer.start()`, however you will need a response handler to do something useful, see below. The stream will close after ~30 seconds if there are no subscriptions. By default the stream starts as a daemon thread, meaning that if the main thread terminates then the stream will too, however if you want the stream to continue despite the main thread terminating then add `daemon=False` to the .start(...) parameters - this is useful if you are only using the response handler for processing.
### Using your own response handler
In typical applications you will want to use a seperate response handler that parses received data from the stream. The default method just prints to the terminal. 
```py
def my_handler(message):
        print("TEST" + message)
streamer.start(my_handler)
```
In the above example, the `my_handler` function is called whenever a response is received from the stream, and prints "TEST" prefixed with the response to the terminal. It is important to code this function such that it is not too taxing on the system as we dont want the response handler to run behind the streamer. You can also pass in variables, args and/or kwargs, into the start function which will be passed to the `my_handler` function.  
### Starting the stream automatically
If you want to start the streamer automatically when the market opens then instead of `streamer.start()` use the call `streamer.start_automatic(receiver=print, start_time=..., stop_time=..., daemon=True)`, shown are the default values which will start & stop the streamer during normal market hours (9:30am-4:00pm). If you want to start and/or stop the streamer at specific times then set the `start_time` and `stop_time` parameters to `datetime.datetime.time(HH,MM,SS, tzinfo=datetime.timezone.utc)`, times are in UTC; You can also change the days when the streamer starts by adding a list or set of ints to the `on_days` parameter, the default (Mon-Fri) is `on_days=(0,1,2,3,4)`. Starting the stream automatically will preserve the previous subscriptions.
### Stopping the stream
To stop the streamer use `streamer.stop()`, pass the parameter `clear_subscriptions=False` (default: true) if you want to keep the recorded subscriptions -> this means that the next time you start the steam it will resubscribe to the previous subscriptions (except if program is restarted).
### Sending stream requests
Sending in requests to the streamer can be done using the `streamer.send(message)` function. Schwabdev offers shortcut functions for **all** streamable assets (covered below), to subscribe to an equity, pass in `streamer.level_one_equities(...)` to the send function. Important: "0" must always be included in the fields. Shown here is every way to use the shortcut functions:
```py
# Every way to subscribe to the fields 0,1,2,3 for equities "AMD" and "INTC"
streamer.send(streamer.level_one_equities("AMD,INTC", "0,1,2,3"))
streamer.send(streamer.level_one_equities(["AMD","INTC"], ["0","1","2","3"]))
streamer.send(streamer.level_one_equities("AMD,INTC", "0,1,2,3", command="ADD"))
streamer.send(streamer.basic_request("LEVELONE_EQUITIES", "ADD", parameters={"keys": "AMD,INTC", "fields": "0,1,2,3"}))
```
If you are using an async function, then sending asyncronous requests to the streamer can be done using the `streamer.send_async(message)` function. 
```py
# Asyncronous subscription request for fields 0,1,2,3 of equities "AMD" and "INTC"
await streamer.send_async(streamer.level_one_equities("AMD,INTC", "0,1,2,3"))
```
## Streamable assets
Notes:  
* "0" must always be included in the fields.
* The list of fields and their definitions can be found in the streamer guide pdf.
* The maximum number of keys that can be subscribed to at once is 500.
* Shortcut function commands can be changed by setting the command parameter i.e. command="ADD". The default is the "ADD" command with the exception of account_activity with a default of "SUBS". Each command is explained below:
    * "ADD" -> the list of symbols will be added/appended to current subscriptions for a particular service, 
    * "SUBS" -> overwrites ALL current subscriptions (in a particular service) with the list of symbols passed in. 
    * "UNSUBS" -> removes the list of symbols from current subscriptions for a particular service. 
    * "VIEW" -> change the list of subscribed fields for the passed in symbols. \**Might not be functional on Schwab's end.*
* These shortcuts all send the same thing:
    * `streamer.basic_request("LEVELONE_EQUITIES", "ADD", parameters={"keys": "AMD,INTC", "fields": "0,1,2,3,4"}))`
    * `streamer.level_one_equities("AMD,INTC", "0,1,2,3,4", command="ADD"))`
    * `streamer.level_one_equities(["AMD", "INTC"], "0,1,2,3,4")`
    * `streamer.level_one_equities("AMD,INTC", ["0", "1", "2", "3", "4"])`
    * `streamer.level_one_equities("AMD,INTC", "0,1,2,3,4")`
* Different products have different methods of sending data:
    * LEVELONE_EQUITIES, LEVELONE_OPTIONS, LEVELONE_FUTURES, LEVELONE_FUTURES_OPTIONS, and LEVELONE_FOREX all stream **changes**, meaning that the data you receive overwrites the previous fields. E.g. if you first receive {"1": 20, "2": 25, "3": 997}, then secondly receive {"2": 28}, the current data (for secondly) will be {"1": 20, "2": 28, "3": 997}
    * NYSE_BOOK, NASDAQ_BOOK, OPTIONS_BOOK, SCREENER_EQUITY, and SCREENER_OPTION all stream **whole** data, meaning all fields.
    * CHART_EQUITY, CHART_FUTURES, and ACCT_ACTIVITY stream **all sequence** data, meaning you are given a sequence number for each response.

Listed below are the shortcut functions for all streamable assets.

### Level one equities  
> `streamer.send(streamer.level_one_equities(keys, fields))`   
> Key examples: "AMD", "INTC", "$SPX"

<!---
| Field | Name                              | Type    | Description                                                                                                                   | Notes                                                                                                                                                                                                                                                                                     |
|-------|-----------------------------------|---------|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Symbol                            | String  | Ticker symbol in upper case.                                                                                                  |
| 1     | Bid Price                         | double  | Current Bid Price                                                                                                             |                                                                                                                                                                                                                                                                                           |
| 2     | Ask Price                         | double  | Current Ask Price                                                                                                             |                                                                                                                                                                                                                                                                                           |
| 3     | Last Price                        | double  | Price at which the last trade was matched                                                                                     |
| 4     | Bid Size                          | int     | Number of shares for bid                                                                                                      | Units are "lots" (typically 100 sharesper lot)Note for NFL data this field can be 0 with a non-zero bid price which representing a bid size of less than 100 shares.                                                                                                                      |
| 5     | Ask Size                          | int     | Number of shares for ask                                                                                                      | See bid  size notes.                                                                                                                                                                                                                                                                      |
| 6     | Ask ID                            | char    | Exchange with the ask                                                                                                         |                                                                                                                                                         
| 7     | Bid ID                            | char    | Exchange with the bid                                                                                                         |
| 8     | Total Volume                      | long    | Aggregated shares traded throughout the day, including pre/post market hours.                                                 | Volume is set to zero at 7:28am ET.                                                                                                                                                                                                                                                       |
| 9     | Last Size                         | long    | Number of shares traded with last trade.                                                                                      | Units are shares.                                                                                                                                                                                                                                                                         |
| 10    | High Price                        | double  | Day's high trade price.                                                                                                       | According to industry standard, only regular session trades set the High and Low. If a stock does not trade in the regular session, high and low will be zero. High/Low reset to ZERO at 3:30am ET                                                                                        |
| 11    | Low Price                         | double  | Day's low trade price.                                                                                                        | See High Price notes.                                                                                                                                                                                                                                                                     |
| 12    | Close Price                       | double  | Previous day's closing price.                                                                                                 | Closing prices are updated from the DB at 3:30 AM ET.                                                                                                                                                                                                                                     |
| 13    | Exchange ID                       | char    | Primary "listing" Exchange.                                                                                                   | As long as the symbol is valid, this data is always present. This field is updated every time the closing prices are loaded from the DB.                                                                                                                                                  |
| 14    | Marginable                        | bool    | Approved by Fed and broker to enter margin debt.                                                                              |                                                                                                                                                                                                                                                                                           |
| 15    | Description                       | String  | Company, index, or fund name.                                                                                                 | Broadcasted at 7:29:50 AM ET.                                                                                                                                                                                                                                                             |
| 16    | Last ID                           | char    | Exchange where last trade was executed                                                                                        |
| 17    | Open Price                        | double  | Day's Open Price                                                                                                              | According to industry standard, only regular session trades set the open If a stock does not trade during the regular session, then the open price is 0. In the pre-market session, open is blank because pre-market session trades do not set the open. Open is set to ZERO at 3:30am ET |
| 18    | Net Change                        | double  |                                                                                                                               | LastPrice - ClosePrice If close is zero, change will be zero.                                                                                                                                                                                                                             |
| 19    | 52 Week High                      | double  | Highest price traded in the past 12 months, or 52 weeks.                                                                      | Calculated by merging intraday high (from fh) and 52-week high (from db)                                                                                                                                                                                                                  |
| 20    | 52 Week Low                       | double  | Lowest price traded in the past 12 months, or 52 weeks.                                                                       | Calculated by merging intraday low (from fh) and 52-week low (from db)                                                                                                                                                                                                                    |
| 21    | PE Ratio                          | double  | The price-to-earnings ratio. The P/E ratio equals the price of a share of stock, divided by the company's earnings per share. | Note that the price of a share of stock in the definition does update during the day so this field has the potential to stream. However, the current implementation uses the closing price and therefore does not stream throughout the day.                                              |
| 22    | Annual Dividend Amount            | double  | Annual Dividend Amount                                                                                                        |
| 23    | Dividend Yield                    | double  | Dividend Yield                                                                                                                |
| 24    | NAV                               | double  | Mutual Fund Net Asset Value                                                                                                   | Load various times after market close                                                                                                                                                                                                                                                     |
| 25    | Exchange Name                     | String  | Display name of exchange                                                                                                      |                                                                                                                                                                                                                                                                                           |
| 26    | Dividend Date                     | String  |                                                                                                                               |                                                                                                                                                                                                                                                                                           |
| 27    | Regular Market Quote              | boolean | Is last quote a regular quote                                                                                                 |                                                                                                                                                                                                                                                                                           |
| 28    | Regular Market Trade              | boolean | Is last trade a regular trade                                                                                                 |                                                                                                                                                                                                                                                                                           |
| 29    | Regular Market Last Price         | double  | Only records regular trade                                                                                                    |                                                                                                                                                                                                                                                                                           |
| 30    | Regular Market Last Size          | integer | Currently realize/100, only records regular trade                                                                             |                                                                                                                                                                                                                                                                                           |
| 31    | Regular Market Net Change         | double  | RegularMarketLastPrice - ClosePrice                                                                                           |                                                                                                                                                                                                                                                                                           |
| 32    | Security Status                   | String  | Indicates a symbol's current trading status                                                                                   | Normal, Halted, Closed                                                                                                                                                                                                                                                                    |
| 33    | Mark Price                        | double  | Mark Price                                                                                                                    |                                                                                                                                                                                                                                                                                           |
| 34    | Quote Time in Long                | Long    | Last time a bid or ask updated in milliseconds since Epoch                                                                    | The difference, measured in milliseconds, between the time an event occurs and midnight, January 1, 1970 UTC.                                                                                                                                                                             |
| 35    | Trade Time in Long                | Long    | Last trade time in milliseconds since Epoch                                                                                   | The difference, measured in milliseconds, between the time an event occurs and midnight, January 1, 1970 UTC.                                                                                                                                                                             |
| 36    | Regular Market Trade Time in Long | Long    | Regular market trade time in milliseconds since Epoch                                                                         | The difference, measured in milliseconds, between the time an event occurs and midnight, January 1, 1970 UTC.                                                                                                                                                                             |
| 37    | Bid Time                          | long    | Last bid time in milliseconds since Epoch                                                                                     | The difference, measured in milliseconds, between the time an event occurs and midnight, January 1, 1970 UTC.                                                                                                                                                                             |
| 38    | Ask Time                          | long    | Last ask time in milliseconds since Epoch                                                                                     | The difference, measured in milliseconds, between the time an event occurs and midnight, January 1, 1970 UTC.                                                                                                                                                                             |
| 39    | Ask MIC ID                        | String  | 4-chars Market Identifier Code                                                                                                |                                                                                                                                                                                                                                                                                           |
| 40    | Bid MIC ID                        | String  | 4-chars Market Identifier Code                                                                                                |                                                                                                                                                                                                                                                                                           |
| 41    | Last MIC ID                       | String  | 4-chars Market Identifier Code                                                                                                |                                                                                                                                                                                                                                                                                           |
| 42    | Net Percent Change                | double  | Net Percentage Change                                                                                                         | NetChange / ClosePrice * 100                                                                                                                                                                                                                                                              |
| 43    | Regular Market Percent Change     | double  | Regular market hours percentage change                                                                                        | RegularMarketNetChange / ClosePrice * 100                                                                                                                                                                                                                                                 |
| 44    | Mark Price Net Change             | double  | Mark price net change                                                                                                         | 7.97                                                                                                                                                                                                                                                                                      |
| 45    | Mark Price Percent Change         | double  | Mark price percentage change                                                                                                  | 4.2358                                                                                                                                                                                                                                                                                    |
| 46    | Hard to Borrow Quantity           | integer |                                                                                                                               | -1 = NULL<br>>= 0 is valid quantity                                                                                                                                                                                                                                                       |
| 47    | Hard To Borrow Rate               | double  |                                                                                                                               | null = NULL<br>valid range = -99,999.999 to +99,999.999                                                                                                                                                                                                                                   |
| 48    | Hard to Borrow                    | integer |                                                                                                                               | -1 = NULL<br>1 = true<br>0 = false                                                                                                                                                                                                                                                        |
| 49    | shortable                         | integer |                                                                                                                               | -1 = NULL<br>1 = true<br>0 = false                                                                                                                                                                                                                                                        |
| 50    | Post-Market Net Change            | double  | Change in price since the end of the regular session (typically 4:00pm)                                                       | PostMarketLastPrice - RegularMarketLastPrice                                                                                                                                                                                                                                              |
| 51    | Post-Market Percent Change        | double  | Percent change in price since the end of the regular session (typically 4:00pm)                                               | PostMarketNetChange / RegularMarketLastPrice * 100                                                                                                                                                                                                                                        |
-->

### Level one options  
> `streamer.send(streamer.level_one_options(keys, fields))`  
> Key examples: "AAPL&nbsp;&nbsp;240517P00190000", "AAPL&nbsp;&nbsp;251219C00200000"   
>> Key format: Underlying Symbol (6 chars including spaces) + Expiration (6 chars) + Call/Put (1 char) + Strike Price (5+3=8 chars)  
>> Expiration is in YYMMDD format.

### Level one futures  
> `streamer.send(streamer.level_one_futures(keys, fields))`  
> Key examples: "/ESF24", "/GCG24", "/ES"
>> Key format: '/' + 'root symbol' + 'month code' + 'year code'   
>> Month code is 1 character: (F: Jan, G: Feb, H: Mar, J: Apr, K: May, M: Jun, N: Jul, Q: Aug, U: Sep, V: Oct, X: Nov, Z: Dec)   
>> Year code is 2 characters (i.e. 2024 = 24)

### Level one futures options   
> `streamer.send(streamer.level_one_futures_options(keys, fields))`  
> Key examples: "./OZCZ23C565"
>> Key format: '.' + '/' + 'root symbol' + 'month code' + 'year code' + 'Call/Put (1 char)' + 'Strike Price'  
>> Month code is 1 character: (F: Jan, G: Feb, H: Mar, J: Apr, K: May, M: Jun, N: Jul, Q: Aug, U: Sep, V: Oct, X: Nov, Z: Dec)   
>> Year code is 2 characters (i.e. 2024 = 24)

### Level one forex   
> `streamer.send(streamer.level_one_forex(keys, fields))`  
> Key examples: "EUR/USD", "GBP/USD", "EUR/JPY", "EUR/GBP"

### NYSE book orders  
> `streamer.send(streamer.nyse_book(keys, fields))`  
> Key examples: "F", "NIO", "ACU"

### NASDAQ book orders  
> `streamer.send(streamer.nasdaq_book(keys, fields))`  
> Key examples: "AMD", "INTC"

### Options book orders  
> `streamer.send(streamer.options_book(keys, fields))`  
> Key examples: "AAPL&nbsp;&nbsp;240517P00190000", "AAPL&nbsp;&nbsp;251219C00200000"  
>> Key format: Underlying Symbol (6 chars including spaces) + Expiration (6 chars) + Call/Put (1 char) + Strike Price (5+3=8 chars)  
>> Expiration is in YYMMDD format.

### Chart equity  
> `streamer.send(streamer.chart_equity(keys, fields))`  
> Key examples: "AMD", "INTC"

### Chart futures  
> `streamer.send(streamer.chart_futures(keys, fields))`  
> Key examples: "/ESF24", "/GCG24"  
>> Key format: '/' + 'root symbol' + 'month code' + 'year code'   
>> Month code is 1 character: (F: Jan, G: Feb, H: Mar, J: Apr, K: May, M: Jun, N: Jul, Q: Aug, U: Sep, V: Oct, X: Nov, Z: Dec)   
>> Year code is 2 characters (i.e. 2024 = 24)

### Screener equity  
> `streamer.send(streamer.screener_equity(keys, fields))`  
> Key examples: "$DJI_PERCENT_CHANGE_UP_60", "NASDAQ_VOLUME_30"
>> Key format: `(PREFIX)_(SORTFIELD)_(FREQUENCY)`   
>> Prefix: $COMPX, $DJI, $SPX.X, INDEX_AL, NYSE, NASDAQ, OTCBB, EQUITY_ALL  
>> Sortfield: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME   
>> Frequency: 0 (all day), 1, 5, 10, 30 60  

### Screener options  
> `streamer.send(streamer.screener_options(keys, fields))`  
> Key examples: "OPTION_PUT_PERCENT_CHANGE_UP_60", "OPTION_CALL_TRADES_30"
>> Key format: `(PREFIX)_(SORTFIELD)_(FREQUENCY)`   
>> Prefix: OPTION_PUT, OPTION_CALL, OPTION_ALL  
>> Sortfield: VOLUME, TRADES, PERCENT_CHANGE_UP, PERCENT_CHANGE_DOWN, AVERAGE_PERCENT_VOLUME   
>> Frequency: 0 (all day), 1, 5, 10, 30 60  

### Account activity  
> `streamer.send(streamer.account_activity("Account Activity", "0,1,2,3"))`  
> There is only one key: "Account Activity" and the fields should be "0,1,2,3"  
> Only "SUBS"(default) and "UNSUBS" are supported for command.