Python Twitter Search API
=========================

This project serves as a wrapper for the `Twitter premium and enterprise search APIs
<https://developer.twitter.com/en/products/tweets/search>`_, 
providing a command-line utility and a Python library.
Pretty docs can be seen `here <https://twitterdev.github.io/search-tweets-python/>`_.


Features
========

- Supports 30-day Search and Full Archive Search (not the standard Search API at this time).
- Command-line utility is pipeable to other tools (e.g., ``jq``).
- Automatically handles pagination of search results with specifiable limits
- Delivers a stream of data to the user for low in-memory requirements
- Handles enterprise and premium authentication methods
- Flexible usage within a python program
- Compatible with our group's `Tweet Parser <https://github.com/twitterdev/tweet_parser>`_ for rapid extraction of relevant data fields from each tweet payload
- Supports the Search Counts endpoint, which can reduce API call usage and provide rapid insights if you only need Tweet volumes and not Tweet payloads


Installation
============

The ``searchtweets`` library is on Pypi:

.. code:: bash

  pip install searchtweets

Or you can install the development version locally via

.. code:: bash

  git clone https://github.com/twitterdev/search-tweets-python
  cd search-tweets-python
  pip install -e .

----

.. include:: credential_handling.rst


----


Using the Comand Line Application
=================================

The library includes an application, ``search_tweets.py``, that provides rapid
access to Tweets. When you use ``pip`` to install this package,
``search_tweets.py`` is installed globally. The file is located in the
``tools/`` directory for those who want to run it locally.

Note that the ``--results-per-call`` flag specifies an argument to the API
( ``maxResults``, results returned per CALL), not as a hard max to number of
results returned from this program. The argument ``--max-results`` defines the
maximum number of results to return from a given call. All examples assume that
your credentials are set up correctly in the default location
- ``.twitter_keys.yaml`` or in environment variables.


**Stream json results to stdout without saving**

.. code:: bash

  search_tweets.py \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --print-stream


**Stream json results to stdout and save to a file**

.. code:: bash

  search_tweets.py \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --filename-prefix beyonce_geo \
    --print-stream


**Save to file without output**

.. code:: bash

  search_tweets.py \
    --max-results 100 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --filename-prefix beyonce_geo \
    --no-print-stream


Options can be passed via a configuration file (either ini or YAML). Example
files can be found in the ``tools/api_config_example.config`` or
``./tools/api_yaml_example.yaml`` files, which might look like this:

.. code:: bash

  [search_rules]
  from_date = 2017-06-01
  to_date = 2017-09-01
  pt_rule = beyonce has:geo

  [search_params]
  results_per_call = 500
  max_results = 500

  [output_params]
  save_file = True
  filename_prefix = beyonce
  results_per_file = 10000000

Or this:

.. code:: yaml

  search_rules:
      from-date: 2017-06-01
      to-date: 2017-09-01 01:01
      pt-rule: kanye

  search_params:
      results-per-call: 500
      max-results: 500

  output_params:
      save_file: True
      filename_prefix: kanye
      results_per_file: 10000000


When using a config file in conjunction with the command-line utility, you need
to specify your config file via the ``--config-file`` parameter. Additional
command-line arguments will either be *added* to the config file args or
**overwrite** the config file args if both are specified and present.


Example::

  search_tweets.py \
    --config-file myapiconfig.config \
    --no-print-stream

-----


Full options are listed below:

::

  $ search_tweets.py -h
  usage: search_tweets.py [-h] [--credential-file CREDENTIAL_FILE]
                        [--credential-file-key CREDENTIAL_YAML_KEY]
                        [--env-overwrite ENV_OVERWRITE]
                        [--config-file CONFIG_FILENAME]
                        [--account-type {premium,enterprise}]
                        [--count-bucket COUNT_BUCKET]
                        [--start-datetime FROM_DATE] [--end-datetime TO_DATE]
                        [--filter-rule PT_RULE]
                        [--results-per-call RESULTS_PER_CALL]
                        [--max-results MAX_RESULTS] [--max-pages MAX_PAGES]
                        [--results-per-file RESULTS_PER_FILE]
                        [--filename-prefix FILENAME_PREFIX]
                        [--no-print-stream] [--print-stream] [--debug]

  optional arguments:
    -h, --help            show this help message and exit
    --credential-file CREDENTIAL_FILE
                          Location of the yaml file used to hold your
                          credentials.
    --credential-file-key CREDENTIAL_YAML_KEY
                          the key in the credential file used for this session's
                          credentials. Defaults to search_tweets_api
    --env-overwrite ENV_OVERWRITE
                          Overwrite YAML-parsed credentials with any set
                          environment variables. See API docs or readme for
                          details.
    --config-file CONFIG_FILENAME
                          configuration file with all parameters. Far, easier to
                          use than the command-line args version., If a valid
                          file is found, all args will be populated, from there.
                          Remaining command-line args, will overrule args found
                          in the config, file.
    --account-type {premium,enterprise}
                          The account type you are using
    --count-bucket COUNT_BUCKET
                          Bucket size for counts API. Options:, day, hour,
                          minute (default is 'day').
    --start-datetime FROM_DATE
                          Start of datetime window, format 'YYYY-mm-DDTHH:MM'
                          (default: -30 days)
    --end-datetime TO_DATE
                          End of datetime window, format 'YYYY-mm-DDTHH:MM'
                          (default: most recent date)
    --filter-rule PT_RULE
                          PowerTrack filter rule (See: http://support.gnip.com/c
                          ustomer/portal/articles/901152-powertrack-operators)
    --results-per-call RESULTS_PER_CALL
                          Number of results to return per call (default 100; max
                          500) - corresponds to 'maxResults' in the API
    --max-results MAX_RESULTS
                          Maximum number of Tweets or Counts to return for this
                          session (defaults to 500)
    --max-pages MAX_PAGES
                          Maximum number of pages/API calls to use for this
                          session.
    --results-per-file RESULTS_PER_FILE
                          Maximum tweets to save per file.
    --filename-prefix FILENAME_PREFIX
                          prefix for the filename where tweet json data will be
                          stored.
    --no-print-stream     disable print streaming
    --print-stream        Print tweet stream to stdout
    --debug               print all info and warning messages


----

Using the Twitter Search APIs' Python Wrapper
=============================================

.. include:: api_example.rst





Contributing
============

.. include:: contributing.rst
