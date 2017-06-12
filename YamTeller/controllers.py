from models import Account, Post
from datetime import datetime
import settings
import random

# --------------- TAX CALCULATORS ---------------
def getTransferTaxAmount(amount):
    return amount * settings.TRANSFERTAX

def getWeeklyBalanceTaxAmount(amount):
    return amount * settings.WEEKLYBALANCETAX

def getPostTaxAmount(amount):
    return amount * settings.POSTTAX

# --------------- ACCOUNT ACCESS ---------------
def getUnusedAccountNoInRange(session, range):
    while True:
        number = random.randint(*range)

        try:
            getAccountFromNumber(session, number)
        except:
            return number

def getSmallestAccountNoInRange(session, range):
    for i in xrange(*range):
        try:
            getAccountFromNumber(session, i)
        except ValueError:
            return i

def getAccountFromUsername(session, name):
    acct = session.query(Account).filter(Account.name.ilike(name)).first()

    if acct is None:
        raise ValueError("This user does not have an account.")

    return acct

def forceGetAccountFromUsername(session, name):
    acct = session.query(Account).filter(Account.name.ilike(name)).first()

    if acct is None:
        acct = Account(name=name, number=getUnusedAccountNoInRange(session, settings.USERACCTS), bank_in_cents=settings.STARTINGFUNDS * 100, description="Personal Account")
        session.add(acct)
        session.commit()

    return acct

def createNonUserAccount(session, description):
    acct = Account(number=getUnusedAccountNoInRange(session, settings.COMPANYACCTS), bank_in_cents=0, description=description)
    session.add(acct)
    session.commit()

    return acct

def createGovtAccount(session, description):
    acct = Account(number=getSmallestAccountNoInRange(session, settings.GOVTACCTS), bank_in_cents=0, description=description)
    session.add(acct)
    session.commit()

    return acct

def getAccountFromNumber(session, number):
    acct = session.query(Account).filter(Account.number == number).first()

    if acct is None:
        raise ValueError("No account with this number found.")

    return acct

def getTreasury(session):
    try:
        acc = getAccountFromNumber(session, settings.TREASURYNO)
        return acc
    except ValueError:
        acct = Account(name=settings.TREASURY, number=settings.TREASURYNO, bank_in_cents=settings.TREASURYSTARTSAT * 100, description="The Federal Reserve of the Yam Republic")
        session.add(acct)
        session.commit()

        return acct

def getAccountBalance(account):
    return account.bank_in_cents / float(100)

def transferAccountMoney(session, fromAccount, toAccount, amount):
    tax = getTransferTaxAmount(amount)
    receiveAmount = amount - tax
    if getAccountBalance(fromAccount) > amount:
        fromAccount.bank_in_cents -= int(amount * 100)
        toAccount.bank_in_cents += int(receiveAmount * 100)
        getTreasury(session).bank_in_cents += int(tax * 100)

        session.commit()
    else:
        raise ValueError("The source account has insufficient funds for this operation.")

# --------------- POST REGISTRATION ---------------
def registerPostToUser(session, acct, id):
    if isPostRegistered(session, id):
        raise ValueError("This submission is already deposited.")

    post = Post(id=id, owner_number=acct.number)
    session.add(post)
    session.commit()

    return post

def isPostRegistered(session, id):
    return session.query(Post).filter(Post.id == id).count() > 0

# --------------- FLAIRS ---------------
def addFlair(reddit, session, account, text, css):
    if account.name is None:
        raise ValueError("Flairs can only be added to user-owned accounts.")

    if account.owner_flair_expiration is not None:
        raise ValueError("This user already has a purchased flair, it needs to be deleted first.")

    # Let's set it on reddit
    redditor = reddit.redditor(account.name)
    if redditor is None:
        raise ValueError("The Reddit account linked to this bank account no longer exists.")

    for subName in settings.FLAIRSUBS:
        try:
            sub = reddit.subreddit(subName)
            flairs = sub.flair
            flairs.set(redditor, text, css)
        except:
            raise ValueError("There was an issue adding the flair to the subreddit %s. Please contact the developers.")

    account.owner_flair_text = text
    account.owner_flair_css = css
    account.owner_flair_expiration = datetime.now() + settings.FLAIRDURATION

    session.commit()

def removeFlair(reddit, session, account):
    if account.name is None:
        raise ValueError("Flairs can only be removed from user-owned accounts.")

    if account.owner_flair_expiration is None:
        raise ValueError("This user has not purchased a flair that can be deleted.")

    # Let's set it on reddit
    redditor = reddit.redditor(account.name)
    if redditor is None:
        raise ValueError("The Reddit account linked to this bank account no longer exists.")

    for subName in settings.FLAIRSUBS:
        try:
            sub = reddit.subreddit(subName)
            flairs = sub.flair
            flairs.set(redditor, "", "")
        except:
            raise ValueError("There was an issue removing the flair from the subreddit %s. Please contact the developers.")

    account.owner_flair_text = None
    account.owner_flair_css = None
    account.owner_flair_expiration = None

    session.commit()