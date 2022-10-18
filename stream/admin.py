import json
import urllib
from modules import globals
from datetime import datetime
from streaming import utilities


def loginRequest(qosLevel=2):
    globals.requestId += 1
    credentialsDictionary = {
        "userid": globals.userPrincipals.get("accounts")[0].get("accountId"),
        "token": globals.streamerConnectionInfo.get("token"),
        "company": globals.userPrincipals.get("accounts")[0].get("company"),
        "segment": globals.userPrincipals.get("accounts")[0].get("segment"),
        "cddomain": globals.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
        "usergroup": globals.streamerConnectionInfo.get("userGroup"),
        "accesslevel": globals.streamerConnectionInfo.get("accessLevel"),
        "authorized": "Y",
        "acl": globals.streamerConnectionInfo.get("acl"),
        "timestamp": int(datetime.timestamp(
            datetime.strptime(globals.streamerConnectionInfo.get('tokenTimestamp'), "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
        "appid": globals.streamerConnectionInfo.get("appId")
    }
    parameters = {"credential": urllib.parse.urlencode(credentialsDictionary),
                  "token": globals.streamerConnectionInfo.get("token"),
                  "version": "1.0",
                  "qoslevel": qosLevel
                  }
    request = {"requests": [utilities.basicRequest(service="ADMIN", command="LOGIN", parameters=parameters)]}
    return json.dumps(request)


def logoutRequest():
    globals.requestId += 1
    request = {
        "requests": [utilities.basicRequest(service="ADMIN", command="LOGOUT", parameters={})]}
    return json.dumps(request)


def qosRequest(qosLevel):
    globals.requestId += 1
    request = {
        "requests": [utilities.basicRequest(service="ADMIN", command="QOS", parameters={"qoslevel": qosLevel})]}
    return json.dumps(request)