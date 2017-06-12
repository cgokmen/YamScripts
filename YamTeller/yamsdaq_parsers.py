import settings

PM_PARSERS = {}
YAMSDAQ_PARSERS = {}

# --------------- STOCK EXCHANGE FUNCTIONS ---------------
hasStockExchangePerms = lambda user: settings.STOCK_EXCHANGE_ENABLED

buyHelp = "Buys a given number of stocks from a company. Must be sent as a comment under a company thread. Format: XBUY [number of stocks]"
def buy(session, company, data, author, body):
    pass
YAMSDAQ_PARSERS['XBUY'] = (buy, buyHelp, hasStockExchangePerms)

sellHelp = "Sells a given number of stocks of a company. Must be sent as a comment under a company thread. Format: XSEL [number of stocks]"
def sell(session, company, data, author, body):
    pass
YAMSDAQ_PARSERS['XSEL'] = (sell, sellHelp, hasStockExchangePerms)

portfolioHelp = "Displays your stock portfolio. Format: XPFO"
def portfolio(reddit, session, author, body):
    pass
PM_PARSERS['XPFO'] = (portfolio, portfolioHelp, hasStockExchangePerms)

def defaultYAMSDAQFn(a, b, c, d, e):
    return "This command does not exist. Please use the following commands in a comment under a stock market entry: XBUY [numstocks] or XSEL [numstocks], replacing [numstocks] with the number of stocks you want to buy or sell."

freePerms = lambda x: True
def getYAMSDAQParser(command):
    return YAMSDAQ_PARSERS.get(command.upper(), (defaultYAMSDAQFn, "", freePerms))