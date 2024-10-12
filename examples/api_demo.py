"""
This file contains examples for every api call.
"""


import schwabdev
import datetime
from dotenv import load_dotenv
from time import sleep
import os


def main():
    # place your app key and app secret in the .env file
    load_dotenv()  # load environment variables from .env file

    # create client
    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'), verbose=True)

    print("\n\nAccounts and Trading - Accounts.")

    # get account number and hashes for linked accounts
    print("\nclient.account_linked().json()")
    linked_accounts = client.account_linked().json()
    print(linked_accounts)
    # this will get the first linked account
    account_hash = linked_accounts[0].get('hashValue')
    sleep(3)

    # get positions for linked accounts
    print("\nclient.account_details_all().json()")
    print(client.account_details_all().json())
    sleep(3)

    # get specific account positions (uses default account, can be changed)
    print("\nclient.account_details(account_hash, fields='positions').json()")
    print(client.account_details(account_hash, fields="positions").json())
    sleep(3)

    print("\n\nAccounts and Trading - Orders.")

    # get orders for a linked account
    print(
        "\nclient.account_orders(account_hash, datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30), datetime.datetime.now(datetime.timezone.utc)).json())",
        end="\n")
    print(
        client.account_orders(account_hash, datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
                              datetime.datetime.now(datetime.timezone.utc)).json())
    sleep(3)

    # place an order, get the details, then cancel it (uncomment to test)
    """
    order = {"orderType": "LIMIT",
             "session": "NORMAL",
             "duration": "DAY",
             "orderStrategyType": "SINGLE",
             "price": '10.00',
             "orderLegCollection": [
                 {"instruction": "BUY",
                  "quantity": 1,
                  "instrument": {"symbol": "INTC",
                                 "assetType": "EQUITY"
                                 }
                  }
             ]
             }
    resp = client.order_place(account_hash, order)
    print("\nclient.order_place(account_hash, order).json()")
    print(f"Response code: {resp}")
    # get the order ID - if order is immediately filled then the id might not be returned
    order_id = resp.headers.get('location', '/').split('/')[-1]
    print(f"Order id: {order_id}")
    sleep(3)

    # get specific order details
    print("\nclient.order_details(account_hash, order_id).json()")
    print(client.order_details(account_hash, order_id).json())
    sleep(3)

    # cancel specific order
    print("\nclient.order_cancel(account_hash, order_id).json()")
    print(client.order_cancel(account_hash, order_id))
    sleep(3)

    # replace specific order (no demo implemented)
    # print("\nclient.order_replace(account_hash, order_id, order)")
    # client.order_replace(account_hash, order_id, order)
    """

    # get up to 3000 orders for all accounts for the past 30 days
    print(
        "\nclient.account_orders_all(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30), datetime.datetime.now(datetime.timezone.utc)).json()",
        end="\n")
    print(client.account_orders_all(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
                                    datetime.datetime.now(datetime.timezone.utc)).json())
    sleep(3)

    # preview order (not implemented by Schwab yet)
    # print("\nclient.order_preview(account_hash, orderObject)")
    # client.order_preview(account_hash, orderObject)

    print("\n\nAccounts and Trading - Transactions.")

    # get all transactions for an account
    print(
        "\nclient.transactions(account_hash, datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30), datetime.datetime.now(datetime.timezone.utc),\"TRADE\").json()",
        end="\n")
    print(client.transactions(account_hash, datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
                              datetime.datetime.now(datetime.timezone.utc), "TRADE").json())
    sleep(3)

    # get details for a specific transaction (no demo implemented)
    # print("\nclient.transaction_details(account_hash, transactionId).json()")
    # print(client.transaction_details(account_hash, transactionId).json())

    print("\n\nAccounts and Trading - UserPreference.")

    # get user preferences for an account
    print("\nclient.preferences().json()")
    print(client.preferences().json())
    sleep(3)

    print("\n\nMarket Data - Quotes.")

    # get a list of quotes
    print("\nclient.quotes([\"AAPL\",\"AMD\"]).json()")
    print(client.quotes(["AAPL", "AMD"]).json())
    sleep(3)

    # get a single quote
    print("\nclient.quote(\"INTC\").json()")
    print(client.quote("INTC").json())
    sleep(3)

    print("\n\nMarket Data - Options Chains.")
    print("There is a lot to print so this is not shown, the demo code is commented out")
    # get an option chain
    # print("\nclient.option_chains(\"AAPL\").json()")
    # print(client.option_chains("AAPL").json())
    # Here is another example for SPX, note that if you call with just $SPX then you will exceed the buffer on Schwab's end hence the additional parameters to limit the size of return.
    # print(client.option_chains("$SPX", contractType="CALL", range="ITM").json())
    sleep(3)

    print("\n\nMarket Data - Options Expiration Chain.")

    # get an option expiration chain
    print("\nclient.option_expiration_chain(\"AAPL\").json()")
    print(client.option_expiration_chain("AAPL").json())
    sleep(3)

    print("\n\nMarket Data - PriceHistory.")
    # get price history for a symbol
    print("\nclient.price_history(\"AAPL\", \"year\").json()")
    print(client.price_history("AAPL", "year").json())
    sleep(3)

    print("\n\nMarket Data - Movers.")

    # get movers for an index
    print("\nclient.movers(\"$DJI\").json()")
    print(client.movers("$DJI").json())
    sleep(3)

    print("\n\nMarket Data - MarketHours.")

    # get marketHours for a symbol
    print("\nclient.market_hours([\"equity\",\"option\"]).json()")
    print(client.market_hours(["equity", "option"]).json())
    # print(client.market_hours("equity,option").json()) # also works
    sleep(3)

    # get marketHours for a market
    print("\nclient.market_hour(\"equity\").json()")
    print(client.market_hour("equity").json())
    sleep(3)

    print("\n\nMarket Data - Instruments.")

    # get instruments for a symbol
    print("\nclient.instruments(\"AAPL\", \"fundamental\").json()")
    print(client.instruments("AAPL", "fundamental").json())
    sleep(3)

    # get instruments for a cusip
    print("\nclient.instrument_cusip(\"037833100\").json()")
    print(client.instrument_cusip("037833100").json())  # 037833100 = AAPL
    sleep(3)


if __name__ == '__main__':
    print("Welcome to The Unofficial Schwab Python Wrapper!")
    print("Github: https://github.com/tylerebowers/Schwab-API-Python")
    print("API documentation: https://github.com/tylerebowers/Schwab-API-Python/blob/master/docs/api.md")
    print("Client documentation: https://github.com/tylerebowers/Schwab-API-Python/blob/master/docs/client.md")
    main()  # call the user code above
