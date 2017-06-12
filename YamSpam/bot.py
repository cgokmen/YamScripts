import praw

import auth

import term2 as term

r = praw.Reddit(
    client_id=auth.CLIENTID,
    client_secret=auth.CLIENTSECRET,
    password=auth.PW,
    username=auth.UNAME,
    user_agent=auth.AGENT
)

TITLE = "YamRepublic Senate Vote on Lower Court Amendment"

MESSAGE = """
Dear Senator %s,

Senate voting on the Amendment to the Lower Courts Bill detailing new procedures as well as giving Judges more authority on sentencing has commenced after the House passed the bill.

This bill is our administration's complement to the Yam Legal Act Bill presented by the Conservative Party in the Senate. These two bills together will form the cornerstone of our legal system.

Now, we need your vote to continue the process. To vote, please respond to [this comment](https://www.reddit.com/r/YamSenate/comments/6gs67c/senate_vote_on_hr_2017004_amendment_to_the_lower/disltk9/).

**You need to reply DIRECTLY TO THE LINKED COMMENT BY THE BOT. Replying to the post itself will result in your vote not being counted.**

*Also make sure you are using one of the keywords highlighted in the bot's comment to vote and not a random word of your choice like YEET or something.*

Thank you,

sultanskyman

Vice President of the Yam Republic
"""

for person in term.senators:
    try:
        redditor = r.redditor(person)
        redditor.message(TITLE, MESSAGE % person)
        print("%s has been messaged." % person)
    except:
        print("Redditor %s could not be messaged." % person)

print("Done!")
