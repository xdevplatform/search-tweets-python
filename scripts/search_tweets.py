#!/usr/bin/env python
# Copyright 2020 Twitter, Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0
import os
import argparse
import json
import sys
import logging
from searchtweets import (ResultStream,
                          load_credentials,
                          merge_dicts,
                          read_config,
                          write_result_stream,
                          gen_params_from_config)

logger = logging.getLogger()
# we want to leave this here and have it command-line configurable via the
# --debug flag
logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))


REQUIRED_KEYS = {"query", "endpoint"}


def parse_cmd_args():
    argparser = argparse.ArgumentParser()
    help_msg = """configuration file with all parameters. Far,
          easier to use than the command-line args version.,
          If a valid file is found, all args will be populated,
          from there. Remaining command-line args,
          will overrule args found in the config,
          file."""

    argparser.add_argument("--credential-file",
                           dest="credential_file",
                           default=None,
                           help=("Location of the yaml file used to hold "
                                 "your credentials."))

    argparser.add_argument("--credential-file-key",
                           dest="credential_yaml_key",
                           default="search_tweets_v2",
                           help=("the key in the credential file used "
                                 "for this session's credentials. "
                                 "Defaults to search_tweets_v2"))

    argparser.add_argument("--env-overwrite",
                           dest="env_overwrite",
                           default=True,
                           help=("""Overwrite YAML-parsed credentials with
                                 any set environment variables. See API docs or
                                 readme for details."""))

    argparser.add_argument("--config-file",
                           dest="config_filename",
                           default=None,
                           help=help_msg)

    argparser.add_argument("--query",
                           dest="query",
                           default=None,
                           help="Search query. (See: https://developer.twitter.com/en/docs/labs/recent-search/guides/search-queries)")

    argparser.add_argument("--start-time",
                           dest="start_time",
                           default=None,
                           help="""Start of datetime window, format
                                'YYYY-mm-DDTHH:MM' (default: -7 days for /recent, -30 days for /all)""")

    argparser.add_argument("--end-time",
                           dest="end_time",
                           default=None,
                           help="""End of datetime window, format
                                 'YYYY-mm-DDTHH:MM' (default: to 30 seconds before request time)""")

    argparser.add_argument("--since-id",
                           dest="since_id",
                           default=None,
                           help="Tweet ID, will start search from Tweets after this one. (See: https://developer.twitter.com/en/docs/labs/recent-search/guides/pagination)")

    argparser.add_argument("--until-id",
                           dest="until_id",
                           default=None,
                           help="Tweet ID, will end search from Tweets before this one. (See: https://developer.twitter.com/en/docs/labs/recent-search/guides/pagination)")

    argparser.add_argument("--results-per-call",
                           dest="results_per_call",
                           help="Number of results to return per call "
                                "(default 10; max 100) - corresponds to "
                                "'max_results' in the API")

    argparser.add_argument("--expansions",
                       dest="expansions",
                       default=None,
                       help="""A comma-delimited list of expansions. Specified expansions results in full objects in the 'includes' response object.""")

    argparser.add_argument("--tweet-fields",
                           dest="tweet_fields",
                           default=None,
                           help="""A comma-delimited list of Tweet JSON attributes to include in endpoint responses. (API default:"id,text")""")

    argparser.add_argument("--user-fields",
                           dest="user_fields",
                           default=None,
                           help="""A comma-delimited list of User JSON attributes to include in endpoint responses. (API default:"id")""")

    argparser.add_argument("--media-fields",
                           dest="media_fields",
                           default=None,
                           help="""A comma-delimited list of media JSON attributes to include in endpoint responses. (API default:"id")""")

    argparser.add_argument("--place-fields",
                           dest="place_fields",
                           default=None,
                           help="""A comma-delimited list of Twitter Place JSON attributes to include in endpoint responses. (API default:"id")""")

    argparser.add_argument("--poll-fields",
                           dest="poll_fields",
                           default=None,
                           help="""A comma-delimited list of Twitter Poll JSON attributes to include in endpoint responses. (API default:"id")""")
    #TODO: add code!
    argparser.add_argument("--atomic",
                       dest="atomic",
                       action="store_true",
                       default=False,
                       help="Inject 'includes' objects into Tweet objects.")

    # argparser.add_argument("--output-options",
    #                        dest="output_options",
    #                        default=None,
    #                        help="Set output options: 'a' - atomic, 'r' - response, 'c' - constructed")


    argparser.add_argument("--max-tweets", dest="max_tweets",
                           type=int,
                           help="Maximum number of Tweets to return for this session of requests.")

    argparser.add_argument("--max-pages",
                           dest="max_pages",
                           type=int,
                           default=None,
                           help="Maximum number of pages/API calls to "
                                "use for this session.")

    argparser.add_argument("--results-per-file", dest="results_per_file",
                           default=None,
                           type=int,
                           help="Maximum tweets to save per file.")

    argparser.add_argument("--filename-prefix",
                           dest="filename_prefix",
                           default=None,
                           help="prefix for the filename where tweet "
                                " json data will be stored.")

    argparser.add_argument("--no-print-stream",
                           dest="print_stream",
                           action="store_false",
                           help="disable print streaming")

    argparser.add_argument("--print-stream",
                           dest="print_stream",
                           action="store_true",
                           default=True,
                           help="Print tweet stream to stdout")



    argparser.add_argument("--extra-headers",
                           dest="extra_headers",
                           type=str,
                           default=None,
                           help="JSON-formatted str representing a dict of additional HTTP request headers")

    argparser.add_argument("--debug",
                           dest="debug",
                           action="store_true",
                           default=False,
                           help="print all info and warning messages")
    return argparser


def _filter_sensitive_args(dict_):
    sens_args = ("consumer_key", "consumer_secret", "bearer_token")
    return {k: v for k, v in dict_.items() if k not in sens_args}

def main():
    args_dict = vars(parse_cmd_args().parse_args())
    if args_dict.get("debug") is True:
        logger.setLevel(logging.DEBUG)
        logger.debug("command line args dict:")
        logger.debug(json.dumps(args_dict, indent=4))

    if args_dict.get("config_filename") is not None:
        configfile_dict = read_config(args_dict["config_filename"])
    else:
        configfile_dict = {}

    extra_headers_str = args_dict.get("extra_headers")
    if extra_headers_str is not None:
        args_dict['extra_headers_dict'] = json.loads(extra_headers_str)
        del args_dict['extra_headers']

    logger.debug("config file ({}) arguments sans sensitive args:".format(args_dict["config_filename"]))
    logger.debug(json.dumps(_filter_sensitive_args(configfile_dict), indent=4))

    creds_dict = load_credentials(filename=args_dict["credential_file"],
                                  yaml_key=args_dict["credential_yaml_key"],
                                  env_overwrite=args_dict["env_overwrite"])

    dict_filter = lambda x: {k: v for k, v in x.items() if v is not None}

    config_dict = merge_dicts(dict_filter(configfile_dict),
                              dict_filter(creds_dict),
                              dict_filter(args_dict))

    logger.debug("combined dict (cli, config, creds):")
    logger.debug(json.dumps(_filter_sensitive_args(config_dict), indent=4))

    if len(dict_filter(config_dict).keys() & REQUIRED_KEYS) < len(REQUIRED_KEYS):
        print(REQUIRED_KEYS - dict_filter(config_dict).keys())
        logger.error("ERROR: not enough arguments for the script to work")
        sys.exit(1)

    stream_params = gen_params_from_config(config_dict)
    logger.debug("full arguments passed to the ResultStream object sans credentials")
    logger.debug(json.dumps(_filter_sensitive_args(stream_params), indent=4))

    rs = ResultStream(tweetify=False, **stream_params)

    logger.debug(str(rs))

    if config_dict.get("filename_prefix") is not None:
        stream = write_result_stream(rs,
                                     filename_prefix=config_dict.get("filename_prefix"),
                                     results_per_file=config_dict.get("results_per_file"))
    else:
        stream = rs.stream()

    for tweet in stream:
        if config_dict["print_stream"] is True:
            print(json.dumps(tweet))

if __name__ == '__main__':
    main()
