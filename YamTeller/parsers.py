import settings
import controllers

PM_PARSERS = {}

# --------------- STANDARD ECONOMY FUNCTIONS ---------------
standardEconPerms = lambda user: user.name in settings.ALPHATESTERS

sendUserHelp = "Sends money to the account owned by the provided user. Format: SNDU [username] [amount]"
def sendUser(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 3:
        raise ValueError("Invalid number of parameters supplied to SNDU. Help: " + sendUserHelp)

    amount = tokens[2]
    fAmount = None
    try:
        fAmount = float(amount)
    except:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    if fAmount < 0.1:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    username = tokens[1]
    acct = controllers.getAccountFromUsername(session, username)

    ownerAcct = controllers.forceGetAccountFromUsername(session, author.name)

    controllers.transferAccountMoney(session, ownerAcct, acct, fAmount)

    redditor = reddit.redditor(username)
    if redditor is not None:
        redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (fAmount, ownerAcct.number, ownerAcct.name if ownerAcct.name is not None else ownerAcct.description))

    return "Transaction completed successfully. You transferred Y%.2f. You have Y%.2f remaining in your account." % (fAmount, controllers.getAccountBalance(ownerAcct))
PM_PARSERS['SNDU'] = (sendUser, sendUserHelp, standardEconPerms)

sendAccountHelp = "Sends money to the account marked with the provided account number. Format: SNDA [account number] [amount]"
def sendAccount(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 3:
        raise ValueError("Invalid number of parameters supplied to SNDA. Help: " + sendAccountHelp)

    amount = tokens[2]
    fAmount = None
    try:
        fAmount = float(amount)
    except:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    if fAmount < 0.1:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    acctNo = tokens[1]
    nAcctNo = None
    try:
        nAcctNo = int(acctNo)
    except:
        raise ValueError("Invalid account number: account numbers need to be integers.")

    acct = controllers.getAccountFromNumber(session, nAcctNo)

    ownerAcct = controllers.forceGetAccountFromUsername(session, author.name)

    controllers.transferAccountMoney(session, ownerAcct, acct, fAmount)

    try:
        username = acct.name
        if username is not None:
            redditor = reddit.redditor(username)
            if redditor is not None:
                redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (fAmount, ownerAcct.number, ownerAcct.name if ownerAcct.name is not None else ownerAcct.description))
    except:
        pass

    return "Transaction completed successfully. You transferred Y%.2f. You have Y%.2f remaining in your account." % (
    fAmount, controllers.getAccountBalance(ownerAcct))
PM_PARSERS['SNDA'] = (sendAccount, sendAccountHelp, standardEconPerms)

balanceHelp = "Shows your bank balance. Format: BALN"
def balance(reddit, session, author, body):
    ownerAcct = controllers.forceGetAccountFromUsername(session, author.name)
    return "You have Y%.2f remaining in your account with number %08d." % (controllers.getAccountBalance(ownerAcct), ownerAcct.number)
PM_PARSERS['BALN'] = (balance, balanceHelp, standardEconPerms)

fedBalanceHelp = "Shows the balance of the Federal Reserve. Format: FBAL"
def fedBalance(reddit, session, author, body):
    return "The Federal Reserve has a balance of Y%.2f." % controllers.getAccountBalance(controllers.getTreasury(session))
PM_PARSERS['FBAL'] = (fedBalance, fedBalanceHelp, standardEconPerms)

helpHelp = "Shows economy command help. Format: HELP"
def help(reddit, session, author, body):
    output = "YAMSDAQbot Help\n\nTo run any command, send it to YAMSDAQbot in a message. The title does not matter.\n\nHere is a list of commands:\n\n"
    for key, value in sorted(PM_PARSERS.iteritems()):
        _, helpString, perms = value
        if perms is None or perms(author):
            output += "* %s %s\n" % (key, helpString)
    return output
PM_PARSERS['HELP'] = (help, helpHelp, standardEconPerms)

# --------------- ADMIN FUNCTIONS ---------------
def hasFederalTransferPerms(user):
    return settings.FEDERAL_RESERVE_TRANSFERS_ENABLED and (user.name in settings.FRTRANSFERPERMS)

federalPaymentToUserHelp = "Transfers money to a given user's bank account from a provided non-user bank account. Format: FEDU [from account number] [to username] [amount]"
def federalPaymentToUser(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 4:
        raise ValueError("Invalid number of parameters supplied to FEDU. Help: " + federalPaymentToUserHelp)

    amount = tokens[3]
    try:
        fAmount = float(amount)
    except:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    if fAmount < 0.1:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    # From Acct
    facctNo = tokens[1]
    try:
        nfAcctNo = int(facctNo)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    facct = controllers.getAccountFromNumber(session, nfAcctNo)

    if facct is None:
        raise ValueError("Source account with this number not found.")

    if facct.name is not None:
        raise ValueError("FEDU can only be used to transfer from non-user accounts.")

    # To Acct
    tusername = tokens[2]
    tacct = controllers.getAccountFromUsername(session, tusername)

    controllers.transferAccountMoney(session, facct, tacct, fAmount)

    redditor = reddit.redditor(tusername)
    if redditor is not None:
        redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (fAmount, facct.number, facct.name if facct.name is not None else facct.description))

    return "Transaction completed successfully. You transferred Y%.2f. There is Y%.2f remaining in the source account." % (
        fAmount, controllers.getAccountBalance(facct))
PM_PARSERS['FEDU'] = (federalPaymentToUser, federalPaymentToUserHelp, hasFederalTransferPerms)

federalPaymentToAccountHelp = "Transfers money to a given bank account from a provided non-user bank account. Format: FEDU [from account number] [to account number] [amount]"
def federalPaymentToAccount(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 4:
        raise ValueError("Invalid number of parameters supplied to FEDA. Help: " + federalPaymentToAccountHelp)

    amount = tokens[3]
    try:
        fAmount = float(amount)
    except:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    if fAmount < 0.1:
        raise ValueError("Invalid transfer amount. The amount parameter needs to be a positive number at least equal to one cent.")

    # From Acct
    facctNo = tokens[1]
    try:
        nfAcctNo = int(facctNo)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    try:
        facct = controllers.getAccountFromNumber(session, nfAcctNo)
    except:
        raise ValueError("Source account with this number not found.")

    if facct.name is not None:
        raise ValueError("FEDA can only be used to transfer from non-user accounts.")

    # To Acct
    tacctNo = tokens[2]
    try:
        ntAcctNo = int(tacctNo)
    except:
        raise ValueError("Invalid destination account number: account numbers need to be integers.")

    try:
        tacct = controllers.getAccountFromNumber(session, ntAcctNo)
    except:
        raise ValueError("Destination account with this number not found.")

    controllers.transferAccountMoney(session, facct, tacct, fAmount)


    username = tacct.name
    try:
        if username is not None:
            redditor = reddit.redditor(username)
            if redditor is not None:
                redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (fAmount, facct.number, facct.name if facct.name is not None else facct.description))
    except:
        pass

    return "Transaction completed successfully. You transferred Y%.2f. There is Y%.2f remaining in the source account." % (
    fAmount, controllers.getAccountBalance(facct))
PM_PARSERS['FEDA'] = (federalPaymentToAccount, federalPaymentToAccountHelp, hasFederalTransferPerms)

federalAccountBalanceHelp = "Shows the balance of a non-user bank account. Format: FEDB [account number]"
def federalAccountBalance(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FEDB. Help: " + federalAccountBalanceHelp)

    acctNo = tokens[1]
    try:
        fAcctNo = int(acctNo)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    try:
        acct = controllers.getAccountFromNumber(session, fAcctNo)
    except:
        raise ValueError("Source account with this number not found.")

    if acct.name is not None:
        raise ValueError("FEDB can only be used to look up the balance of non-user accounts.")

    balance = controllers.getAccountBalance(acct)

    return "The balance of account %08d (%s) is Y%.2f." % (fAcctNo, acct.description, balance)
PM_PARSERS['FEDB'] = (federalAccountBalance, federalAccountBalanceHelp, hasFederalTransferPerms)

createNonUserAccountHelp = "Creates a non-user bank account for use by parties and enterprises. The account description should not contain spaces. Format: CRTA [account description]"
def createNonUserAccount(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTA. Help: " + createNonUserAccountHelp)

    desc = tokens[1]
    acct = controllers.createNonUserAccount(session, desc)

    return "New account created. Account number: %08d, description: %s" % (acct.number, acct.description)
PM_PARSERS['CRTA'] = (createNonUserAccount, createNonUserAccountHelp, hasFederalTransferPerms)

createUserAccountHelp = "Creates an account for a user other than the author of the message. Format: CRTU [Reddit username without u/]"
def createUserAccount(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTU. Help: " + createUserAccountHelp)

    name = tokens[1]

    try:
        redditor = reddit.redditor(name)
        if redditor is None:
            raise ValueError("No such Redditor found.")
    except:
        raise ValueError("No such Redditor found.")

    try:
        existingAcct = controllers.getAccountFromUsername(session, name)
    except:
        pass
    else:
        raise ValueError("This user already has a bank account. Account number: %08d" % existingAcct.number)

    acct = controllers.forceGetAccountFromUsername(session, name)

    return "New user account created. Account number: %08d, username: %s" % (acct.number, acct.name)
PM_PARSERS['CRTU'] = (createUserAccount, createUserAccountHelp, hasFederalTransferPerms)

createGovtAccountHelp = "Creates a non-user bank account for use by Government Institutions. These accounts have 10000000-level numbers. The account description should not contain spaces. Format: CRTG [account description]"
def createGovtAccount(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTG. Help: " + createGovtAccountHelp)

    desc = tokens[1]
    acct = controllers.createGovtAccount(session, desc)

    return "New government account created. Account number: %08d, description: %s" % (acct.number, acct.description)
PM_PARSERS['CRTG'] = (createGovtAccount, createGovtAccountHelp, hasFederalTransferPerms)

# TODO: amount<0.01 not allowed

# --------------- POST EVALUATION & FLAIR SYSTEM FUNCTIONS ---------------
hasPostEvaluationPerms = lambda user: settings.POST_EVALUATION_ENABLED

depositHelp = "Deposits a Reddit post's upvote values into the user's bank account. Format: FDPT [post url]"
def deposit(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FDPT. Help: " + depositHelp)

    url = tokens[1]
    try:
        submission = reddit.submission(url=url)
        if submission is None:
            raise ValueError("No submission found at this URL. If the post is a link post, be sure to post the URL of the Reddit post (get the comments URL) and not the URL of the link.")
    except:
        raise ValueError("No submission found at this URL. If the post is a link post, be sure to post the URL of the Reddit post (get the comments URL) and not the URL of the link.")

    subreddit = submission.subreddit
    if subreddit.display_name.lower() not in settings.SUBREDDITMULTIPLIERS:
        raise ValueError("Submission in subreddit %s are not accepted by the Yam Treasury." % subreddit.display_name)

    if submission.author != author:
        raise ValueError("You can only deposit submissions you submitted.")

    acct = controllers.forceGetAccountFromUsername(session, author.name)
    controllers.registerPostToUser(session, acct, submission.id)

    score = submission.score
    multiplier = settings.SUBREDDITMULTIPLIERS[subreddit.display_name.lower()]
    amount = score * multiplier

    controllers.transferAccountMoney(session, controllers.getTreasury(session), acct, amount)

    return "You have deposited the submission with the ID %s. At Y%.2f per upvote in the subreddit /r/%s, you received Y%.2f for the %d upvotes on your submission."\
           % (submission.id, multiplier, subreddit.display_name, amount, score)
PM_PARSERS['FDPT'] = (deposit, depositHelp, hasPostEvaluationPerms)

purchaseHelp = "Purchases a /r/YamRepublic flair using funds from the user's bank account. Format: FPRS [flair number]"
def purchase(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FPRS. Help: " + purchaseHelp)

    try:
        id = int(tokens[1])
    except:
        raise ValueError("The second parameter needs to be the number representing the flair you want to purchase.")

    if id not in settings.FLAIRS:
        raise ValueError("A flair with this ID does not exist.")

    text, css, price = settings.FLAIRS[id]

    acct = controllers.forceGetAccountFromUsername(session, author.name)
    balance = controllers.getAccountBalance(acct)
    if balance < price:
        raise ValueError("You cannot afford this flair: it costs Y%.2f but you only have Y%.2f" % (price, balance))

    controllers.addFlair(reddit, session, acct, text, css)
    controllers.transferAccountMoney(session, acct, controllers.getTreasury(session), price)

    expiration = acct.owner_flair_expiration.strftime("%A, %d %B %Y")
    return "You have purchased the %s flair for Y%.2f. It will expire on %s. You have Y%.2f remaining in your account." % (text, price, expiration, controllers.getAccountBalance(acct))
PM_PARSERS['FPRS'] = (purchase, purchaseHelp, hasPostEvaluationPerms)

queryFlairHelp = "Shows information about the user's current flair. Format: FQRY"
def queryFlair(reddit, session, author, body):
    acct = controllers.forceGetAccountFromUsername(session, author.name)
    text = acct.owner_flair_text

    if text is None:
        return "You currently do not own a flair."

    expiration = acct.owner_flair_expiration.strftime("%A, %d %B %Y")

    return "You currently own the %s flair. It will expire on %s." % (text, expiration)
PM_PARSERS['FQRY'] = (queryFlair, queryFlairHelp, hasPostEvaluationPerms)

listFlairsHelp = "Lists purchasable flairs. Format: FLST"
def listFlairs(reddit, session, author, body):
    flairs = ["#%d: %s for Y%.2f weekly" % (id, name, price) for id, (name, css, price) in settings.FLAIRS.iteritems()]

    return "Here is a list of purchasable flairs: \n" + "\n".join(flairs)
PM_PARSERS['FLST'] = (listFlairs, listFlairsHelp, hasPostEvaluationPerms)

deleteFlairHelp = "Deletes the user's current flair without a refund so that he can purchase a new one. Format: FDEL"
def deleteFlair(reddit, session, author, body):
    acct = controllers.forceGetAccountFromUsername(session, author.name)
    controllers.removeFlair(reddit, session, acct)

    return "Your current flair has been successfully deleted."
PM_PARSERS['FDEL'] = (deleteFlair, deleteFlairHelp, hasPostEvaluationPerms)

# --------------- INVALID COMMAND FUNCTIONS ---------------
def defaultPMFn(reddit, a, b, c):
    return "This command does not exist. Please send a message starting with the word HELP to see the commands."

# --------------- PARSER ACCESS FUNCTIONS ---------------
freePerms = lambda x: True

def getPMParser(command):
    return PM_PARSERS.get(command.upper(), (defaultPMFn, "", freePerms))