# Schwab-API-Python 
This is an unofficial python program to access the Schwab api.    
You will need a Schwab developer account [here](https://beta-developer.schwab.com/).        
Join the [Discord group](https://discord.gg/m7SSjr9rs9)


## Quick setup
1. Python version 3.11 or higher is recommended.     
2. `pip3 install requests`    
2. Review keys in modules/universe.py specifically tokens.appKey, tokens.appSecret (and callbackUrl if applicable)
3. Start by running from main.py

## What can this program do?
 - Authenticate and access the api
 ### TBD 
 - Functions for all api functions (25% complete)
 - Auto "access token" updates (90% complete) 
 - Stream all data types (not started) (waiting on schwab)


## Usage and Design
This python client makes working with the TD/Schwab api easier.    
The idea is to make an easy to understand, organized, and highly-automatic interface for the api.   
Below is a light documentation on how it works, python is pseudocode-esk so if you are confused just read the code and follow the functions. 

### Organization

The modules folder contains code for main operations:     
 - `api.py` contains functions relating to api calls, requests, and automatic token checker daemons.
 - `tokens.txt` contains api tokens as well as dates for when they expire.
 - `universe.py` contains universal variables that need to be accessed across many functions such as credentials, preferences, tokens, etc.


### Initialization
main.py initializes below main() in `if __name__ == '__main__':` each call is described below:
 1. `api.initialize()` # This calls a function that checks if the access or refresh token need to be re-authenticated. It also adds the tokens and expire times to variables in `universe.py`


