# This is a light documentation on the api side of the client

### First we must import the package
`import schwabdev`

### Then we must make a client to access the api.
`client = schwabdev.Client('your appkey', 'your app secret')`  

### It is recommended to call this function to keep the access token updated 
`client.update_tokens_auto()`

#### Documentation from here on will follow the structure of [schwab documentation](https://developer.schwab.com/products/trader-api--individual)
#### Remember that to access the return of the api call you must call `.json()`, however this does not check for errors.

## Accounts and Trading - Accounts

### Get account number and hashes for linked accounts
`client.account_linked()`  
Returns a list of linked accounts  
`[{'accountNumber': 'XXXX', 'hashValue': 'XXXX'}]`

### Get details for all linked accounts
`client.account_details_all()`  
Return details for all linked accounts (example output shortened)  
`[{'securitiesAccount': {'type': 'XXXX', 'accountNumber': 'XXXX', 'roundTrips': XXXX, 'isDayTrader': XXXX, ........}]`

### Get specific account positions (uses default account, can be changed)
`client.account_details(account_hash, fields="positions")`  
Return details for a specific linked account (example output shortened)   
`{'securitiesAccount': {'type': 'XXXX', 'accountNumber': 'XXXX', 'roundTrips': XXXX, 'isDayTrader': XXXX, ........}`

## Accounts and Trading - Orders 

### Get orders for a linked account
`client.account_orders(account_hash, 3000, datetime.utcnow() - timedelta(days=30), datetime.utcnow())`  
Returns up to 3000 orders from the account tied to account_hash from the previous 30 days up until now

### Place an order
Orders have a specific format, there are examples in schwab documentation   
`client.order_place(account_hash, order_obj)`  
We can get the order id by checking the headers  
`order_id = resp.headers.get('location', '/').split('/')[-1]`  
If order is immediately filled then the id might not be returned

### Get specific order details
For the account tied to account_hash get the details for order_id  
`print(client.order_details(account_hash, order_id)`

### Cancel specific order
For the account tied to account_hash cancel order_id  
`client.order_cancel(account_hash, order_id)`

### Replace a specific order
For the account tied to account_hash replace order_id with order_obj  
`client.order_replace(account_hash, orderID, order_obj)`

### Get account orders for all linked accounts
`client.account_orders_all(3000, datetime.utcnow() - timedelta(days=30), datetime.utcnow())`  
Returns up to 3000 orders from all linked accounts from the previous 30 days up until now

### preview order (not implemented by Schwab yet)
`#client.order_preview(account_hash, orderObject)`

## Accounts and Trading - Transactions

### Get all transactions for an account
`client.transactions(account_hash, datetime.utcnow() - timedelta(days=30), datetime.utcnow(), "TRADE")`

### Get details for a specific transaction
`client.transaction_details(account_hash, transactionId)`

## Accounts and Trading - UserPreference

### Get user preferences for an account, includes streaming information
`client.preferences()`

## Market Data - Quotes

### Get a list of quotes
`client.quotes(["AAPL", "AMD"])`  
`client.quotes("AAPL","AMD")`

### Get a single quote
`client.quote("INTC")`

## Market Data - Options Chains

### Get an option chain
`client.option_chains("AAPL")`

## Market Data - Options Expiration Chain

### Get an option expiration chain
`client.option_expiration_chain("AAPL")`

## Market Data - PriceHistory 

### Get price history for a symbol
`client.price_history("AAPL")`

## Market Data - Movers

### Get movers for an index
`client.movers("$DJI")`

## Market Data - MarketHours

### Get market hours for a symbol
`client.market_hours(["equity", "option"])`  
`client.market_hours("equity,option")`

### Get market hours for a market
`client.market_hour("equity")`

## Market Data - Instruments

### Get instruments for a symbol
`client.instruments("AAPL", "fundamental")`

### Get instruments for a cusip
`client.instrument_cusip("037833100")`