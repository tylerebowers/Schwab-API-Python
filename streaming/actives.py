"""
ACTIVES_NASDAQ

ACTIVES_NYSE

ACTIVES_OTCBB

ACTIVES_OPTIONS
"""
from streaming import utilities


def nasdaq(keys, fields, command="SUBS"):
    return utilities.request(command, "ACTIVES_NASDAQ", keys, fields)


def nyse(keys, fields, command="SUBS"):
    return utilities.request(command, "ACTIVES_NYSE", keys, fields)


def otcbb(keys, fields, command="SUBS"):
    return utilities.request(command, "ACTIVES_OTCBB", keys, fields)


def options(keys, fields, command="SUBS"):
    return utilities.request(command, "ACTIVES_OPTIONS", keys, fields)
