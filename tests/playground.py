import schwabdev
from dotenv import load_dotenv
import os


def main():
    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))
    client.update_tokens_auto()  # update tokens automatically (except refresh token)

    # a "terminal emulator" to play with the API
    history = []
    print("\nTerminal emulator")
    print("Enter code to execute.")
    while True:
        try:
            entered = input("Enter something to execute:\n")
            if entered == "":
                print(history[-1])
                exec(history[-1])
                history.append(history[-1])
            else:
                exec(entered)
                history.append(entered)
            print(" ^^^^[succeeded]^^^^ ")
        except Exception as error:
            print(" ^^^^[ERROR]^^^^ ")
            print(error)


if __name__ == '__main__':
    print("Welcome to the unofficial Schwab interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    load_dotenv()
    main()  # call the user code above
