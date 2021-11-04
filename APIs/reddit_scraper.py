import json

import numpy as np
import pandas as pd
import psaw
from alive_progress import alive_bar
from psaw import PushshiftAPI

# # deps: psaw, pandas, numpy

## define the class


class RedditScraper(object):
    """


    """

    def __init__(self, subred, queries):

        self.subr = subred

        self.subq = queries

        self.reddit_api = PushshiftAPI()

    def extract_threads(self):

        ls = []

        with alive_bar(100) as bar:

            for channel in self.subr:

                for query in self.subq:

                    generator_obj_1 = self.reddit_api.search_comments(
                        q=query, subreddit=channel)

                    submissions = pd.DataFrame(
                        [comment.d_ for comment in generator_obj_1])

                    submissions["Search_Term"] = query

                    submissions["Search_Subreddit"] = channel

                    ls.append(submissions)

                    bar()

                    yield print(
                        "Comment extraction complete for {} in {}".format(
                            query, channel))  ## find a way to log to user

            df = pd.concat(ls)

            csv_out = df.to_csv("RedditComments-8-24.csv")

            json_out = df.to_json(orient="records")

            return csv_out, json_out

    ##############

    def extract_comments(self):

        ls = []

        with alive_bar(100) as bar:

            for channel in self.subr:

                for query in self.subq:

                    generator_obj = self.reddit_api.search_submissions(
                        q=query, subreddit=channel)

                    submissions = pd.DataFrame(
                        [submission.d_ for submission in generator_obj])

                    submissions["Search_Term"] = query

                    submissions["Search_Subreddit"] = channel

                    ls.append(submissions)

                    bar()

                    yield print(
                        "Thread extraction complete for {} in {}".format(
                            query, channel))

            df = pd.concat(ls)

            csv_out = df.to_csv("RedditThreads-8-24.csv")

            json_out = df.to_json(orient="records")

            return csv_out, json_out

    def run_scraper(self):

        dl_csv_threads, dl_json_threads = self.extract_threads()

        dl_csv_comms, dl_json_comms = self.extract_comments()

        return dl_csv_comms, dl_json_threads, dl_json_comms, dl_csv_threads


###########

if __name__ == "__main__":

    pass
