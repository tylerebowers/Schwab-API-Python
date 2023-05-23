# TD-Ameritrade-API-Python-Client  
In 2023 TD is moving to schwab so some significant changes may be needed soon.       
Next update planned for release in June 2023.
Join the [Discord group](https://discord.gg/m7SSjr9rs9)

## Quick setup
1. `pip3 install requests window-terminal websockets pandas SQLAlchemy`    
2. Review preferences and credentials in modules/universe.py (specifically consumerKey, accountNumber (for streaming), and callbackUrl)
3. Start by running from main.py


## What can this program do?
 - Access all api funtions
 - Stream all data types
 - Auto access Token updates
 - Auto Stream starting/stopping
 - Auto create database and dataframe tables
 - Auto add database and dataframe data
 - Dynamically create and submit orders
 - Protect limit orders that are far over market price
 ### TBD
 - Algorithmic / Probability paper money (25% complete)
 - Statistics and analysis functions (not started)


## Usage and Design
This python client makes working with the TD/Schwab api easier.    
The idea is to make an easy to understand, highly-organized, and highly automatic client for the api.   
Below is a light documentation on how it works, python is pseudocode-esk so if you are confused just read the code and follow the functions. 

### Organization

The modules folder contains code for main opperations:     
 - `api.py` contains functions relating to api calls, requests, and automatic token checker daemons, works with `apis/`.
 - `database.py` contains functions for Postgresql and Pandas Dataframes. Note that adding data is normally automatic.
 - `order.py` contains functions for building and submitting orders.
 - `stream.py` handles streaming and stream data, it works closely with database and `streaming/`.
 - `tokens.txt` contains api tokens as well as dates for when they expire.
 - `universe.py` contains universal variables that need to be accessed across many functions such as credentials, preferences, tokens, DB connections, dataframes, data aliases.
 - The folders apis and streaming both contain supporting code which is organized acording to TD's Docs.  
 - Both apis and streaming contain a utilities.py file which contains functions shared across internal files, they are not to be imported. 

### API requests
 - With api calls for example, `apis/instruments.py` contains the functions `searchInstruments` and `getInstrument`; this is 1-1 to [TD's Docs](https://developer.tdameritrade.com/instruments/apis). Then in main.py these apis can be called via `from apis import instruments`... and specific functions via `instruments.getInstrument(...)`; When calling these functions api keys and access tokens are handled automatically, so in this case you only need to pass in the [CUSIP](https://developer.tdameritrade.com/instruments/apis/get/instruments/%7Bcusip%7D). Try this: `print(instruments.getInstrument('AMD'))`. 
 - Another example is `from apis import quotes` then `quotes.getQuote("AMD")`. Note that it is not recomended to repeatably use api requests to get market data, rather, use streaming to get continous data.

### Streaming and dataframes.
 - Chekc the initialization section to see how the stream can be started manually and automatically. 
 - With streaming we can send SUB requests after the stream has started:  `stream.send(levelOne.quote(["AMD", "INTC"], [0, 1, 2, 3, 4, 5, 8, 9, 24]))` Note that you must always send `0`. When the above line is executed several things happen: if you are using a database then a table is automatically created (no overwirite), and a dataframe is created in universe.py. While the stream is running both of these locations (DB and DF) have stream data automatically added to them. The fields that you requested 0,1,2,3, etc... have name aliases which can be found in `universe.stream.fieldAliases`.
 - To access a dataframe (as created above) use `universe.dataframes["QUOTE"]["AMD"]` (and print()) and you will get an output like the screenshot below.
 - Dataframes can also be disabled in `modules/universe.preferences`

### Database (Postgresql)
 - Databases can be disabled in `modules/universe.preferences` if you only want to use dataframes.
 - To setup the database run `DBSetup()` in main, it only needs to be run once. (make sure that the database is connected too)  
 - To get tables from the database use `DBGetTable(...)`, it needs a service ("QUOTE", etc) and a ticker symbol minimum. To select from a certain time period you have two options, either specifying a lowerbound ((optional) and upperbound) or by using backwards. A lowerbound does exactly what it implies and can be an epoch in seconds or a datetime object. Backwards will go "backwards" from the current time for a specified number of seconds, ie if you want to get the previous 12 hours of data then use `backwards=43200`.
 - Please view the tutorial part 3 (on my youtube cahanel) for more information.

### Orders   
 - The orders module in `modules/order.py` is also simple to use. We can both dynamically create and use preset orders. For preset orders it is as simple as `order.submit(order.presets.equity.buyLimited("AMD", 1, 90))` (limit-buy 1x AMD at a price of $90.00), or `order.submit(order.presets.equity.buyMarket("AMD", 1))` (market-buy 1x AMD). Dynamic order creation is shown in main.py.
 - Orders are also protected, meaning that if your order's price is significantly over market price then the order will not be sent, the threshold/limit can be set in `modules/universe.preferences.orderDeltaLimit`.
 - With limit orders a predictive model evaluates the execution probability by using the ask/bid ratio and price difference percentage, this equation can be seen in the appendix (below)
 - Why not protect an order? - a protected order is SLOW because it has to make an additional api request to get the current price of the stock, if you need a quick way to submit an order use `quickSubmit(...)`.
 - An Order object can also be filled with the output of accountsAndTrading.getOrdersByPath(): this function returns a list of all current orders for your account, so you would want to make Order objects in a loop or just select the one you want. The example here: `anOrder = order.Order(accountsAndTrading.getOrdersByPath()[0])` gets the first order in your TD account and creates an Order object in the variable `anOrder`.

### Initialization
main.py initializes below main() in `if __name__ == '__main__':` each call is described below:
 1. `api.initialize()` # This calls a function that checks if the access or refresh token need to be re-authenticated. It also addes the tokens and expire times to `universe.py`
 2. `if universe.preferences.usingDatabase: database.DBConnect()` # This connects the database using the credentials that you supplied in `universe.credentials`, it assumes that it is a postgresql database. It also loads database connection variables into `universe.py`.
 3. `api._checkTokensDaemon()` # This appends a thread to the universe threads. This thread automatically updates the access token if needed. It is highly recomended to check on the program every 85 days to check the refresh token though the expire time for the refresh token is printed every time on startup.
 4. `stream.startAutomatic()` # this appends a thread to main which will automatically start the stream in market hours and stop the stream outside of market hours. It also starts the streaming window.
 5. `stream.startManual()` # this appends a thread to main which starts the stream immediately, it is mainly intended for testing. It also starts the streaming window.
 6. `universe.threads.append(threading.Thread(target=main))` # this adds main() to the list of threads to start.
 7. The `for` loops start and join the threads.


## Screenshots
Example of streaming usage:   
![Picture of streaming](demos/streaming.jpg)

Example of API usage:   
![Picture of api calls](demos/apiCalls.jpg)

Example of Dataframe (DF) usage:   
![Picture of dataframe](demos/dataframe.png)


## Appendix
Execution probability function {s=askSize / bidSize, x=(myPrice - marketPrice) / marketPrice}:   
![Picture of execution probability function](demos/executionProbability.jpg)
