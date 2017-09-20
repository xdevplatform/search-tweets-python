Python Twitter Search API
=========================


This library serves as a python interface to the Twitter/GNIP Search API. It allows use both from a command-line utility and from with a python program. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.


Features
========

- delivers a stream of data to the user for low in-memory requirements
- automatically handles paagination of results with easy hard cutoffs
- will handle both token authentication and basic username/password authentication
- quick to handle in a standalone program or interactive environment
- compatible with our group's Tweet Parser for extraction of relevant data fields from each tweet payload
- supports the Search Counts API to estimate volumes for queries without using many API calls
- command-line utility is pipeable to other tools (e.g., ``jq``).


Installation
============

We will soon handle releases via PyPy, but you can also install the current master version via::

  pip install git+https://github.com/tw-ddis/twitter_search_api.git

Or the development version locally via::
  git clone https://github.com/tw-ddis/twitter_search_api.git
  cd twitter_search_api
  pip install -e .



Command line examples
=====================

Stream json results to stdout without saving::

  python twitter_search_api.py \
    --user-name <USERNAME> \
    --account-name <ACCOUNT> \
    --password <PW> \
    --stream-endpoint ogformat.json \
    --search-api fullarchive \
    --max-tweets 1000 \
    --filter-rule "beyonce has:geo" \
    --print-stream


Stream json results to stdout and save to a file::

  python twitter_search_api.py \
    --user-name <USERNAME> \
    --account-name <ACCOUNT> \
    --password <PW> \
    --stream-endpoint ogformat.json \
    --search-api fullarchive \
    --max-tweets 1000 \
    --filter-rule "beyonce has:geo" \
    --filename-prefix beyonce_geo \
    --print-stream


Save to file without output::

  python twitter_search_api.py \
    --user-name <USERNAME> \
    --account-name <ACCOUNT> \
    --password <PW> \
    --stream-endpoint ogformat.json \
    --search-api fullarchive \
    --max-tweets 1000 \
    --filter-rule "beyonce has:geo" \
    --filename-prefix beyonce_geo \
    --no-print-stream



It can be far easier to specify your information in a configuration file. An example file can be found in the ``tools/api_config_example.config`` file, but will look something like this::

  [credentials]
  account_name = <account_name>
  username =  <user_name>
  password = morrisey_on_twitter


  [api_info]
  search_api = fullarchive
  endpoint_label = ogformat.json

  [gnip_search_rules]
  from_date = 2017-06-01
  to_date = 2017-09-01
  max_results = 500
  pt_rule = beyonce has:geo


  [search_params]
  max_tweets = 500

  [output_params]
  save_file = True
  output_file_prefix = beyonce


When using a config file in conjunction with the command-line utility, you need to specify your config file via the ``--config-file`` parameter. Additional command-line arguments will either be *added* to the config file args or **overwrite** the config file args if both are specified and present.



