# -*- coding: utf-8 -*-
# Copyright 2021 Twitter, Inc.
# Licensed under the MIT License
# https://opensource.org/licenses/MIT
"""
This module contains the request handing and actual API wrapping functionality.
Its core method is the ``ResultStream`` object, which takes the API call
arguments and returns a stream of results to the user.
"""

import time
import logging
import requests
from urllib.parse import urlencode
try:
    import ujson as json
except ImportError:
    import json

from .utils import merge_dicts
from .api_utils import infer_endpoint, change_to_count_endpoint
from collections import defaultdict

from ._version import VERSION

logger = logging.getLogger(__name__)


def make_session(bearer_token=None, extra_headers_dict=None):
    """Creates a Requests Session for use. Accepts a bearer token
    for v2.
    Args:
        bearer_token (str): token for a v2 user.
    """

    if bearer_token is None:
        logger.error("No authentication information provided; "
                     "please check your object")
        raise KeyError

    session = requests.Session()
    session.trust_env = False
    headers = {'Accept-encoding': 'gzip',
               'User-Agent': 'twitterdev-search-tweets-python-labs/' + VERSION}

    if bearer_token:
        logger.info("using bearer token for authentication")
        headers['Authorization'] = "Bearer {}".format(bearer_token)
        session.headers = headers

    if extra_headers_dict:
        headers.update(extra_headers_dict)
    return session

def retry(func):
    """
    Decorator to handle API retries and exceptions. Defaults to five retries.
    Rate-limit (429) and server-side errors (5XX) implement a retry design.
    Other 4XX errors are a 'one and done' type error.
    Retries implement an exponential backoff...
    Args:
        func (function): function for decoration
    Returns:
        decorated function
    """
    def retried_func(*args, **kwargs):
        max_tries = 10
        tries = 0
        total_sleep_seconds = 0

        while True:
            try:
                resp = func(*args, **kwargs)

            except requests.exceptions.ConnectionError as exc:
                exc.msg = "Connection error for session; exiting"
                raise exc

            except requests.exceptions.HTTPError as exc:
                exc.msg = "HTTP error for session; exiting"
                raise exc

            if resp.status_code != 200 and tries < max_tries:

                tries += 1

                logger.error(f" HTTP Error code: {resp.status_code}: {resp.text} | {resp.reason}")
                logger.error(f" Request payload: {kwargs['request_parameters']}")

                if resp.status_code == 429:
                    logger.error("Rate limit hit... Will retry...")
                    #Expontential backoff, but within a 15-minute (900 seconds) period. No sense in backing off for more than 15 minutes.
                    sleep_seconds = min(((tries * 2) ** 2), max(900 - total_sleep_seconds,30))
                    total_sleep_seconds = total_sleep_seconds + sleep_seconds

                elif resp.status_code >= 500:
                    logger.error("Server-side error... Will retry...")
                    sleep_seconds = 30
                else:
                    #Other errors are a "one and done", no use in retrying error...
                    logger.error('Quitting... ')
                    raise requests.exceptions.HTTPError


                logger.error(f"Will retry in {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)
                continue

            break

        return resp

    return retried_func


@retry
def request(session, url, request_parameters, **kwargs):
    """
    Executes a request with the given payload and arguments.
    Args:
        session (requests.Session): the valid session object
        url (str): Valid API endpoint
        request_parameters (str or dict): rule package for the POST. If you pass a
            dictionary, it will be converted into JSON.
    """

    if isinstance(request_parameters, dict):
        request_parameters = json.dumps(request_parameters)
    logger.debug("sending request")

    request_json = json.loads(request_parameters)

    #Using POST command, not yet supported in v2.
    #result = session.post(url, data=request_parameters, **kwargs)

    #New v2-specific code in support of GET requests.
    request_url = urlencode(request_json)
    url = f"{url}?{request_url}"

    result = session.get(url, **kwargs)
    return result


class ResultStream:
    """
    Class to represent an API query that handles two major functionality
    pieces: wrapping metadata around a specific API call and automatic
    pagination of results.
    Args:
        bearer_token (str): bearer token for v2.

        endpoint (str): API endpoint.

        request_parameters (json or dict): payload for the post request

        max_tweets (int): max number results that will be returned from this
        instance. Note that this can be slightly lower than the total returned
        from the API call  - e.g., setting ``max_tweets = 10`` would return
        ten results, but an API call will return at minimum 100 results by default.

        max_requests (int): A hard cutoff for the number of API calls this
        instance will make. Good for testing in v2 environment.

        extra_headers_dict (dict): custom headers to add
    Example:
        >>> rs = ResultStream(**search_args, request_parameters=rule, max_pages=1)
        >>> results = list(rs.stream())
    """
    # leaving this here to have an API call counter for ALL objects in your
    # session, helping with usage of the convenience functions in the library.
    session_request_counter = 0

    def __init__(self, endpoint, request_parameters, bearer_token=None, extra_headers_dict=None, max_tweets=500,
                 max_requests=None, output_format="r", **kwargs):

        self.bearer_token = bearer_token #TODO: Add support for user tokens.
        self.extra_headers_dict = extra_headers_dict
        if isinstance(request_parameters, str):
            request_parameters = json.loads(request_parameters)
        self.request_parameters = request_parameters
        # magic number of max tweets if you pass a non_int
        self.max_tweets = (max_tweets if isinstance(max_tweets, int)
                           else 10 ** 15)

        self.total_results = 0
        self.n_requests = 0
        self.session = None
        self.current_response = None
        self.current_tweets = None
        self.next_token = None
        self.stream_started = False
        self._tweet_func = lambda x: x
        # magic number of requests!
        self.max_requests = (max_requests if max_requests is not None
                             else 10 ** 9)



        #Branching to counts or Tweets endpoint.
        #TODO: unit testing
        self.search_type = 'tweets'
        #infer_endpoint(request_parameters)
        #change_to_count_endpoint(endpoint)
        self.endpoint = (change_to_count_endpoint(endpoint)
                         if infer_endpoint(request_parameters) == "counts"
                         else endpoint)

        if 'counts' in self.endpoint:
            self.search_type = 'counts'

        self.output_format = output_format

    def formatted_output(self):

        def extract_includes(expansion, _id="id"):
            """
            Return empty objects for things missing in includes.
            """
            if self.includes is not None and expansion in self.includes:
                return defaultdict(
                    lambda: {},
                    {include[_id]: include for include in self.includes[expansion]},
                )
            else:
                return defaultdict(lambda: {})

        #TODO - counts does not have extractions.... So, skip if you caunt.
        # Users extracted both by id and by username for expanding mentions
        includes_users = merge_dicts(extract_includes("users"), extract_includes("users", "username"))
        # Tweets in includes will themselves be expanded
        includes_tweets = extract_includes("tweets")
        # Media is by media_key, not id
        includes_media = extract_includes("media", "media_key")
        includes_polls = extract_includes("polls")
        includes_places = extract_includes("places")
        # Errors are returned but unused here
        includes_errors = extract_includes("errors")

        def expand_payload(payload):
            """
            Recursively step through an object and sub objects and append extra data. 
            """

            # Don't try to expand on primitive values, return strings as is:
            if isinstance(payload, (str, bool, int, float)):
                return payload
            # expand list items individually:
            elif isinstance(payload, list):
                payload = [expand_payload(item) for item in payload]
                return payload
            # Try to expand on dicts within dicts:
            elif isinstance(payload, dict):
                for key, value in payload.items():
                    payload[key] = expand_payload(value)

            if "author_id" in payload:
                payload["author"] = includes_users[payload["author_id"]]

            if "in_reply_to_user_id" in payload:
                payload["in_reply_to_user"] = includes_users[payload["in_reply_to_user_id"]]

            if "media_keys" in payload:
                payload["media"] = list(includes_media[media_key] for media_key in payload["media_keys"])

            if "poll_ids" in payload:
                poll_id = payload["poll_ids"][-1] # always 1, only 1 poll per tweet.
                payload["poll"] = includes_polls[poll_id]

            if "geo" in payload and "place_id" in payload["geo"]:
                place_id = payload["geo"]['place_id']
                payload["geo"] = merge_dicts(payload["geo"], includes_places[place_id])

            if "mentions" in payload:
                payload["mentions"] = list(merge_dicts(referenced_user, includes_users[referenced_user['username']]) for referenced_user in payload["mentions"])

            if "referenced_tweets" in payload:
                payload["referenced_tweets"] = list(merge_dicts(referenced_tweet, includes_tweets[referenced_tweet['id']]) for referenced_tweet in payload["referenced_tweets"])

            if "pinned_tweet_id" in payload:
                payload["pinned_tweet"] = includes_tweets[payload["pinned_tweet_id"]]

            return payload

        #TODO: Tweets or Counts?
        # First, expand the included tweets, before processing actual result tweets:
        if self.search_type == 'tweets':
            for included_id, included_tweet in extract_includes("tweets").items():
                includes_tweets[included_id] = expand_payload(included_tweet)

        def output_response_format():
            """ 
            output the response as 1 "page" per line
            """
            #TODO: counts details
            if self.search_type == 'tweets':
                if self.total_results >= self.max_tweets:
                    return
            yield self.current_response

            #With counts, there is nothing to count here... we aren't counting Tweets (but should count requests)
            if self.search_type == 'tweets':
                self.total_results += self.meta['result_count']

        def output_atomic_format():
            """
            Format the results with "atomic" objects:
            """
            for tweet in self.current_tweets:
                if self.total_results >= self.max_tweets:
                    break
                yield self._tweet_func(expand_payload(tweet))
                self.total_results += 1

        def output_message_stream_format():
            """ 
            output as a stream of messages, 
            the way it was implemented originally
            """
            # Serve up data.tweets.
            for tweet in self.current_tweets:
                if self.total_results >= self.max_tweets:
                    break
                yield self._tweet_func(tweet)
                self.total_results += 1

            # Serve up "includes" arrays, this includes errors
            if self.includes != None:
                yield self.includes

            # Serve up meta structure.
            if self.meta != None:
                yield self.meta

        response_format = {"r": output_response_format,
                           "a": output_atomic_format,
                           "m": output_message_stream_format}

        return response_format.get(self.output_format)()

    def stream(self):
        """
        Main entry point for the data from the API. Will automatically paginate
        through the results via the ``next`` token and return up to ``max_tweets``
        tweets or up to ``max_requests`` API calls, whichever is lower.
        Usage:
            >>> result_stream = ResultStream(**kwargs)
            >>> stream = result_stream.stream()
            >>> results = list(stream)
            >>> # or for faster usage...
            >>> results = list(ResultStream(**kwargs).stream())
        """
        self.init_session()
        #self.check_counts() #TODO: not needed if no Tweet Parser being used.
        self.execute_request()
        self.stream_started = True

        while True:

            if self.current_tweets == None:
                break
            yield from self.formatted_output()

            if self.next_token and self.total_results < self.max_tweets and self.n_requests <= self.max_requests:
                self.request_parameters = merge_dicts(self.request_parameters,
                                                      {"next_token": self.next_token})
                logger.info("paging; total requests read so far: {}"
                            .format(self.n_requests))

                #If hitting the "all" search endpoint, wait one second since that endpoint is currently
                #limited to one request per sleep.
                #Revisit and make configurable when the requests-per-second gets revisited.
                if "tweets/search/all" in self.endpoint:
                    time.sleep(2)

                self.execute_request()

            else:
                break

        logger.info("ending stream at {} tweets".format(self.total_results))
        self.current_response = None
        self.current_tweets = None
        self.session.close()

    def init_session(self):
        """
        Defines a session object for passing requests.
        """
        if self.session:
            self.session.close()
        self.session = make_session(self.bearer_token,
                                    self.extra_headers_dict)


    #TODO: not needed if no Tweet Parser being used.
    def check_counts(self):
        """
        Disables tweet parsing if the count API is used.
        """
        if "counts" in re.split("[/.]", self.endpoint):
            logger.info("disabling tweet parsing due to counts API usage")
            self._tweet_func = lambda x: x


    def execute_request(self):
        """
        Sends the request to the API and parses the json response.
        Makes some assumptions about the session length and sets the presence
        of a "next" token.
        """
        if self.n_requests % 20 == 0 and self.n_requests > 1:
            logger.info("refreshing session")
            self.init_session()

        resp = request(session=self.session,
                       url=self.endpoint,
                       request_parameters=self.request_parameters)
        self.n_requests += 1
        ResultStream.session_request_counter += 1
        try:
            resp = json.loads(resp.content.decode(resp.encoding))

            self.current_response = resp
            self.current_tweets = resp.get("data", None)
            self.includes = resp.get("includes", None)
            self.meta = resp.get("meta", None)
            self.next_token = self.meta.get("next_token", None)

        except:
            print("Error parsing content as JSON.")

    def __repr__(self):
        repr_keys = ["endpoint", "request_parameters", "max_tweets"]
        str_ = json.dumps(dict([(k, self.__dict__.get(k)) for k in repr_keys]),
                          indent=4)
        str_ = "ResultStream: \n\t" + str_
        return str_

def collect_results(query, max_tweets=1000, result_stream_args=None):
    """
    Utility function to quickly get a list of tweets from a ``ResultStream``
    without keeping the object around. Requires your args to be configured
    prior to using.
    Args:
        query (str): valid powertrack rule for your account, preferably
        generated by the `gen_request_parameters` function.
        max_tweets (int): maximum number of tweets or counts to return from
        the API / underlying ``ResultStream`` object.
        result_stream_args (dict): configuration dict that has connection
        information for a ``ResultStream`` object.
    Returns:
        list of results
    Example:
        >>> from searchtweets import collect_results
        >>> tweets = collect_results(query,
                                     max_tweets=500,
                                     result_stream_args=search_args)
    """
    if result_stream_args is None:
        logger.error("This function requires a configuration dict for the "
                     "inner ResultStream object.")
        raise KeyError

    rs = ResultStream(request_parameters=query,
                      max_tweets=max_tweets,
                      **result_stream_args)
    return list(rs.stream())
