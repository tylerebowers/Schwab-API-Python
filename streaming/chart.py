from streaming import utilities


def equity(keys, fields, command="SUBS"):
    return utilities.request(command, "CHART_EQUITY", keys, fields)


def futures(keys, fields, command="SUBS"):
    return utilities.request(command, "CHART_FUTURES", keys, fields)

# def futuresHistory(keys, fields, command="SUBS"):
