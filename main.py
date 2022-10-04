import datetime

from pmaw import PushshiftAPI
from PottyUtils import PottyUtils
import time
from RedditBot import RedditBot

class PottyMouthBot:
    def __init__(self):
        self.curse_file_path = "curse_words.txt"

    def main(self):
        # Variable Setup
        api = PushshiftAPI()
        # time_range = PottyUtils.get_time_range()
        time_range = [datetime.datetime.fromtimestamp(time.time() - 86400), datetime.datetime.fromtimestamp(time.time() - 86400 + (60 * 5))]
        yesterday_lower = time_range[0]
        yesterday_upper = time_range[1]
        yesterday_lower_epoch = int(yesterday_lower.timestamp())
        yesterday_upper_epoch = int(yesterday_upper.timestamp())
        curse_words = PottyUtils.load_from_path(self.curse_file_path)
        query = PottyUtils.generate_OR_query(curse_words)

        print("Checking for profanity usage between " + time.strftime("%m/%d/%Y - %H:%M:%S", time.localtime(yesterday_lower_epoch)) + " and " + time.strftime("%m/%d/%Y - %H:%M:%S", time.localtime(yesterday_upper_epoch)) + " on Reddit...")
        # print("Getting initial estimate... ", end='')
        # estimate = PottyUtils.get_estimated_count(query, yesterday_lower_epoch, yesterday_upper_epoch, api)
        # print("found " + str(estimate) + " comments. Querying them now...")
        comments = PottyUtils.get_comments(query, yesterday_lower_epoch, yesterday_upper_epoch, api, limit=None)
        print("Query Complete. Downloaded " + str(len(comments)) + " Comments.\nQuerying Parent Submissions...", end='')

        submission_list_ids = PottyUtils.get_submission_ids(comments)
        nsfw_submission_ids = PottyUtils.get_nsfw_submission_ids(submission_list_ids, api)
        print("Success. Filtering...", end='')
        comments = PottyUtils.remove_comment_by_ids(comments, nsfw_submission_ids)
        print("Success. Counting profanity usage...")
        profanity = PottyUtils.count_profanity_in_comments(comments, curse_words)
        most_curses = profanity[1]
        if most_curses is not None:
            print("Winner found. Gathering information about winner...")
            winner_comment_request = api.search_comments(q=query, author=most_curses[0], before=int(yesterday_upper_epoch), after=int(yesterday_lower_epoch), limit=None)
            print(str(most_curses[0]) + " is the filthiest user during this time period with " + str(most_curses[1]) + " instacnes of profanity found.")
            profantiy_count_by_curse = {}
            for c in winner_comment_request.responses:
                c_body = c["body"]
                print("Comment Body: " + c["body"])
                PottyUtils.count_profanity(c_body, curse_words, profantiy_count_by_curse)
            print("----------------------------------")
            for curse in curse_words:
                print(str(curse) + ":" + str(profantiy_count_by_curse[curse]))

            bot = RedditBot()
            bot.post_potty_talk(most_curses[0], yesterday_lower, yesterday_upper, most_curses[1], profantiy_count_by_curse)
        else:
            print("Error: No cursing found in timeframe")




if __name__ == '__main__':
    PottyMouthBot().main()
