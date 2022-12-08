from streaming import utilities


def equity(keys, fields):
    return utilities.SUBS("TIMESALE_EQUITY", keys, fields)


def forex(keys, fields):
    return utilities.SUBS("TIMESALE_FOREX", keys, fields)


def futures(keys, fields):
    return utilities.SUBS("TIMESALE_FUTURES", keys, fields)


def options(keys, fields):
    return utilities.SUBS("TIMESALE_OPTIONS", keys, fields)
