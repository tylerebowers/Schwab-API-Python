"""
APIs for User Info and Preferences
https://developer.tdameritrade.com/user-principal/apis
"""
import requests
from modules import globals
from apis import utilities


def getPreferences():
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/preferences',
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def getStreamerSubscriptionKeys():
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/userprincipals/streamersubscriptionkeys',
                                                     params={'accountIds': globals.accountNumber},
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))
    # example of what is returned: {"keys": [{"key": "c7fb2_this_is_not_a_real_key_6c169b"}]}


def getUserPrincipals(**kwargs):  # fields is a list of what to return; options are: streamerSubscriptionKeys, streamerConnectionInfo, preferences, surrogateIds
    args = ["fields"]
    params = utilities.kwargsHandler(args, kwargs)
    return utilities.apiResponseHandler(requests.get('https://api.tdameritrade.com/v1/userprincipals',
                                                     params=params,
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken}))


def updatePreferences(data):  # I could only get this to work through the dev website for some reason
    return utilities.apiResponseHandler(requests.put('https://api.tdameritrade.com/v1/accounts/' + globals.accountNumber + '/preferences',
                                                     json=data,
                                                     headers={'Authorization': 'Bearer ' + globals.accessToken,
                                 'Content-Type': 'application/json'}))


"""  # these are what could be put for "updatePreferences" in the dictionary
{
    "expressTrading": false,
    "directOptionsRouting": false,
    "directEquityRouting": false,
    "defaultEquityOrderLegInstruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'NONE'",
    "defaultEquityOrderType": "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'NONE'",
    "defaultEquityOrderPriceLinkType": "'VALUE' or 'PERCENT' or 'NONE'",
    "defaultEquityOrderDuration": "'DAY' or 'GOOD_TILL_CANCEL' or 'NONE'",
    "defaultEquityOrderMarketSession": "'AM' or 'PM' or 'NORMAL' or 'SEAMLESS' or 'NONE'",
    "defaultEquityQuantity": 0,
    "mutualFundTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
    "optionTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
    "equityTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
    "defaultAdvancedToolLaunch": "'TA' or 'N' or 'Y' or 'TOS' or 'NONE' or 'CC2'",
    "authTokenTimeout": "'FIFTY_FIVE_MINUTES' or 'TWO_HOURS' or 'FOUR_HOURS' or 'EIGHT_HOURS'"
}
            # these are what you will probably have as your values (authTokenTimeout has been changed from 55m to 8h)
            # as arguments: ("false","false","false","NONE","LIMIT","NONE","DAY","NORMAL",0,"FIFO","FIFO","FIFO","NONE","EIGHT_HOURS")
{
    "expressTrading": false,
    "directOptionsRouting": false,
    "directEquityRouting": false,
    "defaultEquityOrderLegInstruction": "NONE",
    "defaultEquityOrderType": "LIMIT",
    "defaultEquityOrderPriceLinkType": "NONE",
    "defaultEquityOrderDuration": "DAY",
    "defaultEquityOrderMarketSession": "NORMAL",
    "defaultEquityQuantity": 0,
    "mutualFundTaxLotMethod": "FIFO",
    "optionTaxLotMethod": "FIFO",
    "equityTaxLotMethod": "FIFO",
    "defaultAdvancedToolLaunch": "NONE",
    "authTokenTimeout": "EIGHT_HOURS"
}
"""
