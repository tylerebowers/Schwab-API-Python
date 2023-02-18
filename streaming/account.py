"""
ACCT_ACTIVITY
"""
from streaming import utilities


def activity(keys, fields, command="SUBS"):
    return utilities.request(command, "ACCT_ACTIVITY", keys, fields)
