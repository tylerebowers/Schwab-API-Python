"""
This file stores variables to be used between python files and functions
Coded by Tyler Bowers
Github: https://github.com/tylerebowers/TD-Ameritrade-API-Python-Wrapper
"""


class _Credentials:
    # Schwab/TD account credentials
    consumerKey = "your consumer key"
    callbackUrl = "https://localhost/"
    accountUsername = "your account username"
    accountNumber = "your account number"
    # Postgresql database credentials
    postgresqlHost = "127.0.0.1"
    postgresqlUsername = "stockbot"  # edit if necessary
    postgresqlPassword = "PASSWORD"
    postgresqlDatabase = "stockdata"

credentials = _Credentials()


class _Preferences:
    usingDatabase = False
    printResponseCode = True
    streamingQOSLevel = 2
    usingDataframes = True

preferences = _Preferences()

"""
Below here are variables for functionality of the program; they shouldn't be changed
"""

threads = []


class _Tokens:
    accessToken = None
    refreshToken = None
    accessTokenDateTime = None
    refreshTokenDateTime = None
    authTokenTimeout = 30  # in minutes

tokens = _Tokens()


class _Postgresql:
    connection = None
    cursor = None
    engine = None

    def commit(self):
        self.connection.commit()

    def execute(self, toExecute):
        self.cursor.execute(toExecute)

database = _Postgresql()


class _Streaming:
    subscriptionKey = None
    connectionInfo = {}
    userPrincipals = {}
    requestId = 0
    terminal = None
    active = False
    _QOSToSeconds = [0.5, 0.75, 1.0, 1.5, 3.0, 5.0]
    def getQOS(self, qos=preferences.streamingQOSLevel):
        try: return self._QOSToSeconds[int(qos)]
        except: return -1

    subscriptions = {"QUOTE": {"keys": [], "fields": []},
                     "OPTION": {"keys": [], "fields": []},
                     "LEVELONE_FUTURES": {"keys": [], "fields": []},
                     "LEVELONE_FOREX": {"keys": [], "fields": []},
                     "LEVELONE_FUTURES_OPTIONS": {"keys": [], "fields": []},
                     "ACCT_ACTIVITY": {"keys": [], "fields": []},
                     "ACTIVES_NYSE": {"keys": [], "fields": []},
                     "ACTIVES_OTCBB": {"keys": [], "fields": []},
                     "ACTIVES_OPTIONS": {"keys": [], "fields": []},
                     "FOREX_BOOK": {"keys": [], "fields": []},
                     "FUTURES_BOOK": {"keys": [], "fields": []},
                     "LISTED_BOOK": {"keys": [], "fields": []},
                     "NASDAQ_BOOK": {"keys": [], "fields": []},
                     "OPTIONS_BOOK": {"keys": [], "fields": []},
                     "FUTURES_OPTIONS_BOOK": {"keys": [], "fields": []},
                     "CHART_EQUITY": {"keys": [], "fields": []},
                     "CHART_FUTURES": {"keys": [], "fields": []},
                     "NEWS_HEADLINE": {"keys": [], "fields": []},
                     "NEWS_HEADLINELIST": {"keys": [], "fields": []},
                     "NEWS_STORY": {"keys": [], "fields": []},
                     "TIMESALE_EQUITY": {"keys": [], "fields": []},
                     "TIMESALE_FOREX": {"keys": [], "fields": []},
                     "TIMESALE_FUTURES": {"keys": [], "fields": []},
                     "TIMESALE_OPTIONS": {"keys": [], "fields": []}}

    fieldAliases = {
        "CHART_EQUITY": (
            "key", "Open_Price", "High_Price", "Low_Price", "Close_Price", "Volume", "Sequence", "Chart_Time",
            "Chart_Day"),
        "CHART_FUTURES": ("key", "Chart_Time", "Open_Price", "High_Price", "Low_Price", "Close_Price", "Volume"),
        "CHART_HISTORY_FUTURES": (
            "key", "Chart_Time", "Open_Price", "High_Price", "Low_Price", "Close_Price", "Volume"),
        "QUOTE": ("Symbol", "Bid_Price", "Ask_Price", "Last_Price", "Bid_Size", "Ask_Size", "Ask_ID", "Bid_ID",
                  "Total_Volume", "Last_Size", "Trade_Time", "Quote_Time", "High_Price", "Low_Price", "Bid_Tick",
                  "Close_Price", "Exchange_ID", "Marginable", "Shortable", "Island_Bid", "Island_Ask", "Island_Volume",
                  "Quote_Day", "Trade_Day", "Volatility", "Description", "Last_ID", "Digits", "Open_Price",
                  "Net_Change",
                  "52_Week_High", "52_Week_Low", "PE_Ratio", "Dividend_Amount", "Dividend_Yield", "Island_Bid_Size",
                  "Island_Ask_Size", "NAV", "Fund_Price", "Exchange_Name", "Dividend_Date", "Regular_Market_Quote",
                  "Regular_Market_Trade", "Regular_Market_Last_Price", "Regular_Market_Last_Size",
                  "Regular_Market_Trade_Time", "Regular_Market_Trade_Day", "Regular_Market_Net_Change",
                  "Security_Status",
                  "Mark", "Quote_Time_in_long", "Trade_Time_in_long", "Regular_Market_Trade_Time_in_long"),
        "OPTION": (
            "Symbol", "Description", "Bid_Price", "Ask_Price", "Last_Price", "High_Price", "Low_Price", "Close_Price",
            "Total_Volume", "Open_Interest", "Volatility", "Quote_Time", "Trade_Time", "Money_Intrinsic_Value",
            "Quote_Day", "Trade_Day", "Expiration_Year", "Multiplier", "Digits", "Open_Price", "Bid_Size", "Ask_Size",
            "Last_Size", "Net_Change", "Strike_Price", "Contract_Type", "Underlying", "Expiration_Month",
            "Deliverables", "Time_Value", "Expiration_Day", "Days_to_Expiration", "Delta", "Gamma", "Theta", "Vega",
            "Rho", "Security_Status", "Theoretical_Option_Value", "Underlying_Price", "UV_Expiration_Type", "Mark"),
        "LEVELONE_FUTURES": (
            "Symbol", "Bid_Price", "Ask_Price", "Last_Price", "Bid_Size", "Ask_Size", "Ask_ID", "Bid_ID",
            "Total_Volume", "Last_Size", "Quote_Time", "Trade_Time", "High_Price", "Low_Price",
            "Close_Price", "Exchange_ID", "Description", "Last_ID", "Open_Price", "Net_Change",
            "Future_Percent_Change", "Exhange_Name", "Security_Status", "Open_Interest", "Mark", "Tick",
            "Tick_Amount", "Product", "Future_Price_Format", "Future_Trading_Hours", "Future_Is_Tradable",
            "Future_Multiplier", "Future_Is_Active", "Future_Settlement_Price", "Future_Active_Symbol",
            "Future_Expiration_Date"),
        "LEVELONE_FOREX": ("Symbol", "Bid_Price", "Ask_Price", "Last_Price", "Bid_Size", "Ask_Size", "Total_Volume",
                           "Last_Size", "Quote_Time", "Trade_Time", "High_Price", "Low_Price", "Close_Price",
                           "Exchange_ID",
                           "Description", "Open_Price", "Net_Change", "Percent_Change", "Exchange_Name", "Digits",
                           "Security_Status", "Tick", "Tick_Amount", "Product", "Trading_Hours", "Is_Tradable",
                           "Market_Maker", "52_Week_High", "52_Week_Low", "Mark"),
        "LEVELONE_FUTURES_OPTIONS": ("Symbol", "Bid_Price", "Ask_Price", "Last_Price", "Bid_Size", "Ask_Size", "Ask_ID",
                                     "Bid_ID", "Total_Volume", "Last_Size", "Quote_Time", "Trade_Time", "High_Price",
                                     "Low_Price", "Close_Price", "Exchange_ID", "Description", "Last_ID", "Open_Price",
                                     "Net_Change", "Future_Percent_Change", "Exchange_Name", "Security_Status",
                                     "Open_Interest", "Mark", "Tick", "Tick_Amount", "Product", "Future_Price_Format",
                                     "Future_Trading_Hours", "Future_Is_Tradable", "Future_Multiplier",
                                     "Future_Is_Active",
                                     "Future_Settlement_Price", "Future_Active_Symbol", "Future_Expiration_Date"),
        "NEWS_HEADLINE": ("Symbol", "Error_Code", "Story_Datetime", "Headline_ID", "Status", "Headline", "Story_ID",
                          "Count_for_Keyword", "Keyword_Array", "Is_Hot", "Story_Source"),
        "TIMESALE": ("Symbol", "Trade_Time", "Last_Price", "Last_Size", "Last_Sequence")}

    fieldDatatypes = {
        "CHART_EQUITY": ("varchar(32)", "float8", "float8", "float8", "float8", "float8", "bigint", "bigint", "int"),
        "CHART_FUTURES": ("varchar(32)", "bigint", "float8", "float8", "float8", "float8", "float8"),
        "CHART_HISTORY_FUTURES": ("varchar(32)", "bigint", "float8", "float8", "float8", "float8", "float8"),
        "QUOTE": (
            "varchar(32)", "float4", "float4", "float4", "float4", "float4", "char(1)", "char(1)", "bigint", "float4",
            "int", "int", "float4", "float4", "char(1)", "float4", "char(1)", "bool", "bool", "float4", "float4",
            "Int", "Int", "Int", "float4", "varchar(32)", "char(1)", "int", "float4", "float4", "float4", "float4",
            "float4", "float4", "float4", "Int", "Int", "float4", "float4", "varchar(32)", "varchar(32)", "bool",
            "bool", "float4", "float4", "int", "int", "float4", "varchar(32)", "float8", "bigint", "bigint", "bigint"),
        "OPTION": (
            "varchar(32)", "varchar(32)", "float4", "float4", "float4", "float4", "float4", "float4", "bigint", "int",
            "float4", "bigint", "bigint", "float4", "Int", "Int", "int", "float4", "int", "float4", "float4", "float4",
            "float4", "float4", "float4", "char(1)", "varchar(32)", "int", "varchar(32)", "float4", "int", "int",
            "float4", "float4", "float4", "float4", "float4", "varchar(32)", "float4", "float8", "char(1)",
            "float8"),
        "LEVELONE_FUTURES": (
            "varchar(32)", "float8", "float8", "float8", "bigint", "bigint", "char(1)", "char(1)", "float8",
            "bigint", "bigint", "bigint", "float8", "float8", "float8", "char(1)", "varchar(32)", "char(1)",
            "float8", "float8", "float8", "varchar(32)", "varchar(32)", "int", "float8", "float8",
            "float8",
            "varchar(32)", "varchar(32)", "varchar(32)", "bool", "float8", "bool", "float8", "varchar(32)",
            "bigint"),
        "LEVELONE_FOREX": (
            "varchar(32)", "float8", "float8", "float8", "bigint", "bigint", "float8", "bigint", "bigint", "bigint",
            "float8", "float8", "float8", "char(1)", "varchar(32)", "float8", "float8", "float8",
            "varchar(32)", "Int", "varchar(32)", "float8", "float8", "varchar(32)", "varchar(32)", "bool",
            "varchar(32)", "float8", "float8", "float8"),
        "LEVELONE_FUTURES_OPTIONS": (
            "varchar(32)", "float8", "float8", "float8", "bigint", "bigint", "char(1)", "char(1)",
            "float8", "bigint", "bigint", "bigint", "float8", "float8", "float8", "char(1)",
            "varchar(32)", "char(1)", "float8", "float8", "float8", "varchar(32)", "varchar(32)",
            "int", "float8", "float8", "float8", "varchar(32)", "varchar(32)", "varchar(32)",
            "bool", "float8", "bool", "float8", "varchar(32)", "bigint"), "NEWS_HEADLINE": (
            "varchar(32)", "float8", "bigint", "varchar(32)", "char(1)", "varchar(32)", "varchar(32)", "integer",
            "varchar(32)", "bool", "char(1)"), "TIMESALE": ("varchar(32)", "bigint", "float8", "float8", "bigint")}

stream = _Streaming()


class _Orders:
    openOrders = []
    closedOrders = []

orders = _Orders()


dataframes = {"QUOTE": {},
              "OPTION": {},
              "LEVELONE_FUTURES": {},
              "LEVELONE_FOREX": {},
              "LEVELONE_FUTURES_OPTIONS": {},
              "ACCT_ACTIVITY": {},
              "ACTIVES_NYSE": {},
              "ACTIVES_OTCBB": {},
              "ACTIVES_OPTIONS": {},
              "FOREX_BOOK": {},
              "FUTURES_BOOK": {},
              "LISTED_BOOK": {},
              "NASDAQ_BOOK": {},
              "OPTIONS_BOOK": {},
              "FUTURES_OPTIONS_BOOK": {},
              "CHART_EQUITY": {},
              "CHART_FUTURES": {},
              "NEWS_HEADLINE": {},
              "NEWS_HEADLINELIST": {},
              "NEWS_STORY": {},
              "TIMESALE_EQUITY": {},
              "TIMESALE_FOREX": {},
              "TIMESALE_FUTURES": {},
              "TIMESALE_OPTIONS": {}}
