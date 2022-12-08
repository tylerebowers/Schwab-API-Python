import urllib
from modules import globals
from datetime import datetime
from streaming import utilities


def login(qosLevel=2):
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
    return utilities.basicRequest(service="ADMIN", command="LOGIN", parameters=parameters)


def logout():
    return utilities.basicRequest(service="ADMIN", command="LOGOUT")


def qos(qosLevel):
    return utilities.basicRequest(service="ADMIN", command="QOS", parameters={"qoslevel": qosLevel})
