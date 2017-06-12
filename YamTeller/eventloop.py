import logging
import controllers
from parsers import getPMParser
from models import Account
import datetime

def loop(r, session):
    # Check PMs for account-related requests
    inbox = r.inbox
    unread = inbox.unread(mark_read=True)

    for msg in unread:
        author = msg.author
        body = msg.body

        logging.info("Processing msg from %s: %s" % (author, body))

        command = body.split(' ', 1)[0]

        try:
            # Before running the command lets make sure the user has an account first
            controllers.forceGetAccountFromUsername(session, author.name)

            commandFn, commandHelp, commandPerms = getPMParser(command)

            if not commandPerms(author):
                raise ValueError("You do not have the permission to use this command.")

            out = commandFn(r, session, author, body)
        except ValueError as e:
            out = "An error occurred: %s" % e.message

        msg.reply(out)

    for acct in session.query(Account).filter(Account.owner_flair_expiration.isnot(
            None), Account.owner_flair_expiration <= datetime.datetime.now()):
        controllers.removeFlair(r, session, acct)