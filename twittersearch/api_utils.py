import datetime
import logging
import sys
if sys.version_info.major == 2:
    import ConfigParser as configparser
else:
    import configparser
try:
    import ujson as json
except ImportError:
    import json

__all__ = ["gen_endpoint", "gen_rule_payload", "gen_params_from_config",
           "validate_count_api"]

logger = logging.getLogger(__name__)

GNIP_RESP_CODES = {
    '200': 'OK: The request was successful. The JSON response will be similar to the following:',

    '400': ("Bad Request: Generally, this response occurs due to the presence of "
            "invalid JSON in the request, or where the request failed to send any JSON payload."),

    '401': ("Unauthorized: HTTP authentication failed due to invalid "
            "credentials. Log in to console.gnip.com with your credentials to ensure"
            " you are using them correctly with your request. "),
    '404': ("Not Found: The resource was not found at the URL to which the "
            "request was sent, likely because an incorrect URL was used."),
    '422': ("Unprocessable Entity: This is returned due to invalid parameters "
            "in a query or when a query is too complex for us to process. – e.g. "
            " invalid PowerTrack rules or too many phrase operators, rendering a "
            " query too complex."),
    '429': ("Unknown Code: Your app has exceeded the limit on connection "
            "requests. The corresponding JSON message will look similar to the "
            "following:"),
    '500': ("Internal Server Error: There was an error on Gnip's side. Retry "
            "your request using an exponential backoff pattern."),
    '502': ("Proxy Error: There was an error on Gnip's side. Retry your request "
            "using an exponential backoff pattern."),
    '503': ("Service Unavailable: There was an error on Gnip's side. Retry your "
            "request using an exponential backoff pattern.")
}

BASE_URL = "https://gnip-api.twitter.com/search/"
BASE_ENDPOINT = "{api}/accounts/{account_name}/{label}"
PREMIUM_URL = "https://api.twitter.com/1.1/tweets/search/30day/{ENV}.json"


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
        >>> from twittersearch.utils import convert_utc_time
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



def _gen_premium_endpoint(env_name, count_endpoint=False):
    """Generates the endpoint URL for a premium account. Early stage and will
    anticipate changes, particularly around the search API or version?
    """
    freemium_baseurl = "https://api.twitter.com/1.1/tweets/search/30day/{ENV}"
    url = freemium_baseurl.format(ENV=env_name)
    return url


def _gen_enterprise_endpoint(search_api, account_name, label):
    """Generates the endpoint URL for an enterprise account."""

    base_url = "https://gnip-api.twitter.com/search/"
    base_endpoint = "{api}/accounts/{account_name}/{label}"
    label = label if not label.endswith(".json") else label.split(".")[0]
    endpoint = base_endpoint.format(api=search_api,
                                    account_name=account_name,
                                    label=label)
    return base_url + endpoint


def gen_endpoint(kind="enterprise",
                 search_api=None,
                 account_name=None,
                 label=None,
                 count_endpoint=False,
                 **kwargs):
    """
    Creates the endpoint URL from discrete information.

    Args:
        kind (str): supports both `enterprise` and `premium` access.
        search_api (str): the api to use, `30day` or `fullarchive`
        account_name (str): the master account for the user
        label (str): stream within an account to connect
        count_endpoint (bool): defines using the Counts endpoint over the default data endpoint.

    Returns:
        str: well-formed url for a connection.

    Example:
        >>> from twittersearch.utils import gen_endpoint
        >>> search_api = "30day"
        >>> account_name = "montypython"
        >>> endpoint_label = "python.json"
        >>> gen_endpoint("enterprise",
                search_api, account_name, endpoint_label, count_endpoint=False)
        'https://gnip-api.twitter.com/search/30day/accounts/montypython/python.json'
        >>> gen_endpoint("enterprise",
                search_api, account_name, endpoint_label, count_endpoint=True)
        'https://gnip-api.twitter.com/search/30day/accounts/montypython/python/counts.json'
        >>> gen_endpoint(kind="premium", label="dev", count_endpoint=False)
        'https://api.twitter.com/1.1/tweets/search/30day/dev.json'
    """
    if kind == 'enterprise':
        endpoint = _gen_enterprise_endpoint(search_api=search_api,
                                            account_name=account_name,
                                            label=label)
    elif kind == 'premium':
        endpoint = _gen_premium_endpoint(env_name=label)

    else:
        logger.error("only two types of access are supported here; Enterprise and Premium")
        raise ValueError

    if count_endpoint:
        if kind == 'premium':
            logger.warn("premium sandbox envionments do not have counts"
                        "API access. You might receive errors downstream.")
        endpoint = endpoint + "/counts.json"
    else:
        endpoint = endpoint + ".json"

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

        >>> from twittersearch.utils import gen_rule_payload
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
            logger.error("invalid count bucket: provided {}".format(count_bucket))
            raise ValueError

    return json.dumps(payload) if stringify else payload


def gen_params_from_config(config_dict):
    """
    Generates parameters for a ResultStream from a dictionary.
    """

    endpoint = gen_endpoint(config_dict["account_type"],
                            config_dict["search_api"],
                            config_dict["account_name"],
                            config_dict["endpoint_label"],
                            config_dict.get("count_bucket") # autoconfigures counts api
                           )

    rule = gen_rule_payload(pt_rule=config_dict["pt_rule"],
                            from_date=config_dict.get("from_date", None),
                            to_date=config_dict.get("to_date", None),
                            max_results=int(config_dict.get("max_results", None)),
                            count_bucket=config_dict.get("count_bucket", None)
                           )


    _dict = {"url": endpoint,
             "username": config_dict.get("username"),
             "password": config_dict.get("password"),
             "bearer_token": config_dict.get("bearer_token"),
             "rule_payload": rule,
             "results_per_file": int(config_dict.get("results_per_file")),
             "max_tweets": int(config_dict.get("max_tweets")),
             "max_pages": config_dict.get("max_pages", None)
            }
    return _dict


def validate_count_api(rule_payload, url):
    rule = rule_payload if isinstance(rule_payload, dict) else json.loads(rule_payload)
    bucket = rule.get('bucket')
    counts = set(url.split("/")) & {"counts.json"}
    if len(counts) == 0:
        if bucket is not None:
            msg = ("""there is a count bucket present in your payload,
                   but you are using not using the counts API.
                   Please check your endpoints and try again""")
            logger.error(msg)
            raise ValueError
