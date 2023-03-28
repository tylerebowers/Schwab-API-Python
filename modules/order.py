from modules import universe
from apis import quotes
import requests
import math


def help(term):
    definitions = {
        "order": {
            'session': "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'",
            'duration': "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'",
            'orderType': "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or "
                         "'MARKET_ON_CLOSE' or 'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or "
                         "'NET_CREDIT' or 'NET_ZERO'",
            'cancelTime': {"date": "string", "shortFormat": False},
            'complexOrderStrategyType': "'NONE' or 'COVERED' or 'VERTICAL' or 'BACK_RATIO' or 'CALENDAR' or 'DIAGONAL' or 'STRADDLE' or 'STRANGLE' or 'COLLAR_SYNTHETIC' or 'BUTTERFLY' or 'CONDOR' or 'IRON_CONDOR' or 'VERTICAL_ROLL' or 'COLLAR_WITH_STOCK' or 'DOUBLE_DIAGONAL' or 'UNBALANCED_BUTTERFLY' or 'UNBALANCED_CONDOR' or 'UNBALANCED_IRON_CONDOR' or 'UNBALANCED_VERTICAL_ROLL' or 'CUSTOM'",
            'quantity': 0,
            'filledQuantity': 0,
            'remainingQuantity': 0,
            'requestedDestination': "'INET' or 'ECN_ARCA' or 'CBOE' or 'AMEX' or 'PHLX' or 'ISE' or 'BOX' or 'NYSE' or 'NASDAQ' or 'BATS' or 'C2' or 'AUTO'",
            'destinationLinkName': "string",
            'releaseTime': "string",
            'stopPrice': 0,
            'stopPriceLinkBasis': "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
            'stopPriceLinkType': "'VALUE' or 'PERCENT' or 'TICK'",
            'stopPriceOffset': 0,
            'stopType': "'STANDARD' or 'BID' or 'ASK' or 'LAST' or 'MARK'",
            'priceLinkBasis': "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
            'priceLinkType': "'VALUE' or 'PERCENT' or 'TICK'",
            'price': 0,
            'taxLotMethod': "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'AVERAGE_COST' or 'SPECIFIC_LOT'",
            'orderLegCollection': [{
                "orderLegType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                "legId": 0,
                "instrument": "The type <Instrument> has the following subclasses [Equity, FixedIncome, MutualFund, CashEquivalent, Option] descriptions are listed below\"",
                "instruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or 'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'",
                "positionEffect": "'OPENING' or 'CLOSING' or 'AUTOMATIC'",
                "quantity": 0,
                "quantityType": "'ALL_SHARES' or 'DOLLARS' or 'SHARES'"
            }],
            'activationPrice': 0,
            'specialInstruction': "'ALL_OR_NONE' or 'DO_NOT_REDUCE' or 'ALL_OR_NONE_DO_NOT_REDUCE'",
            'orderStrategyType': "'SINGLE' or 'OCO' or 'TRIGGER'",
            'orderId': 0,
            'cancelable': False,
            'editable': False,
            'status': "'AWAITING_PARENT_ORDER' or 'AWAITING_CONDITION' or 'AWAITING_MANUAL_REVIEW' or 'ACCEPTED' or 'AWAITING_UR_OUT' or 'PENDING_ACTIVATION' or 'QUEUED' or 'WORKING' or 'REJECTED' or 'PENDING_CANCEL' or 'CANCELED' or 'PENDING_REPLACE' or 'REPLACED' or 'FILLED' or 'EXPIRED'",
            'enteredTime': "string",
            'closeTime': "string",
            'accountId': 0,
            'orderActivityCollection': [
                "The type <OrderActivity> has the following subclasses [Execution] descriptions are listed below"],
            'replacingOrderCollection': [{}],
            'childOrderStrategies': [{}],
            'statusDescription': "string"},

        "leg": {
            "orderLegType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
            "legId": 0,
            "instrument": "The type <Instrument> has the following subclasses [Equity, FixedIncome, MutualFund, CashEquivalent, Option] descriptions are listed below\"",
            "instruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or 'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'",
            "positionEffect": "'OPENING' or 'CLOSING' or 'AUTOMATIC'",
            "quantity": 0,
            "quantityType": "'ALL_SHARES' or 'DOLLARS' or 'SHARES'"},

        "instrument": {
            "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
            "cusip": "string",
            "symbol": "string",
            "description": "string",
            "maturityDate": "string",
            "variableRate": 0,
            "factor": 0,
            "type": "\n MutualFund: 'NOT_APPLICABLE' or 'OPEN_END_NON_TAXABLE' or 'OPEN_END_TAXABLE' or 'NO_LOAD_NON_TAXABLE' or 'NO_LOAD_TAXABLE'\n CashEquivalent: 'SAVINGS' or 'MONEY_MARKET_FUND'\n OPTION: 'VANILLA' or 'BINARY' or 'BARRIER'",
            "putCall": "'PUT' or 'CALL'",
            "underlyingSymbol": "string",
            "optionMultiplier": 0,
            "optionDeliverables": [{
                "symbol": "string",
                "deliverableUnits": 0,
                "currencyType": "'USD' or 'CAD' or 'EUR' or 'JPY'",
                "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"}]},

        "execution": {
            "activityType": "'EXECUTION' or 'ORDER_ACTION'",
            "executionType": "'FILL'",
            "quantity": 0,
            "orderRemainingQuantity": 0,
            "executionLegs": [{
                "legId": 0,
                "quantity": 0,
                "mismarkedQuantity": 0,
                "price": 0,
                "time": "string"}]},
    }
    try:
        spl = term.split(".")
        print(f"[HELP]: {term} = {definitions[spl[0].lower()][spl[1]]}")
    except:
        universe.terminal.warning("Definition not found")


class Instrument:
    aliases = ('assetType', 'cusip', 'symbol', 'description', 'maturityDate', 'variableRate', 'factor', 'type',
               'putCall', 'underlyingSymbol', 'optionMultiplier', 'optionDeliverables')
    scopes = {"EQUITY": ("assetType", "cusip", "symbol", "description"),
              "FIXED_INCOME": ("assetType", "cusip", "symbol", "description", "maturityDate", "variableRate", "factor"),
              "MUTUAL_FUND": ("assetType", "cusip", "symbol", "description", "type"),
              "CASH_EQUIVALENT": ("assetType", "cusip", "symbol", "description", "type"),
              "OPTION": ("assetType", "cusip", "symbol", "description", "type", "putCall", "underlyingSymbol",
                         "optionMultiplier", "optionDeliverables")}

    def __init__(self, assetType, cusip=None, symbol=None, description=None, maturityDate=None,
                 variableRate=None, factor=None, type=None, putCall=None,
                 underlyingSymbol=None, optionMultiplier=None, optionDeliverables=None):
        if assetType.upper() not in self.scopes.keys():
            universe.terminal.error("Invalid assetType in modules/order.createInstrument")
        self.assetType = assetType
        self.cusip = cusip
        self.symbol = symbol
        self.description = description
        self.maturityDate = maturityDate
        self.variableRate = variableRate
        self.factor = factor
        self.type = type
        self.putCall = putCall
        self.underlyingSymbol = underlyingSymbol
        self.optionMultiplier = optionMultiplier
        self.optionDeliverables = optionDeliverables

    def __dict__(self):
        instrument = {}
        for i, param in enumerate((self.assetType, self.cusip, self.symbol, self.description, self.maturityDate,
                                   self.variableRate, self.factor, self.type, self.putCall, self.underlyingSymbol,
                                   self.optionMultiplier, self.optionDeliverables)):
            if param is not None and self.aliases[i] in self.scopes.get(self.assetType, [None]):
                instrument[self.aliases[i]] = param
        return instrument

    def __str__(self):
        return str(self.__dict__())


class Leg:
    aliases = ("orderLegType", "legId", "instrument", "instruction", "positionEffect", "quantity", "quantityType")

    def __init__(self, orderLegType=None, legId=None, instrument=None, instruction=None, positionEffect=None,
                 quantity=None, quantityType=None):
        self.orderLegType = orderLegType
        self.legId = legId
        self.instrument = instrument
        self.instruction = instruction
        self.positionEffect = positionEffect
        self.quantity = quantity
        self.quantityType = quantityType

    def addInstrument(self, instrument):
        self.instrument = instrument

    def __dict__(self):
        legDict = {}
        for i, param in enumerate((
                self.orderLegType, self.legId, self.instrument, self.instruction, self.positionEffect,
                self.quantity, self.quantityType)):
            if param is not None:
                legDict[self.aliases[i]] = param
        if 'instrument' in legDict.keys():
            legDict['instrument'] = legDict['instrument'].__dict__()
            return legDict
        else:
            universe.terminal.error("Order does not contain a leg! (returning null)")
            return None

    def __str__(self):
        return str(self.__dict__())


class Execution:
    aliases = ("activityType", "executionType", "quantity", "orderRemainingQuantity", "executionLegs")

    def __init__(self, activityType=None, executionType=None, quantity=None, orderRemainingQuantity=None, executionLegs=None):
        self.activityType = activityType
        self.executionType = executionType
        self.quantity = quantity
        self.orderRemainingQuantity = orderRemainingQuantity
        self.executionLegs = executionLegs

    def __dict__(self):
        execDict = {}
        for i, param in enumerate((self.activityType, self.executionType, self.quantity, self.orderRemainingQuantity, self.executionLegs)):
            if param is not None: execDict[self.aliases[i]] = param
        return execDict

    def __str__(self):
        return str(self.__dict__())


class Order:
    aliases = ("session", "duration", "orderType", "cancelTime",
               "complexOrderStrategyType", "quantity", "filledQuantity",
               "remainingQuantity", "requestedDestination",
               "destinationLinkName", "releaseTime",
               "stopPrice", "stopPriceLinkBasis", "stopPriceLinkType",
               "stopPriceOffset", "stopType", "priceLinkBasis",
               "priceLinkType", "price", "taxLotMethod", "orderLegCollection",
               "activationPrice", "specialInstruction",
               "orderStrategyType", "orderId", "cancelable", "editable", "status",
               "enteredTime", "closeTime",
               "accountId", "orderActivityCollection", "replacingOrderCollection",
               "childOrderStrategies", "statusDescription")

    def __init__(self, fromDict=None, session=None, duration=None, orderType=None, cancelTime=None, complexOrderStrategyType=None,
                 quantity=None, filledQuantity=None, remainingQuantity=None, requestedDestination=None,
                 destinationLinkName=None, releaseTime=None, stopPrice=None, stopPriceLinkBasis=None,
                 stopPriceLinkType=None, stopPriceOffset=None, stopType=None, priceLinkBasis=None, priceLinkType=None,
                 price=None, taxLotMethod=None, orderLegCollection=None, activationPrice=None, specialInstruction=None,
                 orderStrategyType=None, orderId=None, cancelable=None, editable=None, status=None, enteredTime=None,
                 closeTime=None, accountId=None, orderActivityCollection=None, replacingOrderCollection=None,
                 childOrderStrategies=None, statusDescription=None):
        self.session = session
        self.duration = duration
        self.orderType = orderType
        self.cancelTime = cancelTime
        self.complexOrderStrategyType = complexOrderStrategyType
        self.quantity = quantity
        self.filledQuantity = filledQuantity
        self.remainingQuantity = remainingQuantity
        self.requestedDestination = requestedDestination
        self.destinationLinkName = destinationLinkName
        self.releaseTime = releaseTime
        self.stopPrice = stopPrice
        self.stopPriceLinkBasis = stopPriceLinkBasis
        self.stopPriceLinkType = stopPriceLinkType
        self.stopPriceOffset = stopPriceOffset
        self.stopType = stopType
        self.priceLinkBasis = priceLinkBasis
        self.priceLinkType = priceLinkType
        self.price = price
        self.taxLotMethod = taxLotMethod
        self.orderLegCollection = orderLegCollection
        self.activationPrice = activationPrice
        self.specialInstruction = specialInstruction
        self.orderStrategyType = orderStrategyType
        self.orderId = orderId
        self.cancelable = cancelable
        self.editable = editable
        self.status = status
        self.enteredTime = enteredTime
        self.closeTime = closeTime
        self.accountId = accountId
        self.orderActivityCollection = orderActivityCollection
        self.replacingOrderCollection = replacingOrderCollection
        self.childOrderStrategies = childOrderStrategies
        self.statusDescription = statusDescription
        if fromDict is not None and type(fromDict) == dict:
            for key, value in fromDict.items():
                setattr(self, key, value)

    def addLeg(self, leg):
        if self.orderLegCollection is None: self.orderLegCollection = []
        self.orderLegCollection.append(leg)

    def addOrderActivity(self, leg):
        if self.orderActivityCollection is None: self.orderActivityCollection = []
        self.orderActivityCollection.append(leg)

    def addReplacingOrder(self, leg):
        if self.replacingOrderCollection is None: self.replacingOrderCollection = []
        self.replacingOrderCollection.append(leg)

    def addChildOrder(self, leg):
        if self.childOrderStrategies is None: self.childOrderStrategies = []
        self.childOrderStrategies.append(leg)

    def __dict__(self):
        orderDict = {}
        for i, param in enumerate(
                [self.session, self.duration, self.orderType, self.cancelTime, self.complexOrderStrategyType,
                 self.quantity, self.filledQuantity, self.remainingQuantity, self.requestedDestination,
                 self.destinationLinkName, self.releaseTime, self.stopPrice, self.stopPriceLinkBasis,
                 self.stopPriceLinkType, self.stopPriceOffset, self.stopType, self.priceLinkBasis, self.priceLinkType,
                 self.price, self.taxLotMethod, self.orderLegCollection, self.activationPrice, self.specialInstruction,
                 self.orderStrategyType, self.orderId, self.cancelable, self.editable, self.status, self.enteredTime,
                 self.closeTime, self.accountId, self.orderActivityCollection, self.replacingOrderCollection,
                 self.childOrderStrategies, self.statusDescription]):
            if param is not None:
                orderDict[self.aliases[i]] = param
        if 'orderLegCollection' in orderDict.keys():
            legs = []
            for leg in orderDict['orderLegCollection']:
                if type(leg) == Leg: legs.append(leg.__dict__())
                else: legs.append(leg)
            orderDict['orderLegCollection'] = legs
            return orderDict
        else:
            universe.terminal.error("Order does not contain a leg! (returning null)")
            return None

    def __str__(self):
        return str(self.__dict__())

    def submit(self, protected=True, probability=True):
        submit(self.__dict__(), protected=protected, probability=probability)

    def quickSubmit(self):
        quickSubmit(self.__dict__())


"""
def wizard(instruction, symbol, quantity, price=0, **kwargs): 
    if symbol[0] == "/":
"""


class _Presets:  # https://developer.tdameritrade.com/content/place-order-samples


    class _Equity:

        def _SimpleAssembler(self, orderType, duration, instruction, quantity, symbol, price=None):
            toRet = {
                "orderType": orderType,
                "session": "NORMAL",
                "duration": duration,
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": instruction,
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }
            if price is not None: toRet['price'] = price
            return toRet

        def buyMarket(self, symbol, quantity, duration="DAY"):
            return self._SimpleAssembler("MARKET", duration, "BUY", quantity, symbol)

        def sellMarket(self, symbol, quantity, duration="DAY"):
            return self._SimpleAssembler("MARKET", duration, "SELL", quantity, symbol)

        def buyLimited(self, symbol, quantity, limit, duration="DAY"):
            return self._SimpleAssembler("LIMIT", duration, "BUY", quantity, symbol, limit)

        def sellLimited(self, symbol, quantity, limit, duration="DAY"):
            return self._SimpleAssembler("LIMIT", duration, "SELL", quantity, symbol, limit)

        def sellTrailingStop(self, symbol, quantity, stopPriceOffset):
            return {
                "complexOrderStrategyType": "NONE",
                "orderType": "TRAILING_STOP",
                "session": "NORMAL",
                "stopPriceLinkBasis": "BID",
                "stopPriceLinkType": "VALUE",
                "stopPriceOffset": stopPriceOffset,
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": "SELL",
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }

    equity = _Equity()

    class _Option:

        def buyLimited(self, symbol, quantity, limit, duration="DAY"):
            return {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': duration,
                'orderStrategyType': 'SINGLE',
                'price': limit,
                'orderLegCollection': [
                    {'instruction': 'BUY',
                     'quantity': quantity,
                     'instrument': {
                         'symbol': symbol,
                         'assetType': 'OPTION'}
                     }
                ]
            }

        def sellLimited(self, symbol, quantity, limit, duration="DAY"):
            return {
                'orderType': 'LIMIT',
                'session': 'NORMAL',
                'duration': duration,
                'orderStrategyType': 'SINGLE',
                'price': limit,
                'orderLegCollection': [
                    {'instruction': 'SELL',
                     'quantity': quantity,
                     'instrument': {
                         'symbol': symbol,
                         'assetType': 'OPTION'}
                     }
                ]
            }

        def buyVerticalCallSpread(self, buySymbol, sellSymbol, buyQuantity, sellQuantity, price):
            return {
                "orderType": "NET_DEBIT",
                "session": "NORMAL",
                "price": price,
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollection": [
                    {
                        "instruction": "BUY_TO_OPEN",
                        "quantity": buyQuantity,
                        "instrument": {
                            "symbol": buySymbol,
                            "assetType": "OPTION"
                        }
                    },
                    {
                        "instruction": "SELL_TO_OPEN",
                        "quantity": sellQuantity,
                        "instrument": {
                            "symbol": sellSymbol,
                            "assetType": "OPTION"
                        }
                    }
                ]
            }

    option = _Option()


presets = _Presets()


def submit(order, protected=True, probability=True):
    if type(order) == Order: order = order.__dict__()
    if len(order.get("orderLegCollection", [])) < 1:
        universe.terminal.error("Order does not contain a Leg (canceled).")
        return
    for leg in order.get("orderLegCollection", []):
        if leg.get("instrument", None) is None:
            universe.terminal.error("Order Leg does not contain an Instrument (canceled).")
            return
    if protected and order.get("orderType").upper() == "LIMIT":
        for leg in order.get("orderLegCollection"):
            symbol = leg.get("instrument").get("symbol", None)
            resp = quotes.getQuote(symbol).get(symbol, {})
            price = (resp.get("askPrice", -10) + resp.get("bidPrice", -10)) / 2
            priceEpsilon = (order.get("price") - price) / price
            if resp.get("askSize", 0) == 0 or resp.get("bidSize", 0) == 0:
                abSizeRatio = 1
            else:
                abSizeRatio = resp.get("askSize") / resp.get("bidSize", 1)
            if priceEpsilon > universe.preferences.orderDeltaLimit:
                universe.terminal.error(
                    "Order price difference surpassed limit in universe.prefernces.orderDeltaLimit (canceled).")
                return
            if probability:
                universe.terminal.info(
                    f"Execution probability: {math.atan(500 * abSizeRatio ** 3 * priceEpsilon) / math.pi + 0.5:.4f}")
    return _OrderResponseHandler(
        requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                      json=order,
                      headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def quickSubmit(order):
    if type(order) == Order: order = order.__dict__()
    return _OrderResponseHandler(
        requests.post('https://api.tdameritrade.com/v1/accounts/' + universe.credentials.accountNumber + '/orders',
                      json=order,
                      headers={'Authorization': 'Bearer ' + universe.tokens.accessToken}))


def _OrderResponseHandler(response):
    if universe.preferences.printResponseCode: print(response)
    if response.ok:
        universe.terminal.info("Order received successfully")
    else:
        universe.terminal.error("Order improperly formatted (are you missing some variables in it?)")
