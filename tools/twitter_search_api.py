import os
import argparse
import json
import sys

if sys.version_info.major == 2:
    import ConfigParser as configparser
else:
    import configparser
import logging

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ModuleNotFoundError:
        from io import StringIO


from twittersearchapi.resul_stream import ResultStream
from twittersearchapi.utils import gen_endpoint
from gapi.utils import *


def parse_cmd_args():
    twitter_parser = argparse.ArgumentParser()

    twitter_parser.add_argument("--config-file", dest="config_filename",
                                default=None,
                                help=("configuration file with all parameters. Far",
                                      "easier to use than the command-line args version.",
                                      "If a valid file is found, all args will be populated",
                                      "from there. Remaining command-line args",
                                      "will overrule args found in the config",
                                      "file."))

    twitter_parser.add_argument("--account-name",
                                dest="account_name",
                                default=None,
                                help="Gnip API account name")

    twitter_parser.add_argument("-u",
                                "--user-name",
                                dest="username",
                                default=None,
                                help="User name")

    twitter_parser.add_argument("-p",
                                "--password",
                                dest="password",
                                default=None,
                                help="Password")

    twitter_parser.add_argument("-b",
                                "--bucket",
                                dest="count_bucket",
                                default="day",
                                help=("Bucket size for counts query. Options",
                                      "are day, hour, minute (default is 'day')."))

    twitter_parser.add_argument("-s",
                                "--start-datetime",
                                dest="from_date",
                                default=None,
                                help="Start of datetime window, format 'YYYY-mm-DDTHH:MM' (default: 30 days ago)")

    twitter_parser.add_argument("-e", "--end-datetime", dest="to_date",
                                default=None,
                                help="End of datetime window, format 'YYYY-mm-DDTHH:MM' (default: most recent activities)")

    twitter_parser.add_argument("-f", "--filter_rule", dest="pt_rule",
                                default="beyonce has:geo",
                                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")

    twitter_parser.add_argument("--stream-endpoint",
                                dest="endoint_label",
                                default=None,
                                help="Url of search endpoint. (See your Gnip console.)")

    twitter_parser.add_argument("--results-max", dest="results_max",
                                default=500,
                                help="Maximum results to return per api call (default 500; max 500)")

    twitter_parser.add_argument("--max_tweets", dest="max_tweets",
                                default=500,
                                type=int,
                                help="Maximum results to return for all pages; see -a option")

    twitter_parser.add_argument("--output-filename-prefix",
                                dest="output_filename_prefix",
                                default=None,
                                help="prefix for the filename where tweet json data will be stored."
                               )

    twitter_parser.add_argument("--output-file-path",
                                dest="output_file_path",
                                default="./data/",
                                help=("Create files in ./OUTPUT-FILE-PATH. This path must exist &",
                                      "will not be created. This option is available only with -a",
                                      "option. Default is no output files."))
    return twitter_parser


def main():
    args = parse_cmd_args().parse_args()

    print(json.dumps(args, spaces=4))


if __name__ == '__main__':
    main()
