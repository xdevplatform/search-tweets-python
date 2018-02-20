# -*- coding: utf-8 -*-
# Copyright 2017 Twitter, Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0
"""This module handles credential management and parsing for the API. As we
have multiple Search products with different authentication schemes, we try to
provide some flexibility to make this process easier. We suggest putting your
credentials in a YAML file, but the main function in this module,
``load_credentials``, will parse environment variables as well.
"""
import os
import logging
import yaml
import requests
import base64
from .utils import merge_dicts

OAUTH_ENDPOINT = 'https://api.twitter.com/oauth2/token'

__all__ = ["load_credentials"]

logger = logging.getLogger(__name__)


def _load_yaml_credentials(filename=None, yaml_key=None):
    """Loads and parses credentials in a YAML file. Catches common exceptions
    and returns an empty dict on error, which will be handled downstream.

    Returns:
        dict: parsed credentials or {}
    """
    try:
        with open(os.path.expanduser(filename)) as f:
            search_creds = yaml.load(f)[yaml_key]
    except FileNotFoundError:
        logger.error("cannot read file {}".format(filename))
        search_creds = {}
    except KeyError:
        logger.error("{} is missing the provided key: {}"
                     .format(filename, yaml_key))
        search_creds = {}

    return search_creds


def _load_env_credentials():
    vars_ = ["SEARCHTWEETS_ENDPOINT",
             "SEARCHTWEETS_ACCOUNT",
             "SEARCHTWEETS_USERNAME",
             "SEARCHTWEETS_PASSWORD",
             "SEARCHTWEETS_BEARER_TOKEN",
             "SEARCHTWEETS_ACCOUNT_TYPE",
             "SEARCHTWEETS_CONSUMER_KEY",
             "SEARCHTWEETS_CONSUMER_SECRET"
             ]
    renamed = [var.replace("SEARCHTWEETS_", '').lower() for var in vars_]

    parsed = {r: os.environ.get(var) for (var, r) in zip(vars_, renamed)}
    parsed = {k: v for k, v in parsed.items() if v is not None}
    return parsed


def _parse_credentials(search_creds, account_type):

    if account_type is None:
        account_type = search_creds.get("account_type", None)
        # attempt to infer account type
        if account_type is None:
            if search_creds.get("bearer_token") is not None:
                account_type = "premium"
            elif search_creds.get("password") is not None:
                account_type = "enterprise"
            else:
                pass

    if account_type not in {"premium", "enterprise"}:
        msg = """Account type is not specified and cannot be inferred.
        Please check your credential file, arguments, or environment variables
        for issues. The account type must be 'premium' or 'enterprise'.
        """
        logger.error(msg)
        raise KeyError

    try:
        if account_type == "premium":
            if "bearer_token" not in search_creds:
                if "consumer_key" in search_creds \
                  and "consumer_secret" in search_creds:
                    search_creds["bearer_token"] = _generate_bearer_token(
                        search_creds["consumer_key"],
                        search_creds["consumer_secret"])

            search_args = {
                "bearer_token": search_creds["bearer_token"],
                "endpoint": search_creds["endpoint"]}
        if account_type == "enterprise":
            search_args = {"username": search_creds["username"],
                           "password": search_creds["password"],
                           "endpoint": search_creds["endpoint"]}
    except KeyError:
        logger.error("Your credentials are not configured correctly and "
                     " you are missing a required field. Please see the "
                     " readme for proper configuration")
        raise KeyError

    return search_args


def load_credentials(filename=None, account_type=None,
                     yaml_key=None, env_overwrite=True):
    """
    Handles credential management. Supports both YAML files and environment
    variables. A YAML file is preferred for simplicity and configureability.
    A YAML credential file should look something like this:

    .. code:: yaml

        <KEY>:
          endpoint: <FULL_URL_OF_ENDPOINT>
          username: <USERNAME>
          password: <PW>
          consumer_key: <KEY>
          consumer_secret: <SECRET>
          bearer_token: <TOKEN>
          account_type: <enterprise OR premium>

    with the appropriate fields filled out for your account. The top-level key
    defaults to ``search_tweets_api`` but can be flexible.

    If a YAML file is not found or is missing keys, this function will check
    for this information in the environment variables that correspond to

    .. code: yaml

        SEARCHTWEETS_ENDPOINT
        SEARCHTWEETS_USERNAME
        SEARCHTWEETS_PASSWORD
        SEARCHTWEETS_BEARER_TOKEN
        SEARCHTWEETS_ACCOUNT_TYPE
        ...

    Again, set the variables that correspond to your account information and
    type. See the main documentation for details and more examples.


    Args:
        filename (str): pass a filename here if you do not want to use the
                        default ``~/.twitter_keys.yaml``
        account_type (str): your account type, "premium" or "enterprise". We
            will attempt to infer the account info if left empty.
        yaml_key (str): the top-level key in the YAML file that has your
            information. Defaults to ``search_tweets_api``.
        env_overwrite: any found environment variables will overwrite values
            found in a YAML file. Defaults to ``True``.

    Returns:
        dict: your access credentials.

    Example:
        >>> from searchtweets.api_utils import load_credentials
        >>> search_args = load_credentials(account_type="premium",
                env_overwrite=False)
        >>> search_args.keys()
        dict_keys(['bearer_token', 'endpoint'])
        >>> import os
        >>> os.environ["SEARCHTWEETS_ENDPOINT"] = "https://endpoint"
        >>> os.environ["SEARCHTWEETS_USERNAME"] = "areallybadpassword"
        >>> os.environ["SEARCHTWEETS_PASSWORD"] = "<PW>"
        >>> load_credentials()
        {'endpoint': 'https://endpoint',
         'password': '<PW>',
         'username': 'areallybadpassword'}

    """
    yaml_key = yaml_key if yaml_key is not None else "search_tweets_api"
    filename = "~/.twitter_keys.yaml" if filename is None else filename

    yaml_vars = _load_yaml_credentials(filename=filename, yaml_key=yaml_key)
    if not yaml_vars:
        logger.warning("Error parsing YAML file; searching for "
                       "valid environment variables")
    env_vars = _load_env_credentials()
    merged_vars = (merge_dicts(yaml_vars, env_vars)
                   if env_overwrite
                   else merge_dicts(env_vars, yaml_vars))
    parsed_vars = _parse_credentials(merged_vars, account_type=account_type)
    return parsed_vars


def _generate_bearer_token(consumer_key, consumer_secret):
    """
    Return the bearer token for a given pair of consumer key and secret values.
    """
    data = [('grant_type', 'client_credentials')]
    resp = requests.post(OAUTH_ENDPOINT,
                         data=data,
                         auth=(consumer_key, consumer_secret))
    logger.warning("Grabbing bearer token from OAUTH")
    if resp.status_code >= 400:
        logger.error(resp.text)
        resp.raise_for_status()

    return resp.json()['access_token']
