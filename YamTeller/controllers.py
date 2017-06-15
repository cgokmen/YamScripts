from models import Account, Post
from datetime import datetime
import settings
import random
import decimal

Decimal = decimal.Decimal


# --------------- TAX CALCULATORS ---------------
def get_transfer_tax_for_amount(amount):
    return (amount * settings.TRANSFERTAX).quantize(settings.SMALLESTAMOUNT, rounding=decimal.ROUND_DOWN)


def get_weekly_balance_tax_for_amount(amount):
    return (amount * settings.WEEKLYBALANCETAX).quantize(settings.SMALLESTAMOUNT, rounding=decimal.ROUND_DOWN)


def get_post_registration_tax_for_amount(amount):
    return (amount * settings.POSTTAX).quantize(settings.SMALLESTAMOUNT, rounding=decimal.ROUND_DOWN)


# --------------- ACCOUNT ACCESS ---------------
def get_random_unused_account_number_in_range(session, range_tuple):
    while True:
        number = random.randint(*range_tuple)

        try:
            get_account_from_number(session, number)
        except:
            return number


def get_smallest_unused_account_number_in_range(session, range_tuple):
    for i in xrange(*range_tuple):
        try:
            get_account_from_number(session, i)
        except ValueError:
            return i


def get_account_from_username(session, name):
    acct = session.query(Account).filter(Account.name.ilike(name)).first()

    if acct is None:
        raise ValueError("This user does not have an account.")

    return acct


def force_get_account_from_username(session, name):
    acct = session.query(Account).filter(Account.name.ilike(name)).first()

    if acct is None:
        acct = Account(name=name, number=get_random_unused_account_number_in_range(session, settings.USERACCTS),
                       bank_in_cents=int(settings.STARTINGFUNDS * 100), description="Personal Account")
        session.add(acct)
        session.commit()

    return acct


def create_non_user_account(session, description):
    acct = Account(number=get_random_unused_account_number_in_range(session, settings.COMPANYACCTS), bank_in_cents=0,
                   description=description)
    session.add(acct)
    session.commit()

    return acct


def create_government_account(session, description):
    acct = Account(number=get_smallest_unused_account_number_in_range(session, settings.GOVTACCTS), bank_in_cents=0,
                   description=description)
    session.add(acct)
    session.commit()

    return acct


def get_account_from_number(session, number):
    acct = session.query(Account).filter(Account.number == number).first()

    if acct is None:
        raise ValueError("No account with this number found.")

    return acct


def get_treasury_account(session):
    try:
        acc = get_account_from_number(session, settings.TREASURYNO)
        return acc
    except ValueError:
        acct = Account(name=settings.TREASURY, number=settings.TREASURYNO,
                       bank_in_cents=settings.TREASURYSTARTSAT * 100,
                       description="The Federal Reserve of the Yam Republic")
        session.add(acct)
        session.commit()

        return acct


def get_account_balance(account):
    return Decimal(account.bank_in_cents) / Decimal(100)


def transfer_account_money(session, from_account, to_account, amount):
    # Tax the source account
    tax = get_transfer_tax_for_amount(amount)
    send_amount = amount + tax
    if get_account_balance(from_account) >= send_amount:
        from_account.bank_in_cents -= int(send_amount * 100)
        to_account.bank_in_cents += int(amount * 100)
        get_treasury_account(session).bank_in_cents += int(tax * 100)

        session.commit()
    else:
        raise ValueError("The source account has insufficient funds for this operation.")


# --------------- POST REGISTRATION ---------------
def register_post_to_user(session, acct, post_id):
    if is_post_registered(session, post_id):
        raise ValueError("This submission is already deposited.")

    post = Post(id=post_id, owner_number=acct.number)
    session.add(post)
    session.commit()

    return post


def is_post_registered(session, post_id):
    return session.query(Post).filter(Post.id == post_id).count() > 0


# --------------- FLAIRS ---------------
def add_flair(reddit, session, account, text, css):
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


def remove_flair(reddit, session, account):
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
            raise ValueError(
                "There was an issue removing the flair from the subreddit %s. Please contact the developers.")

    account.owner_flair_text = None
    account.owner_flair_css = None
    account.owner_flair_expiration = None

    session.commit()
