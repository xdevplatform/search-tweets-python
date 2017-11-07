import os
import argparse
import json
import sys
import logging
import configparser
from io import StringIO

logger = logging.getLogger()
# we want to leave this here and have it command-line configurable via the
# --debug flag
logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

from twittersearch.result_stream import ResultStream
from twittersearch.api_utils import *
from twittersearch.utils import *


REQUIRED_KEYS = {"pt_rule", "endpoint_label",}

def parse_cmd_args():
    twitter_parser = argparse.ArgumentParser()

    twitter_parser.add_argument("--config-file",
                                dest="config_filename",
                                default=None,
                                help=("configuration file with all parameters. Far",
                                      "easier to use than the command-line args version.",
                                      "If a valid file is found, all args will be populated",
                                      "from there. Remaining command-line args",
                                      "will overrule args found in the config",
                                      "file."))


    twitter_parser.add_argument("--account_type",
                                dest="account_type",
                                default=None,
                                help="enterprise or premium account")

    twitter_parser.add_argument("--account-name",
                                dest="account_name",
                                default=None,
                                help="Gnip API account name")

    twitter_parser.add_argument("--user-name",
                                dest="username",
                                default=None,
                                help="User name for Enterprise API access")

    twitter_parser.add_argument("--password",
                                dest="password",
                                default=None,
                                help="Password for Enterprise API access")

    twitter_parser.add_argument("--bearer-token",
                                dest="bearer_token",
                                default=None,
                                help="bearer token for premium API access")

    twitter_parser.add_argument("--count-bucket",
                                dest="count_bucket",
                                default=None,
                                help=("Bucket size for counts query. Options",
                                      "are day, hour, minute (default is 'day')."))

    twitter_parser.add_argument("--start-datetime",
                                dest="from_date",
                                default=None,
                                help="Start of datetime window, format 'YYYY-mm-DDTHH:MM' (default: 30 days ago)")

    twitter_parser.add_argument("--end-datetime", dest="to_date",
                                default=None,
                                help="End of datetime window, format 'YYYY-mm-DDTHH:MM' (default: most recent activities)")

    twitter_parser.add_argument("--filter-rule", dest="pt_rule",
                                default=None,
                                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")

    twitter_parser.add_argument("--search-api",
                                dest="search_api",
                                default=None,
                                help="which api to use")

    twitter_parser.add_argument("--stream-endpoint",
                                dest="endpoint_label",
                                default=None,
                                help=("Label for your environment. Find in your gnip"
                                      " console or developer dashboard"))

    twitter_parser.add_argument("--max-results", dest="max_results",
                                default=500,
                                help="Maximum results to return per api call (default 500; max 500)")

    twitter_parser.add_argument("--max-tweets", dest="max_tweets",
                                default=500,
                                type=int,
                                help="Maximum results to return for all pages; see -a option")

    twitter_parser.add_argument("--max-pages",
                                dest="max_pages",
                                type=int,
                                default=None,
                                help="Maximum number of pages to use for this session.")

    twitter_parser.add_argument("--results-per-file", dest="results_per_file",
                                default=0,
                                type=int,
                                help="Maximum tweets to save per file.")

    twitter_parser.add_argument("--filename-prefix",
                                dest="filename_prefix",
                                default=None,
                                help="prefix for the filename where tweet json data will be stored."
                               )

    twitter_parser.add_argument("--no-print-stream",
                                dest="print_stream",
                                action="store_false",
                                help="disable print streaming")

    twitter_parser.add_argument("--print-stream",
                                dest="print_stream",
                                action="store_true",
                                default=True,
                                help="Print tweet stream to stdout")

    twitter_parser.add_argument("--debug",
                                dest="debug",
                                action="store_true",
                                default=False,
                                help="print all info and warning messages")
    return twitter_parser


def main():
    args_dict = vars(parse_cmd_args().parse_args())
    if args_dict.get("debug") is True:
        logger.setLevel(logging.DEBUG)

    logger.debug(json.dumps(args_dict, indent=4))

    if args_dict.get("config_filename") is not None:
        configfile_dict = read_configfile(args_dict["config_filename"])
    else:
        configfile_dict = {}

    dict_filter = lambda x: {k: v for k, v in x.items() if v is not None}
    config_dict = merge_dicts(dict_filter(configfile_dict),
                              dict_filter(args_dict))

    logger.debug(json.dumps(config_dict, indent=4))

    if len(dict_filter(config_dict).keys() & REQUIRED_KEYS) < len(REQUIRED_KEYS):
        print(REQUIRED_KEYS - dict_filter(config_dict).keys())
        logger.error("ERROR: not enough arguments present for the program to work")
        sys.exit(1)

    stream_params = gen_params_from_config(config_dict)

    logger.debug(json.dumps(config_dict, indent=4))

    rs = ResultStream(**stream_params, tweetify=False)

    logger.debug(str(rs))

    if config_dict.get("filename_prefix") is not None:
        stream = write_result_stream(rs,
                                     filename_prefix=config_dict["filename_prefix"],
                                     results_per_file=config_dict["results_per_file"],
                                    )
    else:
        stream = rs.stream()

    for tweet in stream:
        if config_dict["print_stream"] is True:
            print(json.dumps(tweet))

if __name__ == '__main__':
    main()
