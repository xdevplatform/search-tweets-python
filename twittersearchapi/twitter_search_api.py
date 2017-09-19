# This Python file uses the following encoding: utf-8

from functools import reduce
import time
import re
import datetime
import requests
try:
    import ujson as json
except ImportError:
    import json
from tweet_parser.tweet import Tweet

from .utils import *

BASE_URL = "https://gnip-api.twitter.com/search/"
BASE_ENDPOINT = "{api}/accounts/{account_name}/{label}"


def gen_endpoint(search_api, account_name, label, count_endpoint=False, **kwargs):
    """
    Creates the endpoint URL from discrete information.

    Args:
        search_api (str): the api to use, `30day` or `fullarchive`
        account_name (str): the master account for the user
        label (str): stream within an account to connect
        count_endpoint (bool): defines using the Counts endpoint over the
            default data endpoint.

    Returns:
        str: well-formed url for a connection.

    Example:
        >>> search_api = "30day"
        >>> account_name = "montypython"
        >>> endpoint_label = "python.json"
        >>> gen_endpoint(search_api, account_name, endpoint_label, count_endpoint=False)
        'https://gnip-api.twitter.com/search/30day/accounts/montypython/python.json'
        >>> gen_endpoint(search_api, account_name, endpoint_label, count_endpoint=True)
        'https://gnip-api.twitter.com/search/30day/accounts/montypython/python/counts.json'
    """
    # helper for modifying count data
    label = label if not label.endswith(".json") else label.split(".")[0]
    endpoint = BASE_ENDPOINT.format(api=search_api,
                                    account_name=account_name,
                                    label=label)
    if count_endpoint:
        endpoint = endpoint + "/counts.json"
    else:
        endpoint = endpoint + ".json"

    endpoint = BASE_URL + endpoint
    return endpoint


def make_session(username, password):
    """Creates a Requests Session for use.

    Args:
        username (str): username for the session
        password (str): password for the user
    """

    session = requests.Session()
    session.headers = {'Accept-encoding': 'gzip'}
    session.auth = username, password
    return session


@retry
def request(session, url, rule_payload, **kwargs):
    """
    Executes a request with the given payload and arguments.

    Args:
        session (requests.Session): the valid session object
        url (str): Valid API endpoint
        rule_payload (str or dict): rule package for the POST. if you pass a
            dictionary, it will be converted into JSON.
    """
    if isinstance(rule_payload, dict):
        rule_payload = json.dumps(rule_payload)
    result = session.post(url, data=rule_payload)
    return result


class ResultStream:
    """Class to represent an API query that handles two major functionality
    pieces: wrapping metadata around a specific API call and automatic
    pagination of results.
    """

    def __init__(self, username, password, url, rule_payload,
                 max_tweets=1000, tweetify=True):
        """
        Args:
            username (str): username
            password (str): password
            url (str): API endpoint; should be generated using the
                `gen_endpoint` function.
            rule_payload (json or dict): payload for the post request
            max_tweets (int): max results that will be fetched from the API.
            tweetify (bool): If you are grabbing tweets and not counts, use the
                tweet parser library to convert each raw tweet package to a Tweet
                with lazy properties.

        """

        self.username = username
        self.password = password
        self.url = url
        if isinstance(rule_payload, str):
            rule_payload = json.loads(rule_payload)
        self.rule_payload = rule_payload
        self.tweetify = tweetify
        self.max_tweets = max_tweets

        self.total_results = 0
        self.n_requests = 0
        self.session = None
        self.current_tweets = None
        self.next_token = None
        self.stream_started = False
        self._tweet_func = Tweet if tweetify else lambda x: x


    def stream(self):
        """
        Handles pagination of results. Uses new yield from syntax.
        """
        self.init_session()
        self.check_counts()
        self.execute_request()
        self.stream_started = True
        while True:
            for tweet in self.current_tweets:
                if self.total_results >= self.max_tweets:
                    break
                yield self._tweet_func(tweet)
                self.total_results += 1

            if self.next_token and self.total_results < self.max_tweets:
                self.rule_payload = merge_dicts(self.rule_payload, ({"next": self.next_token}))
                print("paging; total requests read so far: {}".format(self.n_requests))
                self.execute_request()
            else:
                break
        print("ending stream at {} tweets".format(self.total_results))

    def init_session(self):
        if self.session:
            self.session.close()
        self.session = make_session(self.username, self.password)

    def check_counts(self):
        if "counts" in re.split("[/.]", self.url):
            print("disabling tweet parsing due to counts api usage")
            self._tweet_func = lambda x: x

    def end_stream(self):
        self.current_tweets = None
        self.session.close()

    def execute_request(self):
        if self.n_requests % 20 == 0 and self.n_requests > 1:
            print("refreshing session")
            self.init_session()
        resp = request(session=self.session,
                       url=self.url,
                       rule_payload=self.rule_payload)
        self.n_requests += 1
        resp = json.loads(resp.content.decode(resp.encoding))
        self.next_token = resp.get("next", None)
        self.current_tweets = resp["results"]

    def __repr__(self):
        repr_keys = ["username", "url", "rule_payload", "tweetify", "max_tweets"]
        str_ = json.dumps(dict([(k, self.__dict__.get(k)) for k in repr_keys]), indent=4)
        str_ = "ResultStream params: \n\t" + str_
        return str_
