import praw
import time
from datetime import datetime

import settings
import auth
from util import format_timedelta

r = praw.Reddit(
    client_id=auth.CLIENTID,
    client_secret=auth.CLIENTSECRET,
    password=auth.PW,
    username=auth.UNAME,
    user_agent=auth.AGENT
)

# TODO: Check if the bot has mod perms
for s in settings.CHAMBERS.keys():
    settings.CHAMBERS[s]["subreddit"] = r.subreddit(s)

while (True):
    votingOn = []

    # Grab submissions that are open for voting
    for name,chamber in settings.CHAMBERS.iteritems():
        subreddit = chamber["subreddit"]
        for submission in subreddit.hot():
            if not submission.stickied:
                break

            if submission.link_flair_text == settings.VOTEFLAIR:
                votingOn.append((name, submission))

    # For each open vote
    for subName, voteSubmission in votingOn:
        # Check if we have the top comment
        comment = None
        if len(voteSubmission.comments) > 0:
            comment = voteSubmission.comments[0]

        # If we don't, lets do that
        startTime = datetime.now()
        endTime = startTime + settings.VOTEDURATION
        remainingTime = endTime - startTime

        if comment is None or comment.author.name != auth.UNAME:
            untilTime = format_timedelta(remainingTime, "{days} days, {hours} hours and {minutes} minutes")
            if settings.CHAMBERS[subName]["quorum"] is not None:
                untilTime += " or until quorum is reached"

            msg = settings.VOTECOMMENTBODY % (
                ", ".join(settings.YESKEYWORDS),
                ", ".join(settings.NOKEYWORDS),
                ", ".join(settings.ABSTAINKEYWORDS),
                endTime.strftime("%A, %d %B %Y at %I:%M%p"),
                untilTime,
                settings.NOQUORUM if settings.CHAMBERS[subName]["quorum"] is None else settings.HASQUORUM % settings.CHAMBERS[subName]["quorum"],
                str(settings.CHAMBERS[subName]["quorum"]) if settings.CHAMBERS[subName]["quorum"] is not None else "N/A"
            )

            comment = voteSubmission.reply(msg)
            comment.mod.distinguish("yes", True)

            print "Starting voting on submission %s" % voteSubmission.title

            # Loop thru members to ask them to vote
            flairs = [flair for flair in voteSubmission.subreddit.flair(limit=None)]
            voters = []

            for flair in flairs:
                # Let's make sure that the user has the proper flair
                allowed = False
                for allowedFlair in settings.CHAMBERS[subName]["flairs"]:
                    if allowedFlair.lower() in flair["flair_text"].lower():
                        allowed = True
                        break

                if allowed:
                    voters.append(flair["user"])

            for voter in voters:
                msg = settings.VOTEMESSAGE % (voter.name, voteSubmission.title, voteSubmission.url)
                voter.message(settings.VOTEMESSAGEHEADER, msg)
                print "Sent reminder to voter %s" % voter.name

        startTime = datetime.fromtimestamp(comment.created_utc)
        endTime = startTime + settings.VOTEDURATION
        currentTime = datetime.now()
        remainingTime = endTime - currentTime

        # Check if we already terminated the voting here
        if comment.body.startswith(settings.ENDTAG):
            continue

        # Get the children
        comment.refresh()
        comment.replies.replace_more(None, 0)
        replies = comment.replies.list()

        # Prep the counts
        yes = []
        no = []
        idk = []
        rip = []

        voted = set()

        if len(replies) > 0:
            for reply in replies:
                # Let's make sure that the user has the proper flair
                allowed = False
                for allowedFlair in settings.CHAMBERS[subName]["flairs"]:
                    if reply.author_flair_text is not None and allowedFlair.lower() in reply.author_flair_text.lower():
                        allowed = True
                        break

                if allowed and reply.author.name not in voted:
                    body = reply.body.lower()
                    isSpoiled = True

                    for kw in settings.YESKEYWORDS:
                        if body.startswith(kw.lower()):
                            yes.append(settings.NAMELISTINGFORMAT % (reply.author.name, kw))
                            isSpoiled = False
                            break

                    if isSpoiled:
                        for kw in settings.NOKEYWORDS:
                            if body.startswith(kw.lower()):
                                no.append(settings.NAMELISTINGFORMAT % (reply.author.name, kw))
                                isSpoiled = False
                                break

                    if isSpoiled:
                        for kw in settings.ABSTAINKEYWORDS:
                            if body.startswith(kw.lower()):
                                idk.append(settings.NAMELISTINGFORMAT % (reply.author.name, kw))
                                isSpoiled = False
                                break

                    if isSpoiled:
                        rip.append(reply.author.name)

                    voted.add(reply.author.name)
                else:
                    reply.mod.remove()

        total = float(settings.CHAMBERS[subName]["size"])
        totalCast = len(yes) + len(no) + len(idk) + len(rip)

        if settings.CHAMBERS[subName]["quorum"] is not None:
            total = totalCast

        # Prepare the counted tally
        readyData = settings.VOTECOMMENTDATA % (
            totalCast,
            len(yes),
            len(yes) * 100 / total if total > 0 else 0,
            ",\n\n".join(yes) if len(yes) > 0 else "None",
            len(no),
            len(no) * 100 / total if total > 0 else 0,
            ",\n\n".join(no) if len(no) > 0 else "None",
            len(idk),
            len(idk) * 100 / total if total > 0 else 0,
            ",\n\n".join(idk) if len(idk) > 0 else "None",
            len(rip),
            len(rip) * 100 / total if total > 0 else 0,
            ",\n\n".join(rip) if len(rip) > 0 else "None"
        )

        finished = False
        if endTime <= currentTime:
            if settings.CHAMBERS[subName]["quorum"] is not None:
                if totalCast >= settings.CHAMBERS[subName]["quorum"]:
                    finished = True
            else:
                finished = True

        msg = None
        if not finished:
            untilTime = format_timedelta(remainingTime, "{days} days, {hours} hours and {minutes} minutes")
            if settings.CHAMBERS[subName]["quorum"] is not None:
                if endTime <= currentTime:
                    untilTime = "0 minutes - waiting for quorum"
                else:
                    untilTime += " or until quorum is reached"

            msg = settings.VOTECOMMENTBODY % (
                ", ".join(settings.YESKEYWORDS),
                ", ".join(settings.NOKEYWORDS),
                ", ".join(settings.ABSTAINKEYWORDS),
                endTime.strftime("%A, %d %B %Y at %I:%M%p"),
                untilTime,
                settings.NOQUORUM if settings.CHAMBERS[subName]["quorum"] is None else settings.HASQUORUM % settings.CHAMBERS[subName]["quorum"],
                (str(settings.CHAMBERS[subName]["quorum"] - total) if settings.CHAMBERS[subName]["quorum"] > total else "No") if settings.CHAMBERS[subName]["quorum"] is not None else "N/A"
            )
        else:
            msg = settings.ENDTAG + " " + (settings.VOTEENDED % (
                currentTime.strftime("%A, %d %B %Y at %I:%M%p")
            ))

            print "Ending voting on submission %s" % voteSubmission.title

        comment.edit(msg + readyData)

    time.sleep(settings.SLEEP)
