from datetime import timedelta

SLEEP = 5 # Seconds

# ALPHA TEST ACCOUNTS
ALPHATESTERS = [
    "awesomeboy101",
    "Diztortion_",
    "spladlesrus",
    "xxtheproonexx",
    "sultanskyman",
    "Bluy98888",
    "WHYRedditHatesMeSo",
    "Archie357",
    "Laughingtitan",
    "BassistGaming"
]

# BASIC ACCOUNTS
TREASURY = "YamTreasury"
TREASURYNO = 10000000
TREASURYSTARTSAT = 1000000000

# ACCOUNT NO RANGES
GOVTACCTS = (10000001, 19999999)
COMPANYACCTS = (20000000, 29999999)
USERACCTS = (30000000, 99999999)

# BASIC SETTINGS
STARTINGFUNDS = 50000.0

# TAXATION
TRANSFERTAX = 0.0
WEEKLYBALANCETAX = 0.0

# FEDERAL RESERVE TRANSFERS
FEDERAL_RESERVE_TRANSFERS_ENABLED = True
FRTRANSFERPERMS = [
    'Bluy98888',
    'sultanskyman'
]

# POST EVALUATION & FLAIRS
POST_EVALUATION_ENABLED = True
SUBREDDITMULTIPLIERS = { # SMALL LETTERS PLEASE
    'yamrepublic': 5, # Y5.00 per upvote in /r/YamRepublic
}
POSTTAX = 0.0
FLAIRS = {
    1: ("Bronze Yam", "samplecss", 100),
    2: ("Silver Yam", "samplecss", 500),
    3: ("Gold Yam", "samplecss", 800),
    4: ("Emerald Yam", "samplecss", 1000),
    5: ("Sapphire Yam", "samplecss", 5000),
    6: ("Ruby Yam", "samplecss", 10000),
    7: ("3 Star Ruby Yam", "samplecss", 25000),
    8: ("Diamond Yam", "samplecss", 50000),
    9: ("3 Star Diamond Yam", "samplecss", 100000)
}
FLAIRSUBS = ["YAMSDAQ"]
FLAIRDURATION = timedelta(weeks=1)

# STOCK EXCHANGE
STOCK_EXCHANGE_ENABLED = False
STOCK_EXCHANGE_SUBREDDIT = "YAMSDAQ"
STOCK_EXCHANGE_RANDOM_LOWERBOUND = 0.8
STOCK_EXCHANGE_RANDOM_UPPERBOUND = 1.2
STOCKTAX = 0.0
VALUEWINDOWS = {
    60 * 60, # 1 hour
    24 * 60 * 60, # 1 day
    7 * 24 * 60 * 60, # 1 week
    30 * 24 * 60 * 60, # 1 month
    365 * 24 * 60 * 60 # 1 year
}