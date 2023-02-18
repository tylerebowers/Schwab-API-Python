from streaming import utilities


def equity(keys, fields, command="SUBS"):
    return utilities.request(command, "TIMESALE_EQUITY", keys, fields)


def forex(keys, fields, command="SUBS"):
    return utilities.request(command, "TIMESALE_FOREX", keys, fields)


def futures(keys, fields, command="SUBS"):
    return utilities.request(command, "TIMESALE_FUTURES", keys, fields)


def options(keys, fields, command="SUBS"):
    return utilities.request(command, "TIMESALE_OPTIONS", keys, fields)
