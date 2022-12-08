"""
The "fields" variable is sent as a list

"""
from streaming import utilities


def quote(keys, fields):
    return utilities.SUBS("QUOTE", keys, fields)


def option(keys, fields):
    return utilities.SUBS("OPTION", keys, fields)


def futures(keys, fields):
    return utilities.SUBS("LEVELONE_FUTURES", keys, fields)


def forex(keys, fields):
    return utilities.SUBS("LEVELONE_FOREX", keys, fields)


def futures_options(keys, fields):
    return utilities.SUBS("LEVELONE_FUTURES_OPTIONS", keys, fields)


