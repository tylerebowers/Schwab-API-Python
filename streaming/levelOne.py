"""
The "fields" variable is sent as a list

"""
from streaming import utilities


def quote(keys, fields, command="SUBS"):
    return utilities.request(command, "QUOTE", keys, fields)


def option(keys, fields, command="SUBS"):
    return utilities.request(command, "OPTION", keys, fields)


def futures(keys, fields, command="SUBS"):
    return utilities.request(command, "LEVELONE_FUTURES", keys, fields)


def forex(keys, fields, command="SUBS"):
    return utilities.request(command, "LEVELONE_FOREX", keys, fields)


def futures_options(keys, fields, command="SUBS"):
    return utilities.request(command, "LEVELONE_FUTURES_OPTIONS", keys, fields)
