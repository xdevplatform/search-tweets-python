# Copyright 2017 Twitter, Inc.
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


REQUIRED_KEYS = {"pt_rule", "endpoint"}


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
                           default=None,
                           help=("the key in the credential file used "
                                 "for this session's credentials. "
                                 "Defaults to search_tweets_api"))

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

    argparser.add_argument("--account-type",
                           dest="account_type",
                           default=None,
                           choices=["premium", "enterprise"],
                           help="The account type you are using")

    argparser.add_argument("--count-bucket",
                           dest="count_bucket",
                           default=None,
                           help=("""Bucket size for counts API. Options:,
                                 day, hour, minute (default is 'day')."""))

    argparser.add_argument("--start-datetime",
                           dest="from_date",
                           default=None,
                           help="""Start of datetime window, format
                                'YYYY-mm-DDTHH:MM' (default: -30 days)""")

    argparser.add_argument("--end-datetime",
                           dest="to_date",
                           default=None,
                           help="""End of datetime window, format
                                 'YYYY-mm-DDTHH:MM' (default: most recent
                                 date)""")

    argparser.add_argument("--filter-rule",
                           dest="pt_rule",
                           default=None,
                           help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")

    argparser.add_argument("--results-per-call",
                           dest="results_per_call",
                           default=100,
                           help="Number of results to return per call "
                                "(default 100; max 500) - corresponds to "
                                "'maxResults' in the API")

    argparser.add_argument("--max-results", dest="max_results",
                           default=500,
                           type=int,
                           help="Maximum number of Tweets or Counts to return for this "
                                "session (defaults to 500)")

    argparser.add_argument("--max-pages",
                           dest="max_pages",
                           type=int,
                           default=None,
                           help="Maximum number of pages/API calls to "
                           "use for this session.")

    argparser.add_argument("--results-per-file", dest="results_per_file",
                           default=0,
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

    argparser.add_argument("--debug",
                           dest="debug",
                           action="store_true",
                           default=False,
                           help="print all info and warning messages")
    return argparser


def main():
    parser = parse_cmd_args()
    args_dict = vars(parse_cmd_args().parse_args())
    if args_dict.get("debug") is True:
        logger.setLevel(logging.DEBUG)
        logger.debug(json.dumps(args_dict, indent=4))

    if args_dict.get("config_filename") is not None:
        configfile_dict = read_config(args_dict["config_filename"])
    else:
        configfile_dict = {}

    creds_dict = load_credentials(filename=args_dict["credential_file"],
                                  account_type=args_dict["account_type"],
                                  yaml_key=args_dict["credential_yaml_key"],
                                  env_overwrite=args_dict["env_overwrite"])

    dict_filter = lambda x: {k: v for k, v in x.items() if v is not None}

    config_dict = merge_dicts(dict_filter(configfile_dict),
                              dict_filter(args_dict),
                              dict_filter(creds_dict))

    logger.debug(json.dumps(config_dict, indent=4))

    if len(dict_filter(config_dict).keys() & REQUIRED_KEYS) < len(REQUIRED_KEYS):
        print(REQUIRED_KEYS - dict_filter(config_dict).keys())
        logger.error("ERROR: not enough arguments for the program to work")
        sys.exit(1)

    stream_params = gen_params_from_config(config_dict)

    logger.debug(json.dumps(config_dict, indent=4))

    rs = ResultStream(tweetify=False, **stream_params)

    logger.debug(str(rs))

    if config_dict.get("filename_prefix") is not None:
        stream = write_result_stream(rs,
                                     filename_prefix=config_dict["filename_prefix"],
                                     results_per_file=config_dict["results_per_file"])
    else:
        stream = rs.stream()

    for tweet in stream:
        if config_dict["print_stream"] is True:
            print(json.dumps(tweet))


if __name__ == '__main__':
    main()
