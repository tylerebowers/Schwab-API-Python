from streaming import utilities


# there aren't any examples in TD's documentation yet, but there is a way to get book data

def forex(keys, fields):
    return utilities.SUBS("FOREX_BOOK", keys, fields)


def futures(keys, fields):
    return utilities.SUBS("FUTURES_BOOK", keys, fields)


def listed(keys, fields):
    return utilities.SUBS("LISTED_BOOK", keys, fields)


def nasdaq(keys, fields):
    return utilities.SUBS("NASDAQ_BOOK", keys, fields)


def options(keys, fields):
    return utilities.SUBS("OPTIONS_BOOK", keys, fields)


def futures_options(keys, fields):
    return utilities.SUBS("FUTURES_OPTIONS_BOOK", keys, fields)
