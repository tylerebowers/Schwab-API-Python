"""
This file stores variables to be used between python files.
"""
# Credentials (These you need to change to your own)
consumerKey = "your consumer key"
callbackUrl = "https://localhost/"
accountUsername = "your TD account username"
accountNumber = "your TD account number"
# Token variables
accessToken = None
refreshToken = None
authTokenTimeout = 30  # in minutes
# Streaming variables
streamerSubscriptionKey = None
streamerConnectionInfo = {}
userPrincipals = {}
requestId = 0
terminalOutput = True  # for outputting the stream to a terminal
