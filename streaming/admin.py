import urllib
from modules import universe
from datetime import datetime
from streaming import utilities


def login(qosLevel=2):
    credentialsDictionary = {
        "userid": universe.stream.userPrincipals.get("accounts")[0].get("accountId"),
        "token": universe.stream.connectionInfo.get("token"),
        "company": universe.stream.userPrincipals.get("accounts")[0].get("company"),
        "segment": universe.stream.userPrincipals.get("accounts")[0].get("segment"),
        "cddomain": universe.stream.userPrincipals.get("accounts")[0].get("accountCdDomainId"),
        "usergroup": universe.stream.connectionInfo.get("userGroup"),
        "accesslevel": universe.stream.connectionInfo.get("accessLevel"),
        "authorized": "Y",
        "acl": universe.stream.connectionInfo.get("acl"),
        "timestamp": int(datetime.timestamp(
            datetime.strptime(universe.stream.connectionInfo.get('tokenTimestamp'), "%Y-%m-%dT%H:%M:%S%z"))) * 1000,
        "appid": universe.stream.connectionInfo.get("appId")
    }
    parameters = {"credential": urllib.parse.urlencode(credentialsDictionary),
                  "token": universe.stream.connectionInfo.get("token"),
                  "version": "1.0",
                  "qoslevel": qosLevel
                  }
    return utilities.basicRequest(service="ADMIN", command="LOGIN", parameters=parameters)


def logout():
    return utilities.basicRequest(service="ADMIN", command="LOGOUT")


def qos(qosLevel):
    return utilities.basicRequest(service="ADMIN", command="QOS", parameters={"qoslevel": qosLevel})
