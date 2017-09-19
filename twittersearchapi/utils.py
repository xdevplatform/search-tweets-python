from functools import reduce
import itertools as it
import types
import re
import codecs
import unicodedata
import datetime
import time
import sys
if sys.version_info.major == 2:
    import ConfigParser as configparser
else:
    import configparser
try:
    import ujson as json
except ImportError:
    import json
import requests


GNIP_RESP_CODES = {
    '200': 'OK: The request was successful. The JSON response will be similar to the following:',
    '400': 'Bad Request: Generally, this response occurs due to the presence of invalid JSON in the request, or where the request failed to send any JSON payload. ',
    '401': 'Unauthorized: HTTP authentication failed due to invalid credentials. Log in to console.gnip.com with your credentials to ensure you are using them correctly with your request. ',
    '404': 'Not Found: The resource was not found at the URL to which the request was sent, likely because an incorrect URL was used.',
    '422': 'Unprocessable Entity: This is returned due to invalid parameters in a query or when a query is too complex for us to process. – e.g. invalid PowerTrack rules or too many phrase operators, rendering a query too complex.',
    '429': 'Unknown Code: Your app has exceeded the limit on connection requests. The corresponding JSON message will look similar to the following:',
    '500': "Internal Server Error: There was an error on Gnip's side. Retry your request using an exponential backoff pattern.",
    '502': "Proxy Error: There was an error on Gnip's side. Retry your request using an exponential backoff pattern.",
    '503': "Service Unavailable: There was an error on Gnip's side. Retry your request using an exponential backoff pattern."
}
BASE_URL = "https://gnip-api.twitter.com/search/"
BASE_ENDPOINT = "{api}/accounts/{account_name}/{label}"




def take(n, iterable):
    "Return first n items of the iterable as a list"
    return it.islice(iterable, n)


def partition(iterable, chunk_size, pad_none=False):
    """adapted from Toolz"""
    args = [iter(iterable)] * chunk_size
    if not pad_none:
        return zip(*args)
    else:
        return it.zip_longest(*args)


def merge_dicts(*dicts):
    """
    Helpful function to merge / combine dictionaries and return a new
    dictionary.

    Args:
        dicts (list or Iterable): iterable set of dictionarys for merging.

    Returns:
        dict: dict with all keys from the passed list.

    Example:
        >>> d1 = {"rule": "something has:geo"}
        >>> d2 = {"maxResults": 1000}
        >>> merge_dicts([d1, d2])
        {"maxResults": 1000, "rule": "something has:geo"}
    """
    def _merge_dicts(dict1, dict2):
        return {**dict1, **dict2}

    return reduce(_merge_dicts, dicts)



def retry(func):
    """
    Decorator to handle API retries and exceptions. Defaults to three retries.

    Args:
        func (function): function for decoration

    Returns:
        decorated function

    """
    def retried_func(*args, **kwargs):
        MAX_TRIES = 3
        tries = 0
        while True:
            try:
                resp = func(*args, **kwargs)

            except requests.exceptions.ConnectionError as exc:
                exc.msg = "Connection error for session; exiting"
                raise exc

            except requests.exceptions.HTTPError as exc:
                exc.msg = "HTTP error for session; exiting"
                raise exc

            if resp.status_code != 200 and tries < MAX_TRIES:
                print("retrying request; current status code: {}"
                      .format(resp.status_code))
                tries += 1
                time.sleep(1)
                continue

            break

        if resp.status_code != 200:
            print("HTTP Error code: {}: {}"
                  .format(resp.status_code,
                          GNIP_RESP_CODES[str(resp.status_code)]))
            print("rule payload: {}".format(kwargs["rule_payload"]))
            raise requests.exceptions.HTTPError

        return resp

    return retried_func


def convert_utc_time(datetime_str):
    """Handles datetime argument conversion to the GNIP API format, which is
    `YYYYMMDDHHSS`. Flexible passing of date formats.

    Args:
        datetime_str (str): the datestring, which can either be in GNIP API
        Format (YYYYmmDDHHSS), ISO date format (YYYY-mm-DD), ISO datetime
        format (YYYY-mm-DD HH:mm), or command-line ISO format (YYYY-mm-DDTHH:mm)
    Returns:
        string of GNIP API formatted date.

    Example:
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
    if not set(['-', ':']) & set(datetime_str):
        _date = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M")
    else:
        try:
            if "T" in datetime_str:
                datetime_str = datetime_str.replace('T', ' ') # command line with 'T'
            _date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            _date = datetime.datetime.strptime(datetime_str, "%Y-%m-%d")
    return _date.strftime("%Y%m%d%H%M")


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



def gen_rule_payload(pt_rule, max_results=500,
                     from_date=None, to_date=None, count_bucket=None,
                     stringify=True):

    """Generates the dict or json payload for a PowerTrack rule.

    Args:
        pt_rule (str): the string version of a powertrack rule, e.g., "kanye
            west has:geo". Accepts multi-line strings for ease of entry.
        max_results (int): max results for the batch. Defaults to 500 to reduce
                           API call usage.
        from_date (str or None): date format as specified by
            `convert_utc_time` for the starting time of your search.

        to_date (str or None): date format as specified by
            `convert_utc_time` for the end time of your search.

        count_bucket (str or None): if using the counts api endpoint, will
            define the count bucket for which tweets are aggregated.
        stringify (bool): specifies the return type, `dict` or json-formatted
            `str`.

    Example:

        >>> gen_rule_payload("kanye west has:geo",
            ...              from_date="2017-08-21",
            ...              to_date="2017-08-22")
        '{"query":"kanye west has:geo","maxResults":100,"toDate":"201708220000","fromDate":"201708210000"}'
    """

    pt_rule = ' '.join(pt_rule.split()) # allows multi-line strings
    payload = {"query": pt_rule,
               "maxResults": max_results,
              }
    if from_date:
        payload["toDate"] = convert_utc_time(to_date)
    if to_date:
        payload["fromDate"] = convert_utc_time(from_date)
    if count_bucket:
        if set(["day", "hour", "minute"]) & set([count_bucket]):
            payload["bucket"] = count_bucket
            del payload["maxResults"]
        else:
            print("invalid count bucket: provided {}".format(count_bucket))
            raise ValueError

    return json.dumps(payload) if stringify else payload


def write_ndjson(filename, data_iterable, append=False, **kwargs):
    write_mode = "ab" if append else "wb"
    print("writing data to file {}".format(filename))
    with codecs.open(filename, write_mode, "utf-8") as outfile:
        for item in data_iterable:
            outfile.write(json.dumps(item) + "\n")
            yield item


def write_result_stream(result_stream, filename_prefix=None,
                        results_per_file=None, **kwargs):
    if isinstance(result_stream, types.GeneratorType):
        stream = result_stream
    else:
        stream = result_stream.stream()

    file_time_formatter = "%Y-%m-%dT%H:%M:%S"
    if filename_prefix is None:
        filename_prefix = "twitter_search_results"

    if results_per_file:
        print("chunking result stream to files with {} tweets per file".format(results_per_file))
        chunked_stream = partition(stream, results_per_file, pad_none=True)
        for chunk in chunked_stream:
            chunk = filter(lambda x: x is not None, chunk)
            curr_datetime = datetime.datetime.utcnow().strftime(file_time_formatter)
            _filename = "{}_{}.json".format(filename_prefix, curr_datetime)
            yield from write_ndjson(_filename, chunk)

    else:
        curr_datetime = datetime.datetime.utcnow().strftime(file_time_formatter)
        _filename = "{}.json".format(filename_prefix)
        yield from write_ndjson(_filename, stream)


def gen_params_from_config(config_dict):
    endpoint = gen_endpoint(config_dict["search_api"],
                            config_dict["account_name"],
                            config_dict["endpoint_label"],
                            config_dict.get("count_endpoint", None)
                           )

    rule = gen_rule_payload(pt_rule=config_dict["pt_rule"],
                            from_date=config_dict.get("from_date", None),
                            to_date=config_dict.get("to_date", None),
                            max_results=int(config_dict.get("max_results", None)),
                            count_bucket=config_dict.get("count_bucket", None)
                           )


    _dict = {"url": endpoint,
             "username": config_dict["username"],
             "password": config_dict["password"],
             "rule_payload": rule,
             "results_per_file": int(config_dict.get("results_per_file")),
             "max_tweets": int(config_dict.get("max_tweets"))
            }
    return _dict


def gen_filepath(config_dict):
    parts = [i for i in [config_dict.get("output_file_path"),
                         config_dict.get("output_file_prefix")]]
    return os.path.join(*parts)


def read_configfile(filename):
    config = configparser.ConfigParser()

    with open(filename) as f:
        config.read_file(f)

    config_dict = merge_dicts(*[dict(config[s]) for s in config.sections()])
    return config_dict

