import praw
from PottyUtils import PottyUtils
from datetime import datetime


class RedditBot:
    def __init__(self, botname="PottyBot"):
        self.reddit = praw.Reddit(botname)
        self.post_template = "### Congratulations to the Dirtiest Mouth on Reddit (10/3/22)\n# u/{user}\n## They commented profanity **{totalprofanity}** times between {starttime} and {endtime}\n| Curse Word | Number of Occurrences |\n| :----------: | :---------------------: |\n{tablevalues}\n---\n^(BEEP BOOP I am a BOT. Created by /u/no_potty_talk)"

    def generate_curse_table(self, curse_dict):
        table_string = ""
        for word in curse_dict:
            temp = "| >!" + str(word) + "!< | " + str(curse_dict[word]) + "|\n"
            table_string += temp
        return table_string

    def post_potty_talk(self, user, start: datetime, end: datetime, total_curses, curse_dict):
        sub = self.reddit.subreddit("pottymouth")
        start_date = start.strftime("%m/%d/%y")
        end_date = end.strftime("%m/%d/%y")
        curse_table = self.generate_curse_table(curse_dict)
        post_body = self.post_template.format(user=user, totalprofanity=total_curses, starttime=start_date, endtime=end_date, tablevalues=curse_table)
        title = "Congratulations to " + str(user) + "! They cursed the most during a 24 hour period on Reddit! ({startdate} - {enddate})".format(startdate=start_date, enddate=end_date)
        sub.submit(title=title, selftext=post_body, send_replies=False)



