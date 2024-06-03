import schwabdev
from dotenv import load_dotenv
import os


def main():
    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))
    client.update_tokens_auto()  # update tokens automatically (except refresh token)

    client.stream.start()

    # these two do the same thing
    client.stream.send(client.stream.basic_request("CHART_EQUITY", "SUBS", parameters={"keys": "AMD,INTC", "fields": "0,1,2,3,4,5,6,7,8"}))
    client.stream.send(client.stream.chart_equity("AMD,INTC", "0,1,2,3,4,5,6,7,8"))

    client.stream.send(client.stream.chart_futures("ES,GC", "0,1,2,3,4,5,6,7,8"))
    client.stream.send(client.stream.level_one_quote("AMD", "0,1,2,3,4,5,6,7,8"))
    #client.stream.send(client.stream.level_one_option("", "0,1,2,3,4,5,6,7,8"))
    client.stream.send(client.stream.level_one_futures("ES", "0,1,2,3,4,5,6,7,8"))
    client.stream.send(client.stream.level_one_forex("EUR/USD", "0,1,2,3,4,5,6,7,8"))
    #client.stream.send(client.stream.level_one_futures_options("", "0,1,2,3,4,5,6,7,8"))

    # stop the stream (uncomment if you start the stream below)
    # client.stream.stop() # this will stop the stream but it is a bit "hacky"


if __name__ == '__main__':
    print("Welcome to the unofficial Schwab interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    load_dotenv()
    main()  # call the user code above
