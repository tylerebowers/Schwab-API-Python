import schwabdev
from dotenv import load_dotenv
import os


def main():
    # place your app key and app secret in the .env file
    load_dotenv()  # load environment variables from .env file

    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))
    streamer = client.stream

    # a "terminal emulator" to play with the API
    print("\nTerminal emulator - enter python code to execute.")
    while True:
        try:
            entered = input(">")
            exec(entered)
            print("[Succeeded]")
        except Exception as error:
            print("[ERROR]")
            print(error)


if __name__ == '__main__':
    print("Welcome to the unofficial Schwab interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    main()  # call the user code above
