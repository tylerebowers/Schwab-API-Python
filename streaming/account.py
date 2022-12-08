"""
ACCT_ACTIVITY
"""
from streaming import utilities


def activity(keys, fields):
    return utilities.SUBS("ACCT_ACTIVITY", keys, fields)
