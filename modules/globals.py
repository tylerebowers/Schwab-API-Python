"""
##################################################
This file stores variables to be used between python files.
I have been thinking of renaming this file to cosmos.py.
__author__  = Tyler Bowers
##################################################
"""
# Credentials
consumerKey = "your key here"
callbackUrl = "https://localhost/"
accountUsername = "your account username"
accountNumber = "your account number"
# postgresql database credentials (not used yet)
usingDatabase = False
postgresql_host = "127.0.0.1"
postgresql_username = "username"
postgresql_password = "password"

# Below here are variables for functionality of the program; they don't need to be changed
# Token variables
accessToken = None
refreshToken = None
accessTokenDateTime = None
refreshTokenDateTime = None
authTokenTimeout = 30  # in minutes
# postgresql database
database = None
# threading variables
threads = []
# Streaming variables
streamerSubscriptionKey = None
streamerConnectionInfo = {}
userPrincipals = {}
requestId = 0
streamTerminal = None
streamIsActive = False
streamSubscriptions = {"QUOTE": {},
                       "OPTION": {},
                       "LEVELONE_FUTURES": {},
                       "LEVELONE_FOREX": {},
                       "LEVELONE_FUTURES_OPTIONS": {},
                       "ACCT_ACTIVITY": {},
                       "ACTIVES_NYSE": {},
                       "ACTIVES_OTCBB": {},
                       "ACTIVES_OPTIONS": {},
                       "FOREX_BOOK": {},
                       "FUTURES_BOOK": {},
                       "LISTED_BOOK": {},
                       "NASDAQ_BOOK": {},
                       "OPTIONS_BOOK": {},
                       "FUTURES_OPTIONS_BOOK": {},
                       "CHART_EQUITY": {},
                       "CHART_FUTURES": {},
                       "NEWS_HEADLINE": {},
                       "NEWS_HEADLINELIST": {},
                       "NEWS_STORY": {},
                       "TIMESALE_EQUITY": {},
                       "TIMESALE_FOREX": {},
                       "TIMESALE_FUTURES": {},
                       "TIMESALE_OPTIONS": {}}
