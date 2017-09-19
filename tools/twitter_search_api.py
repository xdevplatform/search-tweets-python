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


from gapi.gnipapi import ResultStream
from gapi.gnipapi import gen_endpoint
from gapi.utils import *


USE_CASES = ["json", "wordcount","users", "rate", "links", "timeline", "geo", "audience"]

import configparser

def gen_params_from_config(config_dict):
    endpoint = gen_endpoint(config_dict["search_api"],
                            config_dict["account_name"],
                            config_dict["endpoint_label"],
                            config_dict.get("count_endpoint", None)
                           )
    rule = gen_rule_payload(pt_rule=config_dict["pt_rule"],
                            from_date=config_dict.get("from_date", None),
                            to_date=config_dict.get("to_date", None),
                            max_results=config_dict.get("max_results", None),
                            count_bucket=config_dict.get("count_bucket", None)
                           )


    _dict = {"url": endpoint,
             "username": config_dict["username"],
             "password": config_dict["password"],
             "rule_payload": rule,
             "max_tweets": config_dict.get("max_tweets")
            }
    return _dict


def read_configfile(filename):
    config = configparser.ConfigParser()

    with open(filename) as f:
        config.read_file(f)

    config_dict = merge_dicts(*[dict(config[s]) for s in config.sections()])
    return config_dict





def parse_cmd_args():
    twitter_parser = argparse.ArgumentParser(
        description="GnipSearch supports the following use cases: {}".format(USE_CASES))


    twitter_parser.add_argument("--config-file", dest="config_filename",
        default=None, help=("configuration file with all parameters. Far",
        "easier to use than the command-line args version. If a valid file",
        "is found, all args will be populated from there."))

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
                                default=None,help="Password")

    twitter_parser.add_argument("use_case",
                                metavar= "USE_CASE",
                                choices=USE_CASES,
                                help="Use case for this search.")

    # twitter_parser.add_argument("-c", "--csv", dest="csv_flag", action="store_true",
    #         default=False,
    #         help="Return comma-separated 'date, counts' or geo data.")

    twitter_parser.add_argument("-b",
            "--bucket",
            dest="count_bucket", 
            default="day", 
            help="Bucket size for counts query. Options are day, hour, minute (default is 'day').")

    twitter_parser.add_argument("-s", "--start-datetime", dest="from_date",
            default=None,
            help="Start of datetime window, format 'YYYY-mm-DD:HH:MM' (default: 30 days ago)")

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

    twitter_parser.add_argument("-n", "--results-max", dest="results_max",
            default=500,
            help="Maximum results to return per api call (default 500; max 500)")

    twitter_parser.add_argument("-N", "--max_tweets", dest="max_tweets",
            default=500, type=int, help="Maximum results to return for all pages; see -a option")


    twitter_parser.add_argument("-w", "--output-file-path", dest="output_file_path", default=None,
            help="Create files in ./OUTPUT-FILE-PATH. This path must exist and will not be created. This option is available only with -a option. Default is no output files.")
    return twitter_parser


def main():
    args = parse_cmd_args().parse_args()
    if args["config_filename"]:

    print(json.dumps(args, spaces=4))


if __name__ == '__main__':
    main()
