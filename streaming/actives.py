"""
ACTIVES_NASDAQ

ACTIVES_NYSE

ACTIVES_OTCBB

ACTIVES_OPTIONS
"""
from streaming import utilities


def nasdaq(keys, fields):
    return utilities.SUBS("ACTIVES_NASDAQ", keys, fields)


def nyse(keys, fields):
    return utilities.SUBS("ACTIVES_NYSE", keys, fields)


def otcbb(keys, fields):
    return utilities.SUBS("ACTIVES_OTCBB", keys, fields)


def options(keys, fields):
    return utilities.SUBS("ACTIVES_OPTIONS", keys, fields)
