"""
This file stores variables to be used between python files and functions some
Github: https://github.com/tylerebowers/Schwab-API-Python
"""


class credentials:
    # Schwab account credentials
    appKey = "Your App Key"
    appSecret = "Your App Secret"
    callbackUrl = "https://127.0.0.1"
    accountUsername = ""
    accountNumber = ""
    encryptedId = ""


"""
Below here are variables for functionality of the program; they shouldn't be changed
"""

class tokens:
    refreshToken = None
    accessToken = None
    idToken = None
    refreshTokenDateTime = None
    accessTokenDateTime = None
    refreshTokenTimeout = 7 # in days
    accessTokenTimeout = 1800 # in seconds


class terminal:
    @staticmethod
    def info(string): print(f"\033[92m{'[INFO]: '}\033[00m{string}")
    @staticmethod
    def warning(string): print(f"\033[93m{'[WARN]: '}\033[00m{string}")
    @staticmethod
    def error(string): print(f"\033[91m{'[ERROR]: '}\033[00m{string}")
    @staticmethod
    def input(string): return input(f"\033[94m{'[INPUT]: '}\033[00m{string}")
    @staticmethod
    def user(string): print(f"\033[1;31m{'[USER]: '}\033[00m{string}")


