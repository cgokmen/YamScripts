from datetime import timedelta

VOTEFLAIR = "VOTING"

YESKEYWORDS = ["Yea", "Yes", "In favor"]
NOKEYWORDS = ["Nay", "No", "Against"]
ABSTAINKEYWORDS = ["Abstaining", "I abstain", "Abstention"]

CHAMBERS = {
    "YamSenate": {
        "quorum": None,
        "size": 15,
        "flairs": ["Senator"]
    },
    "HouseOfYams": {
        "quorum": 25,
        "size": 50,
        "flairs": ["Representative"]
    }
}

VOTEDURATION = timedelta(0,0,0,0,3) # 1 day

VOTECOMMENTBODY = """
This comment is automatically populated by the **YamVoting** bot.

To vote, reply to this comment.

Your vote is counted according to the first word of your reply, after that you can write whatever you want.

To vote in favor, start your reply with one of **%s**. To vote against, start with one of **%s**. To abstain, start with one of **%s**. All votes are case insensitive. Votes starting with other phrases will be considered spoiled, which are equivalent to abstentions.

Vote counts are refreshed once every minute. Feel free to change your vote as you see fit before end of the voting period.

Voting ends %s.

Time remaining: %s.

%s

%s more votes needed to reach quorum.

&nbsp;
"""

VOTECOMMENTDATA = """

**-- VOTE STATUS --**

Total votes cast: %d

&nbsp;

**In favor:** %d (%.2f%%)

%s

&nbsp;

**Against:** %d (%.2f%%)

%s

&nbsp;

**Abstentions:** %d (%.2f%%)

%s

&nbsp;

**Spoiled:** %d (%.2f%%)

%s
"""

VOTEENDED = """
This comment is automatically populated by the **YamVoting** bot.

&nbsp;

Voting on this submission ended %s. Here are the results:

&nbsp;
"""

ENDTAG = "(ENDED)"

NAMELISTINGFORMAT = '%s ("%s")'

HASQUORUM = "This chamber has a quorum requirement of %d members that must be reached before voting ends."
NOQUORUM = "This chamber does not have a quorum requirement."

SLEEP = 20 # Seconds
