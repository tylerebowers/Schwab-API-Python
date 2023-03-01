"""

This file has not been completed yet

"""


class Order:
    session = ""  # "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'",
    duration = ""  # "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'",
    orderType = ""  # "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'",
    cancelTime = {
        "date": "string",
        "shortFormat": ""  # false
    }
    complexOrderStrategyType = ""  # "'NONE' or 'COVERED' or 'VERTICAL' or 'BACK_RATIO' or 'CALENDAR' or 'DIAGONAL' or 'STRADDLE' or 'STRANGLE' or 'COLLAR_SYNTHETIC' or 'BUTTERFLY' or 'CONDOR' or 'IRON_CONDOR' or 'VERTICAL_ROLL' or 'COLLAR_WITH_STOCK' or 'DOUBLE_DIAGONAL' or 'UNBALANCED_BUTTERFLY' or 'UNBALANCED_CONDOR' or 'UNBALANCED_IRON_CONDOR' or 'UNBALANCED_VERTICAL_ROLL' or 'CUSTOM'",
    quantity = ""  # 0
    filledQuantity = ""  # 0,
    remainingQuantity = ""  # 0
    requestedDestination = ""  # "'INET' or 'ECN_ARCA' or 'CBOE' or 'AMEX' or 'PHLX' or 'ISE' or 'BOX' or 'NYSE' or 'NASDAQ' or 'BATS' or 'C2' or 'AUTO'",
    destinationLinkName = ""  # "string",
    releaseTime = ""  # "string",
    stopPrice = ""  # 0
    stopPriceLinkBasis = ""  # "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
    stopPriceLinkType = ""  # "'VALUE' or 'PERCENT' or 'TICK'",
    stopPriceOffset = ""  # 0,
    stopType = ""  # "'STANDARD' or 'BID' or 'ASK' or 'LAST' or 'MARK'",
    priceLinkBasis = ""  # "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
    priceLinkType = ""  # "'VALUE' or 'PERCENT' or 'TICK'",
    price = ""  # 0
    taxLotMethod = ""  # "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'AVERAGE_COST' or 'SPECIFIC_LOT'",
    orderLegCollection = [
        {
            "orderLegType": "",
            # "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
            "legId": "",  # 0,
            "instrument": "",
            # "The type <Instrument> has the following subclasses [Equity, FixedIncome, MutualFund, CashEquivalent, Option] descriptions are listed below\"",
            "instruction": "",
            # "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or 'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'",
            "positionEffect": "",  # "'OPENING' or 'CLOSING' or 'AUTOMATIC'",
            "quantity": "",  # 0,
            "quantityType": ""  # "'ALL_SHARES' or 'DOLLARS' or 'SHARES'"
        }
    ],
    activationPrice = ""  # 0,
    specialInstruction = ""  # "'ALL_OR_NONE' or 'DO_NOT_REDUCE' or 'ALL_OR_NONE_DO_NOT_REDUCE'",
    orderStrategyType = ""  # "'SINGLE' or 'OCO' or 'TRIGGER'",
    orderId = ""  # 0,
    cancelable = ""  # false,
    editable = ""  # false,
    status = ""  # "'AWAITING_PARENT_ORDER' or 'AWAITING_CONDITION' or 'AWAITING_MANUAL_REVIEW' or 'ACCEPTED' or 'AWAITING_UR_OUT' or 'PENDING_ACTIVATION' or 'QUEUED' or 'WORKING' or 'REJECTED' or 'PENDING_CANCEL' or 'CANCELED' or 'PENDING_REPLACE' or 'REPLACED' or 'FILLED' or 'EXPIRED'",
    enteredTime = ""  # "string",
    closeTime = ""  # "string",
    accountId = ""  # 0,
    orderActivityCollection = [
        "\"The type <OrderActivity> has the following subclasses [Execution] descriptions are listed below\""],
    replacingOrderCollection = [{}],
    childOrderStrategies = [{}],
    statusDescription = ""  # "string"

    class instrument:
        class Equity:
            assetType = "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            cusip = "string"
            symbol = "string"
            description = "string"

        class FixedIncome:
            assetType = "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            cusip = "string"
            symbol = "string"
            description = "string"
            maturityDate = "string"
            variableRate = 0
            factor = 0

        class MutualFund:
            assetType = "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            cusip = "string"
            symbol = "string"
            description = "string"
            type = "'NOT_APPLICABLE' or 'OPEN_END_NON_TAXABLE' or 'OPEN_END_TAXABLE' or 'NO_LOAD_NON_TAXABLE' or 'NO_LOAD_TAXABLE'"

        class CashEquivalent:
            assetType = "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            cusip = "string"
            symbol = "string"
            description = "string"
            type = "'SAVINGS' or 'MONEY_MARKET_FUND'"

        class Option:
            assetType = "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            cusip = "string"
            symbol = "string"
            description = "string"
            type = "'VANILLA' or 'BINARY' or 'BARRIER'"
            putCall = "'PUT' or 'CALL'"
            underlyingSymbol = "string"
            optionMultiplier = 0
            optionDeliverables = [{
                "symbol": "",  # string
                "deliverableUnits": "",  # 0
                "currencyType": "'USD' or 'CAD' or 'EUR' or 'JPY'",
                "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            }]


class orderWizard:
    def __init__(self, session=None, duration=None, orderType=None, cancelTime=None, complexOrderStrategyType=None,
                 quantity=None, filledQuantity=None, remainingQuantity=None, requestedDestination=None,
                 destinationLinkName=None, releaseTime=None, stopPrice=None, stopPriceLinkBasis=None,
                 stopPriceLinkType=None, stopPriceOffset=None, stopType=None, priceLinkBasis=None, priceLinkType=None,
                 price=None, taxLotMethod=None, orderLegCollection=None, activationPrice=None, specialInstruction=None,
                 orderStrategyType=None, orderId=None, cancelable=None, editable=None, status=None, enteredTime=None,
                 closeTime=None, accountId=None, orderActivityCollection=None, replacingOrderCollection=None,
                 childOrderStrategies=None, statusDescription=None):
        print(locals())
        self.session = None
        self.duration = None
        self.orderType = None
        self.cancelTime = {
            "date": "string",
            "shortFormat": None
        }
        self.complexOrderStrategyType = None
        self.quantity = None
        self.filledQuantity = None
        self.remainingQuantity = None
        self.requestedDestination = None
        self.destinationLinkName = None
        self.releaseTime = None
        self.stopPrice = None
        self.stopPriceLinkBasis = None
        self.stopPriceLinkType = None
        self.stopPriceOffset = None
        self.stopType = None
        self.priceLinkBasis = None
        self.priceLinkType = None
        self.price = None
        self.taxLotMethod = None
        self.orderLegCollection = [
            {
                "orderLegType": None,
                "legId": None,
                "instrument": None,
                # "The type <Instrument> has the following subclasses [Equity, FixedIncome, MutualFund, CashEquivalent, Option] descriptions are listed below\"",
                "instruction": None,
                "positionEffect": None,
                "quantity": None,
                "quantityType": None,
            }
        ]
        self.activationPrice = None
        self.specialInstruction = None
        self.orderStrategyType = None
        self.orderId = None
        self.cancelable = None
        self.editable = None
        self.status = None
        self.enteredTime = None
        self.closeTime = None
        self.accountId = None
        self.orderActivityCollection = []
        #   "\"The type <OrderActivity> has the following subclasses [Execution] descriptions are listed below\""
        self.replacingOrderCollection = None  # [{}]
        self.childOrderStrategies = None  # [{}]
        self.statusDescription = None


class presets:
    class _Equity:
        def buyMarket(self, symbol, quantity):
            order = {
                "orderType": "MARKET",
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": "Buy",
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }
            return order

        def buyLimited(self, symbol, quantity, limit):
            order = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'price': limit,
                'orderLegCollection': [
                    {'instruction': 'Buy',
                     'quantity': quantity,
                     'instrument': {
                         'symbol': symbol,
                         'assetType': 'EQUITY'}
                     }
                ]
            }
            return order

    class _Option:
        def buyEquityLimited(self, symbol, quantity, limit):
            order = {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': 'DAY',
                'orderStrategyType': 'SINGLE',
                'price': limit,
                'orderLegCollection': [
                    {'instruction': 'Buy',
                     'quantity': quantity,
                     'instrument': {
                         'symbol': symbol,
                         'assetType': 'EQUITY'}
                     }
                ]
            }
            return order
