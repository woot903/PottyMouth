import datetime
class PottyUtils:
    def __init__(self):
        pass

    # Load Profanity words from a text file into a list
    @staticmethod
    def load_profanity(path):
        words = []
        with open(path) as f:
            while line := f.readline().rstrip():
                words.append(line)
        return words

    @staticmethod
    def generate_OR_query(search_terms: list):
        query = ""
        for word in search_terms:
            query += (word + "|")
        return query[:-1]

    #TODO - Also Add spam filter check
    @staticmethod
    def count_profanity(body, curses, count_dict={}):
        total_count = 0
        for curse in curses:
            curse_count = body.count(curse)
            total_count += curse_count

            if curse in count_dict:
                count_dict[curse] += curse_count
            else:
                count_dict[curse] = curse_count
        return total_count, count_dict

    # Get Comments from PushShift
    @staticmethod
    def get_comments(query, time_bound_lower, time_bound_upper, api, limit=None):
        comment_data = api.search_comments(q=query, before=int(time_bound_upper), after=int(time_bound_lower), limit=limit)
        comments = comment_data.responses.copy()
        return comments

    # Gets upper and lower bound for time range (6pm MST)
    @staticmethod
    def get_time_range():
        day_diff = datetime.timedelta(days=1)
        # Runs at 17:00 UTC scheduled
        yesterday = datetime.date.today() - (day_diff * 2)
        time = datetime.time(hour=1, minute=0)
        lower = datetime.datetime.combine(yesterday, time)
        upper = lower + day_diff
        return lower, upper

    # Get Submission IDS that each comment is from
    @staticmethod
    def get_submission_ids(comments):
        submission_list_ids = []
        for i in range(len(comments)):
            submission = comments[i]["link_id"]
            submission_split = submission.split("_", 1)[1]
            submission_list_ids.append(submission_split)
        return submission_list_ids

    # Check if submissions are NSFW
    @staticmethod
    def get_nsfw_submission_ids(ids, api):
        id_tracker = ids.copy()
        submission_request = api.search_submissions(ids=ids).responses
        nsfw_submissions = []
        for submission in submission_request:
            if submission["over_18"]:
                nsfw_submissions.append(submission["id"])
                # Remove ids after we check them
            id_tracker.remove(submission["id"])
        # Any ids not found are assumed to be NSFW
        if (count := len(id_tracker)) != 0:
            print("There were " + str(count) + " submissions that appear to have been deleted. They are assumed NSFW.")
            for sub in id_tracker:
                nsfw_submissions.append(sub)
        return nsfw_submissions

    # Deletes comments by id and removes moderator comments if desired (default behavior)
    @staticmethod
    def remove_comment_by_ids(comments, ids_to_remove, remove_mods=True):
        for i in range(len(comments) - 1, -1, -1):
            c = comments[i]
            sub_id = c["link_id"].split("_", 1)[1]
            distinguished = c["distinguished"] == "moderator"
            if sub_id in ids_to_remove or (remove_mods and distinguished):
                del comments[i]
        return comments

    # Returns a dictionary of users and profanity count
    @staticmethod
    def count_profanity_in_comments(comments, curse_words):
        user_dict = {}
        most_profanity = None
        for comment in comments:
            author = comment["author"]
            body = comment["body"]

            prof_count = PottyUtils.count_profanity(body, curse_words)[0]

            if author in user_dict:
                user_dict[author] += prof_count
            else:
                user_dict[author] = prof_count

            if most_profanity is None or user_dict[author] > most_profanity[1]:
                most_profanity = (author, user_dict[author])
        return user_dict, most_profanity

    @staticmethod
    def get_estimated_count(query, yesterday_lower_epoch, yesterday_upper_epoch, api):
        count_request = api.search_comments(q=query, before=yesterday_upper_epoch, after=yesterday_lower_epoch, limit=1)
        print("test")


