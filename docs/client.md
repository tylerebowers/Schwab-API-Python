# Using the Client

The client is used to make api calls and start streaming data from the Schwab API.  
In order to use all api calls you must have both "APIs" added to your app, both "Accounts and Trading Production" and "Market Data Production"

It is recommended to store your app keys and app secret in a dot-env file `.env` especially if you are using a git repo.
With a github repo you can include `*.env` and `tokens.json` in the `.gitignore` file to stop your credentials from getting commited. 

Making a client is as simple as:
```py
import schwabdev

client = schwabdev.Client(app_key, app_secret)
```
And from here on "client" can be used to make api calls via `client.XXXX()`, all calls are outlined in `examples/api_demo.py` and `docs/api.md`.  
Now lets look at all of the parameters that can be passed to the client constructor:
> Syntax: `client = schwabdev.Client(app_key, app_secret, callback_url="https://127.0.0.1", tokens_file="tokens.json", timeout=5, verbose=True, update_tokens_auto=True)`
> * Param app_key(str): app key to use, 32 chars long.  
> * Param app_secret(str): app secret to use, 16 chars long.  
> * Param callback_url(str): callback url to use, must be https and not end with a slash "/".  
> * Param tokens_file(str): path to tokens file.  
> * Param timeout(int): timeout to use when making requests.  
> * Param verbose(bool): verbose (print extra information that isn't neccessary).  
> * Param update_tokens_auto(bool): thread that checks/updates the access token and refresh token (requires user input for refresh token).

Schwabdev now uses the logging module to log/print information, warnings and errors. You can change the level of logging by setting `logging.basicConfig(level=logging.XXXX)` where `XXXX` is the level of logging you want such as `INFO` or `WARNING`.

Schwabdev can also capture the callback urls, so you dont have to copy/paste. If you use a callback url such as `https://127.0.0.1:7777` then Schwabdev will listen on port 7777 and capture the callback url after you have signed in your account. You may get a warning "net::ERR_CERT_AUTHORITY_INVALID" since it is a self-signed certificate but this is not an issue, just click "Advanced" -> "Proceed to ..." to send the code to Schwabdev (usually only warns the first time). If you still want to copy/paste then remove the port from your callback url.

The Schwab API uses two tokens to use the api:
* Refresh token - valid for 7 days, used to "refresh" the access token.
* Access token - valid for 30 minutes, used in all api calls.   

If you want to access the access or refresh tokens you can call `client.tokens.access_token` or `client.tokens.refresh_token`.  
The access token can be easily updated/refreshed assuming that the refresh token is valid, getting a new refresh token, however, requires user input. It is recommended force-update the refresh token during weekends so it is valid during the week, this can be done with the call: `client.tokens.update_tokens(force=True)`, or by changing the date in `tokens.json`.

If you want to manually control token updating then you can set `update_tokens_auto=False` during client creation and have your own thread that updates the tokens. Look at the `client.tokens.update_tokens(...)` method (in tokens.py). Essentially you want to keep the access token and refresh tokens valid, you can probably use `client.tokens.update_access_token` directly and make your own `client.tokens.update_refresh_token` function. Keep in mind that Schwabdev can also listen on a port and capture the callback url, you could use a different port for the callback and let Schwabdev listen on it.

## Common Issues

> Problem: unauthorized error `{'errors': [{'id': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX', 'status': 401, 'title': 'Unauthorized', 'detail': 'Client not authorized'}]}`  
> Cause: You do not have access to both APIs and are attempting to access one that you have not added to your app.  
> Fix: Add both APIs "Accounts and Trading Production" and "Market Data Production" to your app.  
> Cause: The access token is expired, sometimes Schwab invalidates tokens when they make backend changes.  
> Fix: Manually update access token by changing the date in `tokens.json` or update both tokens by calling `client.tokens.update_tokens(force=True)`

> Problem: Trying to sign into account and get error message: "We are unable to complete your request. Please contact customer service for further assistance."  
> Problem: "Whitelabel Error Page This application has no configured error view, so you are seeing this as a fallback." (status=500)  
> Fix: Your app is "Approved - Pending", you must wait for status "Ready for Use".  
> Note: Or you *could* have an account type that is not supported by the Schwab API.

> Problem: SSL: CERTIFICATE_VERIFY_FAILED - self-signed certificate in certificate chain error when connecting to streaming server  
> Fix: For MacOS you must run the python certificates installer: `open /Applications/Python\ 3.12/Install\ Certificates.command`

> Problem: Issues with option contracts in api calls or streaming:  
> Fix: You are likely not following the format for option contracts.   
> Option contract format: Symbol (6 characters including spaces!) | Expiration (6 characters) | Call/Put (1 character) | Strike Price (5+3=8 characters)

> Problem: "{"error":"unsupported_token_type","error_description":"400 Bad Request: \"{\"error_description\":\"Exception while authenticating refresh token..."  
> Problem: "Could not get new access token (1 of 3)." (or x of 3 etc)  
> Cause: Your refresh token is invalid (maybe you created a new refresh token on a different machine).  
> Fix: Manually update refresh token by changing the date in `tokens.json` or by calling `client.tokens.update_tokens(force=True)`

> Problem: "can't register atexit after shutdown"  
> Cause: The main thread dies before the stream thread starts  
> Fix: Add a delay after starting or sending a request, something to let the stream thread start up before the main thread closes.

> Problem: API calls throwing errors despite access token and refresh token being valid / not expired.  
> Fix: Manually update refresh / access tokens by calling `client.tokens.update_tokens(force=True)`; You can also delete the tokens.json file.

> Problem: Streaming ACCT_ACTIVITY yields no responses.   
> Fix: This is a known issue on Schwab's end.

> Problem: After signing in, you get a "Access Denied" web page.  
> Fix: Your callback url is likely incorrect due to a slash "/" at the end.

> Problem: App Registration Error  
> Fix: email Schwab (traderapi@schwab.com)

> Problem: Issue in streaming with websockets - "Unsupported extension: name = permessage-deflate, params = []"  
> Cause: You are using a proxy that is blocking streaming or your DNS is not correctly resolving.  
> Fix: Change DNS servers (Google's are known-working) or change/bypass proxy.

> Problem: "{'fault': {'faultstring': 'Body buffer overflow', 'detail': {'errorcode': 'protocol.http.TooBigBody'}}}"  
> Cause: The call that you made exceeds the amount of data that can be returned.  
> Example: The call `print(client.option_chains("$SPX").json())` returns too much data and will exceed the buffer size.  
> Fix: Add additional parameters to limit the amount of data returned.

> Problem: refresh token expiring in 7 days is too short. - I know. 




