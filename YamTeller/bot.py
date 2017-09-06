import signal
import sys
import time

import praw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import auth
import controllers
import eventloop
import settings
import yamsdaq_eventloop

loopHandlers = [eventloop.loop]

if settings.STOCK_EXCHANGE_ENABLED:
    loopHandlers.append(yamsdaq_eventloop.loop)


class GracefulKiller(object):
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


if __name__ == "__main__":
    killer = GracefulKiller()

    r = praw.Reddit(
        client_id=auth.CLIENTID,
        client_secret=auth.CLIENTSECRET,
        password=auth.PW,
        username=auth.UNAME,
        user_agent=auth.AGENT
    )

    if settings.STOCK_EXCHANGE_ENABLED:
        sub = r.subreddit(settings.STOCK_EXCHANGE_SUBREDDIT)

    engine = create_engine('sqlite:///' + settings.DBPATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    controllers.get_treasury_account(session)  # Done so that the treasury account is always created first

    while True:
        inbox = r.inbox
        unread = inbox.unread(mark_read=True)
        msgsToClean = []
        for x in unread:
            msgsToClean.append(x)

        for handler in loopHandlers:
            handler(r, session)

        # Clean up the PM inbox:
        for msg in msgsToClean:
            msg.mark_read()

        if killer.kill_now:
            print 'YamTeller shutting down.'

            if session is not None:
                session.close()

            sys.exit(0)

        time.sleep(settings.SLEEP)
