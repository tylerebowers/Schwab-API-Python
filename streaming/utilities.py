from modules import globals


def basicRequest(**kwargs):
    globals.requestId += 1
    args = ["service", "requestid", "command", "account", "source", "parameters"]
    request = {"requestid": globals.requestId, "account": globals.userPrincipals.get("accounts")[0].get("accountId"),
               "source": globals.streamerConnectionInfo.get("appId")}
    for key, value in kwargs.items():
        if key in args: request[key] = value
    return request


def listToString(ls):
    return ",".join(map(str, ls))
