from streaming import utilities


# there aren't any examples in TD's documentation yet, but there is a way to get book data

def forex(keys, fields, command="SUBS"):
    return utilities.request(command, "FOREX_BOOK", keys, fields)


def futures(keys, fields, command="SUBS"):
    return utilities.request(command, "FUTURES_BOOK", keys, fields)


def listed(keys, fields, command="SUBS"):
    return utilities.request(command, "LISTED_BOOK", keys, fields)


def nasdaq(keys, fields, command="SUBS"):
    return utilities.request(command, "NASDAQ_BOOK", keys, fields)


def options(keys, fields, command="SUBS"):
    return utilities.request(command, "OPTIONS_BOOK", keys, fields)


def futures_options(keys, fields, command="SUBS"):
    return utilities.request(command, "FUTURES_OPTIONS_BOOK", keys, fields)
