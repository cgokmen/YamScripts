import controllers
from parsers import get_pm_parser
from models import Account
import datetime


def loop(r, session):
    # Check PMs for account-related requests
    inbox = r.inbox
    unread = inbox.unread(mark_read=True)

    for msg in unread:
        try:
            author = msg.author
            body = msg.body

            print "Processing msg from %s: %s" % (author, body)

            command = body.split(' ', 1)[0]
        except:
            continue

        try:
            # Before running the command lets make sure the user has an account first
            controllers.force_get_account_from_username(session, author.name)

            handler = get_pm_parser(command)
            has_permission = handler.hasPermission

            if not has_permission(author):
                raise ValueError("You do not have the permission to use this command.")

            out = handler(r, session, author, body)
        except ValueError as e:
            out = "An error occurred: %s" % e.message

        msg.reply(out)

    for acct in session.query(Account).filter(Account.owner_flair_expiration.isnot(None),
                                              Account.owner_flair_expiration <= datetime.datetime.now()):
        controllers.remove_flair(r, session, acct)
