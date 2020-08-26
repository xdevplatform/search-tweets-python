# -*- coding: utf-8 -*-
# Copyright 2020 Twitter, Inc.
# Licensed under the MIT License
# https://opensource.org/licenses/MIT
"""
Module containing the various functions that are used for API calls,
request payload generation, and related.
"""

import re
import datetime
from dateutil.relativedelta import *
import logging
try:
    import ujson as json
except ImportError:
    import json

__all__ = ["gen_request_parameters",
           "gen_params_from_config",
           "convert_utc_time"]

logger = logging.getLogger(__name__)

def convert_utc_time(datetime_str):
    """
    Handles datetime argument conversion to the Labs API format, which is
    `YYYY-MM-DDTHH:mm:ssZ`.
    Flexible passing of date formats in the following types::

        - YYYYmmDDHHMM
        - YYYY-mm-DD
        - YYYY-mm-DD HH:MM
        - YYYY-mm-DDTHH:MM
        - 3d (set start_time to three days ago)
        - 12h (set start_time to twelve hours ago)
        - 15m (set start_time to fifteen minutes ago)

    Args:
        datetime_str (str): valid formats are listed above.

    Returns:
        string of ISO formatted date.

    Example:
        >>> from searchtweets.utils import convert_utc_time
        >>> convert_utc_time("201708020000")
        '201708020000'
        >>> convert_utc_time("2017-08-02")
        '201708020000'
        >>> convert_utc_time("2017-08-02 00:00")
        '201708020000'
        >>> convert_utc_time("2017-08-02T00:00")
        '201708020000'
    """

    if not datetime_str:
        return None
    try:
        if len(datetime_str) <= 5:
            _date = datetime.datetime.utcnow()
            #parse out numeric character.
            num = float(datetime_str[:-1])
            if 'd' in datetime_str:
                _date = (_date + relativedelta(days=-num))
            elif 'h' in datetime_str:
                _date = (_date + relativedelta(hours=-num))
            elif 'm' in datetime_str:
                _date = (_date + relativedelta(minutes=-num))
        elif not set(['-', ':']) & set(datetime_str):
            _date = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M")
        elif 'T' in datetime_str:
            # command line with 'T'
            datetime_str = datetime_str.replace('T', ' ')
            _date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        else:
            _date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

    except ValueError:
        _date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d")

    return _date.strftime("%Y-%m-%dT%H:%M:%SZ")

def gen_request_parameters(query, results_per_call=None,
                           start_time=None, end_time=None, since_id=None, until_id=None,
                           tweet_fields=None, user_fields=None, media_fields=None,
                           place_fields=None, poll_fields=None,
                           expansions=None,
                           stringify=True):

    """
    Generates the dict or json payload for a search query.

    Args:
        query (str): The string version of a search query,
            e.g., "snow has:media -is:retweet". Accepts multi-line strings
            for ease of entry.
        results_per_call (int): number of tweets or counts returned per API
        call. This maps to the `max_results`` search API parameter.
            Defaults to 100 (maximum supported in Labs).
        start_time (str or None): Date format as specified by
            `convert_utc_time` for the starting time of your search.
        end_time (str or None): date format as specified by `convert_utc_time`
            for the end time of your search.
        tweet_fields (string): comma-delimted list of Tweet JSON attributes wanted in endpoint responses. Default is "id,created_at,text").
        Also user_fields, media_fields, place_fields, poll_fields
        expansions (string): comma-delimited list of object expansions.
        stringify (bool): specifies the return type, `dict`
            or json-formatted `str`.

    Example:

        >>> from searchtweets.utils import gen_request_parameters
        >>> gen_request_parameters("snow has:media -is:retweet",
            ...              from_date="2020-02-18",
            ...              to_date="2020-02-21")
        '{"query":"snow has:media -is:retweet","max_results":100,"start_time":"202002180000","end_time":"202002210000"}'
    """

    #Set endpoint request parameter to command-line arguments. This is where 'translation' happens.
    query = ' '.join(query.split())  # allows multi-line strings
    payload = {"query": query}
    if results_per_call is not None and isinstance(results_per_call, int) is True:
        payload["max_results"] = results_per_call
    if start_time:
        payload["start_time"] = convert_utc_time(start_time)
    if end_time:
        payload["end_time"] = convert_utc_time(end_time)
    if since_id:
        payload["since_id"] = since_id
    if until_id:
        payload["until_id"] = until_id
    if tweet_fields:
        payload["tweet.fields"] = tweet_fields
    if user_fields:
        payload["user.fields"] = user_fields
    if media_fields:
        payload["media.fields"] = media_fields
    if place_fields:
        payload["place.fields"] = place_fields
    if poll_fields:
        payload["poll.fields"] = poll_fields
    if expansions:
        payload["expansions"] = expansions

    return json.dumps(payload) if stringify else payload


def gen_params_from_config(config_dict):
    """
    Generates parameters for a ResultStream from a dictionary.
    """

    # if config_dict.get("count_bucket"):
    #     logger.warning("change your endpoint to the count endpoint; this is "
    #                    "default behavior when the count bucket "
    #                    "field is defined")
    #     endpoint = change_to_count_endpoint(config_dict.get("endpoint"))
    # else:
    endpoint = config_dict.get("endpoint")


    def intify(arg):
        if not isinstance(arg, int) and arg is not None:
            return int(arg)
        else:
            return arg

    # This numeric parameter comes in as a string when it's parsed
    results_per_call = intify(config_dict.get("results_per_call", None))

    query = gen_request_parameters(query=config_dict["query"],
                            start_time=config_dict.get("start_time", None),
                            end_time=config_dict.get("end_time", None),
                            since_id=config_dict.get("since_id", None),
                            until_id=config_dict.get("until_id", None),
                            tweet_fields=config_dict.get("tweet_fields", None),
                            user_fields=config_dict.get("user_fields", None),
                            media_fields=config_dict.get("media_fields", None),
                            place_fields=config_dict.get("place_fields", None),
                            poll_fields=config_dict.get("poll_fields", None),
                            expansions=config_dict.get("expansions", None),
                            results_per_call=results_per_call)
                            #count_bucket=config_dict.get("count_bucket", None))

    _dict = {"endpoint": endpoint,
             "bearer_token": config_dict.get("bearer_token"),
             "extra_headers_dict": config_dict.get("extra_headers_dict",None),
             "request_parameters": query,
             "results_per_file": intify(config_dict.get("results_per_file")),
             "max_tweets": intify(config_dict.get("max_tweets")),
             "max_pages": intify(config_dict.get("max_pages", None))}

    return _dict





