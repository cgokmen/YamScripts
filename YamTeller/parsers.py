import settings
import controllers
import util

PM_PARSERS = {}


# --------------- STANDARD ECONOMY FUNCTIONS ---------------

def standard_economy_permissions(user):
    return user.name in settings.ALPHATESTERS


def send_by_username(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 3:
        raise ValueError("Invalid number of parameters supplied to SNDU. Help: " + send_by_username.help)

    str_amount = tokens[2]
    amount = util.parse_amount(str_amount)

    username = tokens[1]
    destination_account = controllers.get_account_from_username(session, username)
    source_account = controllers.force_get_account_from_username(session, author.name)

    controllers.transfer_account_money(session, source_account, destination_account, amount)
    tax_paid = controllers.get_transfer_tax_for_amount(amount)

    redditor = reddit.redditor(username)
    if redditor is not None:
        redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (
            amount, source_account.number,
            source_account.name if source_account.name is not None else source_account.description))

    return "Transaction completed successfully. You transferred Y%.2f and paid Y%.2f in transaction tax. You have Y%.2f remaining in your account." % (
        amount, tax_paid, controllers.get_account_balance(source_account))


send_by_username.help = "Sends money to the account owned by the provided user. Format: SNDU [username] [amount]"
send_by_username.hasPermission = standard_economy_permissions
PM_PARSERS['SNDU'] = send_by_username


def send_by_account_number(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 3:
        raise ValueError("Invalid number of parameters supplied to SNDA. Help: " + send_by_account_number.help)

    str_amount = tokens[2]
    amount = util.parse_amount(str_amount)

    str_account_number = tokens[1]
    try:
        account_number = int(str_account_number)
    except:
        raise ValueError("Invalid account number: account numbers need to be integers.")

    destination_account = controllers.get_account_from_number(session, account_number)
    source_account = controllers.force_get_account_from_username(session, author.name)

    controllers.transfer_account_money(session, source_account, destination_account, amount)
    tax_paid = controllers.get_transfer_tax_for_amount(amount)

    try:
        username = destination_account.name
        if username is not None:
            redditor = reddit.redditor(username)
            if redditor is not None:
                redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (
                    amount, source_account.number,
                    source_account.name if source_account.name is not None else source_account.description))
    except:
        pass

    return "Transaction completed successfully. You transferred Y%.2f and paid Y%.2f in transaction tax. You have Y%.2f remaining in your account." % (
        amount, tax_paid, controllers.get_account_balance(source_account))


send_by_account_number.help = "Sends money to the account marked with the provided account number. Format: SNDA [account number] [amount]"
send_by_account_number.hasPermission = standard_economy_permissions
PM_PARSERS['SNDA'] = send_by_account_number


def show_balance(reddit, session, author, body):
    account = controllers.force_get_account_from_username(session, author.name)
    return "You have Y%.2f remaining in your account with number %08d." % (
        controllers.get_account_balance(account), account.number)


show_balance.help = "Shows your bank balance and account number. Format: BALN"
show_balance.hasPermission = standard_economy_permissions
PM_PARSERS['BALN'] = show_balance


def show_federal_reserve_balance(reddit, session, author, body):
    return "The Federal Reserve has a balance of Y%.2f." % controllers.get_account_balance(
        controllers.get_treasury_account(session))


show_federal_reserve_balance.help = "Shows the balance of the Federal Reserve. Format: FBAL"
show_federal_reserve_balance.hasPermission = standard_economy_permissions
PM_PARSERS['FBAL'] = show_federal_reserve_balance


def yamecon_help(reddit, session, author, body):
    output = "YamTellerBot Help\n\nTo run any command, send it to u/YamTellerBot in a message. The title does not matter.\n\nHere is a list of commands:\n\n"
    for key, handler in sorted(PM_PARSERS.iteritems()):
        perms = handler.hasPermission
        if perms is None or perms(author):
            output += "* %s %s\n" % (key, handler.hasPermission)

    return output


yamecon_help.help = "Shows economy command help. Format: HELP"
yamecon_help.hasPermission = standard_economy_permissions
PM_PARSERS['HELP'] = yamecon_help


# --------------- ADMIN FUNCTIONS ---------------
def has_admin_transfer_perms(user):
    return settings.FEDERAL_RESERVE_TRANSFERS_ENABLED and (user.name in settings.FRTRANSFERPERMS)


def admin_payment_to_user(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 4:
        raise ValueError("Invalid number of parameters supplied to FEDU. Help: " + admin_payment_to_user.help)

    str_amount = tokens[3]
    amount = util.parse_amount(str_amount)

    # From Acct
    str_source_account_number = tokens[1]
    try:
        source_account_number = int(str_source_account_number)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    source_account = controllers.get_account_from_number(session, source_account_number)

    if source_account is None:
        raise ValueError("Source account with this number not found.")

    if source_account.name is not None:
        raise ValueError("FEDU can only be used to transfer from non-user accounts.")

    # To Acct
    destination_username = tokens[2]
    destination_account = controllers.get_account_from_username(session, destination_username)

    controllers.transfer_account_money(session, source_account, destination_account, amount)
    tax_paid = controllers.get_transfer_tax_for_amount(amount)

    redditor = reddit.redditor(destination_username)
    if redditor is not None:
        redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (
            amount, source_account.number,
            source_account.name if source_account.name is not None else source_account.description))

    return "Transaction completed successfully. You transferred Y%.2f and Y%.2f was paid in transaction tax. There is Y%.2f remaining in the source account." % (
        amount, tax_paid, controllers.get_account_balance(source_account))


admin_payment_to_user.help = "Transfers money to a given user's bank account from a provided non-user bank account. Format: FEDU [from account number] [to username] [amount]"
admin_payment_to_user.hasPermission = has_admin_transfer_perms
PM_PARSERS['FEDU'] = admin_payment_to_user


def admin_payment_to_account(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 4:
        raise ValueError("Invalid number of parameters supplied to FEDA. Help: " + admin_payment_to_account.help)

    str_amount = tokens[3]
    amount = util.parse_amount(str_amount)

    # From Acct
    str_source_account_number = tokens[1]
    try:
        source_account_number = int(str_source_account_number)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    try:
        source_account = controllers.get_account_from_number(session, source_account_number)
    except:
        raise ValueError("Source account with this number not found.")

    if source_account.name is not None:
        raise ValueError("FEDA can only be used to transfer from non-user accounts.")

    # To Acct
    str_destination_account_number = tokens[2]
    try:
        destination_account_number = int(str_destination_account_number)
    except:
        raise ValueError("Invalid destination account number: account numbers need to be integers.")

    try:
        destination_account = controllers.get_account_from_number(session, destination_account_number)
    except:
        raise ValueError("Destination account with this number not found.")

    controllers.transfer_account_money(session, source_account, destination_account, amount)
    tax_paid = controllers.get_transfer_tax_for_amount(amount)

    username = destination_account.name
    try:
        if username is not None:
            redditor = reddit.redditor(username)
            if redditor is not None:
                redditor.message("You have received funds!", "You have received Y%.2f from account %08d: %s" % (
                    amount, source_account.number,
                    source_account.name if source_account.name is not None else source_account.description))
    except:
        pass

    return "Transaction completed successfully. You transferred Y%.2f and Y%.2f was paid in transaction tax. There is Y%.2f remaining in the source account." % (
        amount, tax_paid, controllers.get_account_balance(source_account))


admin_payment_to_account.help = "Transfers money to a given bank account from a provided non-user bank account. Format: FEDU [from account number] [to account number] [amount]"
admin_payment_to_account.hasPermission = has_admin_transfer_perms
PM_PARSERS['FEDA'] = admin_payment_to_account


def admin_show_account_balance(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FEDB. Help: " + admin_show_account_balance.help)

    str_account_number = tokens[1]
    try:
        account_number = int(str_account_number)
    except:
        raise ValueError("Invalid source account number: account numbers need to be integers.")

    try:
        account = controllers.get_account_from_number(session, account_number)
    except:
        raise ValueError("Source account with this number not found.")

    if account.name is not None:
        raise ValueError("FEDB can only be used to look up the balance of non-user accounts.")

    balance = controllers.get_account_balance(account)

    return "The balance of account %08d (%s) is Y%.2f." % (account_number, account.description, balance)


admin_show_account_balance.help = "Shows the balance of a non-user bank account. Format: FEDB [account number]"
admin_show_account_balance.hasPermission = has_admin_transfer_perms
PM_PARSERS['FEDB'] = admin_show_account_balance


def admin_create_non_user_account(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTA. Help: " + admin_create_non_user_account.help)

    description = tokens[1]
    account = controllers.create_non_user_account(session, description)

    return "New account created. Account number: %08d, description: %s" % (account.number, account.description)


admin_create_non_user_account.help = "Creates a non-user bank account for use by parties and enterprises. The account description should not contain spaces. Format: CRTA [account description]"
admin_create_non_user_account.hasPermission = has_admin_transfer_perms
PM_PARSERS['CRTA'] = admin_create_non_user_account


def admin_create_user_account(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTU. Help: " + admin_create_user_account.help)

    username = tokens[1]

    try:
        redditor = reddit.redditor(username)
        if redditor is None:
            raise ValueError("No such Redditor found.")
    except:
        raise ValueError("No such Redditor found.")

    try:
        existing_account = controllers.get_account_from_username(session, username)
    except:
        pass
    else:
        raise ValueError("This user already has a bank account. Account number: %08d" % existing_account.number)

    account = controllers.force_get_account_from_username(session, username)

    return "New user account created. Account number: %08d, username: %s" % (account.number, account.name)


admin_create_user_account.help = "Creates an account for a user other than the author of the message. Format: CRTU [Reddit username without u/]"
admin_create_user_account.hasPermission = has_admin_transfer_perms
PM_PARSERS['CRTU'] = admin_create_user_account


def admin_create_government_account(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to CRTG. Help: " + admin_create_government_account.help)

    description = tokens[1]
    account = controllers.create_government_account(session, description)

    return "New government account created. Account number: %08d, description: %s" % (
        account.number, account.description)


admin_create_government_account.help = "Creates a non-user bank account for use by Government Institutions. These accounts have 10000000-level numbers. The account description should not contain spaces. Format: CRTG [account description]"
admin_create_government_account.hasPermission = has_admin_transfer_perms
PM_PARSERS['CRTG'] = admin_create_government_account


# --------------- POST EVALUATION & FLAIR SYSTEM FUNCTIONS ---------------
def has_post_evaluation_permissions(user):
    return settings.POST_EVALUATION_ENABLED


def deposit_post(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FDPT. Help: " + deposit_post.help)

    url = tokens[1]
    try:
        submission = reddit.submission(url=url)
        if submission is None:
            raise ValueError(
                "No submission found at this URL. If the post is a link post, be sure to post the URL of the Reddit post (get the comments URL) and not the URL of the link.")
    except:
        raise ValueError(
            "No submission found at this URL. If the post is a link post, be sure to post the URL of the Reddit post (get the comments URL) and not the URL of the link.")

    subreddit = submission.subreddit
    if subreddit.display_name.lower() not in settings.SUBREDDITMULTIPLIERS:
        raise ValueError("Submission in subreddit %s are not accepted by the Yam Treasury." % subreddit.display_name)

    if submission.author != author:
        raise ValueError("You can only deposit submissions you submitted.")

    account = controllers.force_get_account_from_username(session, author.name)
    controllers.register_post_to_user(session, account, submission.id)

    score = submission.score
    multiplier = settings.SUBREDDITMULTIPLIERS[subreddit.display_name.lower()]
    amount = score * multiplier

    post_deposit_tax = controllers.get_post_registration_tax_for_amount(amount)
    amount_after_tax = amount - post_deposit_tax

    controllers.transfer_account_money(session, controllers.get_treasury_account(session), account, amount_after_tax)

    return "You have deposited the submission with the ID %s. At Y%.2f per upvote in the subreddit /r/%s, you received Y%.2f for the %d upvotes on your submission after paying Y%.2f in deposit tax." \
           % (submission.id, multiplier, subreddit.display_name, amount_after_tax, score, post_deposit_tax)


deposit_post.help = "Deposits a Reddit post's upvote values into the user's bank account. Format: FDPT [post url]"
deposit_post.hasPermission = has_post_evaluation_permissions
PM_PARSERS['FDPT'] = deposit_post


def purchase_flair(reddit, session, author, body):
    tokens = body.split()
    if len(tokens) != 2:
        raise ValueError("Invalid number of parameters supplied to FPRS. Help: " + purchase_flair.help)

    try:
        flair_id = int(tokens[1])
    except:
        raise ValueError("The second parameter needs to be the number representing the flair you want to purchase.")

    if flair_id not in settings.FLAIRS:
        raise ValueError("A flair with this ID does not exist.")

    text, css, price = settings.FLAIRS[flair_id]

    account = controllers.force_get_account_from_username(session, author.name)
    balance = controllers.get_account_balance(account)
    if balance < price:
        raise ValueError("You cannot afford this flair: it costs Y%.2f but you only have Y%.2f" % (price, balance))

    controllers.add_flair(reddit, session, account, text, css)
    controllers.transfer_account_money(session, account, controllers.get_treasury_account(session), price)
    tax_paid = controllers.get_transfer_tax_for_amount(price)

    expiration = account.owner_flair_expiration.strftime("%A, %d %B %Y")
    return "You have purchased the %s flair for Y%.2f and paid Y%.2f in transaction tax. It will expire on %s. You have Y%.2f remaining in your account." % (
        text, price, tax_paid, expiration, controllers.get_account_balance(account))


purchase_flair.help = "Purchases a /r/YamRepublic flair using funds from the user's bank account. Format: FPRS [flair number]"
purchase_flair.hasPermission = has_post_evaluation_permissions
PM_PARSERS['FPRS'] = purchase_flair


def show_current_flair(reddit, session, author, body):
    account = controllers.force_get_account_from_username(session, author.name)
    text = account.owner_flair_text

    if text is None:
        return "You currently do not own a flair."

    expiration = account.owner_flair_expiration.strftime("%A, %d %B %Y")

    return "You currently own the %s flair. It will expire on %s." % (text, expiration)


show_current_flair.help = "Shows information about the user's current flair. Format: FQRY"
show_current_flair.hasPermission = has_post_evaluation_permissions
PM_PARSERS['FQRY'] = show_current_flair


def list_available_flairs(reddit, session, author, body):
    flairs = ["#%d: %s for Y%.2f weekly" % (flair_id, name, price) for flair_id, (name, css, price) in
              settings.FLAIRS.iteritems()]

    return "Here is a list of purchasable flairs: \n" + "\n".join(flairs)


list_available_flairs.help = "Lists purchasable flairs. Format: FLST"
list_available_flairs.hasPermission = has_post_evaluation_permissions
PM_PARSERS['FLST'] = list_available_flairs


def delete_flair(reddit, session, author, body):
    acct = controllers.force_get_account_from_username(session, author.name)
    controllers.remove_flair(reddit, session, acct)

    return "Your current flair has been successfully deleted."


delete_flair.help = "Deletes the user's current flair without a refund so that he can purchase a new one. Format: FDEL"
delete_flair.hasPermission = has_post_evaluation_permissions
PM_PARSERS['FDEL'] = delete_flair


# --------------- AUXILLIARY FUNCTIONS ---------------

def default_pm_parser(_, a, b, c):
    return "This command does not exist. Please send a message starting with the word HELP to see the commands."


default_pm_parser.help = ""
default_pm_parser.hasPermission = lambda x: True


def get_pm_parser(command):
    return PM_PARSERS.get(command.upper(), default_pm_parser)
