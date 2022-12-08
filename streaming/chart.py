from streaming import utilities


def equity(keys, fields):
    return utilities.SUBS("CHART_EQUITY", keys, fields)


def futures(keys, fields):
    return utilities.SUBS("CHART_FUTURES", keys, fields)


# def futuresHistory(keys, fields):