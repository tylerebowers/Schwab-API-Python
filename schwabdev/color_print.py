"""
This file is used to print colored text
Github: https://github.com/tylerebowers/Schwab-API-Python
"""

@staticmethod
def info(string, end="\n"): print(f"\033[92m{'[INFO]: '}\033[00m{string}", end=end)
@staticmethod
def warning(string, end="\n"): print(f"\033[93m{'[WARN]: '}\033[00m{string}", end=end)
@staticmethod
def error(string, end="\n"): print(f"\033[91m{'[ERROR]: '}\033[00m{string}", end=end)
@staticmethod
def user(string, end="\n"): print(f"\033[94m{'[USER]: '}\033[00m{string}", end=end)
@staticmethod
def input(string): return input(f"\033[94m{'[INPUT]: '}\033[00m{string}")
