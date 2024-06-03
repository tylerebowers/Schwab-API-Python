# Using the Client

It is recommended to store your app keys and app secret in a dot-env file `.env`.   
Inside you will need:
````py
app_key = "Your app key"
app_secret = "Your app secret"
callback_url = "https://127.0.0.1" #This line is optional
````
With a github repo you can include `*.env` in the `.gitignore` file to stop your credentials from getting commited. You may also want to include `tokens.json` in the `.gitignore` as it contains your tokens.

To get started with the api client:
````py
import schwabdev

client = schwabdev.Client("your app key", "your app secret", "Your callback url (optional)", "Location for tokens file (optional)")
````
If you are using a `.env` file for your keys:
````py
import schwabdev
from dotenv import load_dotenv
import os

load_dotenv()
client = schwabdev.Client(os.getenv("app_key"), os.getenv("app_secret"))
````
The Schwab API uses two tokens to use the api:
* Refresh token - valid for 7 days, used to "refresh" the access token.
* Access token - valid for 30 minutes, used in all api calls. 

The access token can be easily updated/refreshed assuming that the refresh token is valid, getting a new refresh token, however, requires user input.
The Function `client.update_tokens_auto()` will keep the access token updated by spawning a thread that checks the access token every minute. It also checks the refresh token and will present a prompt one day before expiry.

If you want to access the access or refresh tokens you can call `client.access_token` or `client.refresh_token`.

The api calls can be accessed via `client.XXXX()`, all calls are outlined in `tests/api_demo.py` or `docs/api.md`




