Python client for Labs Recent search
====================================

This project serves as a wrapper for the `Twitter Labs recent search
APIs <https://developer.twitter.com/en/docs/labs/recent-search/>`__,
providing a command-line utility and a Python library.

This is a fork of the premium/enterprise search client at https://github.com/twitterdev/search-tweets-python.

If you are working with an enterprise or premium 30-day or Full-archive search endpoint, the ```master``` branch of this repository has what you need.


Features
========

- Supports Labs Recent search, v2. 
- Supports a new "polling" mode using the new Labs ```since-id``` search request parameter. The ```since-id```, along with the new ```until-id``` provide a way to navigate the public Tweet archive by Tweet ID. 
- Supports additional ways to specify ```start-time``` and ```end-time``` request parameters:

  - d# - For example, 'd2' sets ```start-time``` to (exactly) two days ago. 
  - h# - For example, 'h12' sets ```start-time``` to (exactly) twelve hours ago. 
  - m# - For example, 'm15' sets ```start-time``` to (exactly) fifteen minutes ago. 
  
  These are handy for kicking off searches with a backfill period, and also work with the ```end-time``` request parameter. 

These features were inherited from the enterprise/premium version:

-  Command-line utility is pipeable to other tools (e.g., ``jq``).
-  Automatically handles pagination of search results with specifiable limits.
-  Delivers a stream of data to the user for low in-memory requirements.
-  Handles OAuth 2 and Bearer Token authentication.
-  Flexible usage within a python program.


Labs updates
============

When migrating this Python search client from an enterprise or premium search endpoint, the following updates were made:

- Added support for GET requests (and removed POST support for now)
- Added support for since_id and until_id request parameters.
- Updated pagination details.
- Updated app command-line parlance
      -  --start-datetime → --start-time
      -  --end-datetime → --end-time
      -  --filter-rule → --query
      -  --max-results → --max-tweets
      - Dropped --account-type.
      - Dropped --count-bucket. Removed search 'counts' endpoint support. This endpoint is currently not available in Labs.
    

Command-line options
=====================

usage: search_tweets.py 

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
  --start-time START_TIME
                        Start of datetime window, format 'YYYY-mm-DDTHH:MM'
                        (default: -7 days)
  --end-time END_TIME   End of datetime window, format 'YYYY-mm-DDTHH:MM'
                        (default: most recent date)
  --query QUERY         Search query. (See:
                        https://developer.twitter.com/en/docs/labs/recent-
                        search/guides/search-queries)
  --since-id SINCE_ID   Tweet ID, will start search from Tweets after this
                        one. (See:
                        https://developer.twitter.com/en/docs/labs/recent-
                        search/guides/pagination)
  --until-id UNTIL_ID   Tweet ID, will end search from Tweets before this one.
                        (See:
                        https://developer.twitter.com/en/docs/labs/recent-
                        search/guides/pagination)
  --results-per-call RESULTS_PER_CALL
                        Number of results to return per call (default 10; max
                        100) - corresponds to 'max_results' in the API
  --max-tweets MAX_TWEETS
                        Maximum number of Tweets to return for this session of
                        requests.
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
  --extra-headers EXTRA_HEADERS
                        JSON-formatted str representing a dict of additional
                        request headers
  --debug               print all info and warning messages


Migrating from enterprise/premium library
=========================================










Installation
=============

{Are there any new conventions?}
Maintaing two packages: 
+ searchtweets (current enterprise/premium package)
+ searchtweetslabs 
Eventually, there will be searchtweetsv2, and searchtweets will be dropped.

The searchtweets library is on Pypi:

pip install searchtweets
Or you can install the development version locally via

git clone https://github.com/twitterdev/search-tweets-python
cd search-tweets-python
pip install -e .
Credential Handling
The premium and enterprise Search APIs use different authentication methods and we attempt to provide a seamless way to handle authentication for all customers. We know credentials can be tricky or annoying - please read this in its entirety.

Premium clients will require the bearer_token and endpoint fields; Enterprise clients require username, password, and endpoint. If you do not specify the account_type, we attempt to discern the account type and declare a warning about this behavior.

For premium search products, we are using app-only authentication and the bearer tokens are not delivered with an expiration time. You can provide either: - your application key and secret (the library will handle bearer-token authentication) - a bearer token that you get yourself

Many developers might find providing your application key and secret more straightforward and letting this library manage your bearer token generation for you. Please see here for an overview of the premium authentication method.

We support both YAML-file based methods and environment variables for storing credentials, and provide flexible handling with sensible defaults.

YAML method
For premium customers, the simplest credential file should look like this:

search_tweets_endpoint:
  endpoint: <FULL_URL_OF_ENDPOINT>
  consumer_key: <CONSUMER_KEY>
  consumer_secret: <CONSUMER_SECRET>

By default, this library expects this file at "~/.twitter_keys.yaml", but you can pass the relevant location as needed, either with the --credential-file flag for the command-line app or as demonstrated below in a Python program.

Both above examples require no special command-line arguments or in-program arguments. The credential parsing methods, unless otherwise specified, will look for a YAML key called search_tweets_api.

For developers who have multiple endpoints and/or search products, you can keep all credentials in the same file and specify specific keys to use. --credential-file-key specifies this behavior in the command line app. An example:

search_tweets_labsv1:
  endpoint: <FULL_URL_OF_ENDPOINT>
  consumer_key: <KEY>
  consumer_secret: <SECRET>
  (optional) bearer_token: <TOKEN>

search_tweets_labsv2:
  endpoint: <FULL_URL_OF_ENDPOINT>
  consumer_key: <KEY>
  consumer_secret: <SECRET>
  (optional) bearer_token: <TOKEN>


Environment Variables

If you want or need to pass credentials via environment variables, you can set the appropriate variables for your product of the following:

export SEARCHTWEETS_ENDPOINT=
export SEARCHTWEETS_BEARER_TOKEN=
export SEARCHTWEETS_CONSUMER_KEY=
export SEARCHTWEETS_CONSUMER_SECRET=

The load_credentials function will attempt to find these variables if it cannot load fields from the YAML file, and it will overwrite any credentials from the YAML file that are present as environment variables if they have been parsed. This behavior can be changed by setting the load_credentials parameter env_overwrite to False.

The following cells demonstrates credential handling in the Python library.

from searchtweets import load_credentials
load_credentials(filename="./search_tweets_creds_example.yaml",
                 yaml_key="search_tweets_ent_example",
                 env_overwrite=False)
{ 'endpoint': '<MY_ENDPOINT>'}

load_credentials(filename="./search_tweets_creds_example.yaml",
                 yaml_key="search_tweetsv2_example",
                 env_overwrite=False)
                 
{'bearer_token': '<A_VERY_LONG_MAGIC_STRING>',
 'endpoint': 'https://api.twitter.com/labs/2/tweets/search',
 'extra_headers_dict': None}
 
 
Environment Variable Overrides

If we set our environment variables, the program will look for them regardless of a YAML file's validity or existence.

import os
os.environ["SEARCHTWEETS_USERNAME"] = "<ENV_USERNAME>"
os.environ["SEARCHTWEETS_BEARERTOKEN"] = "<ENV_BEARER>"
os.environ["SEARCHTWEETS_ENDPOINT"] = "<https://endpoint>"

load_credentials(filename="nothing_here.yaml", yaml_key="no_key_here")
cannot read file nothing_here.yaml

Error parsing YAML file; searching for valid environment variables
{'bearer_token': '<ENV_BEARER_TOKEN>',
 'endpoint': '<https://endpoint>'}

Command-line app

the flags:

--credential-file <FILENAME>
--credential-file-key <KEY>
--env-overwrite
are used to control credential behavior from the command-line app.

Using the Comand Line Application
The library includes an application, search_tweets.py, that provides rapid access to Tweets. When you use pip to install this package, search_tweets.py is installed globally. The file is located in the tools/ directory for those who want to run it locally.

Note that the --results-per-call flag specifies an argument to the API ( maxResults, results returned per CALL), not as a hard max to number of results returned from this program. The argument --max-results defines the maximum number of results to return from a given call. All examples assume that your credentials are set up correctly in the default location - .twitter_keys.yaml or in environment variables.

Stream json results to stdout without saving

search_tweets.py \
  --max-results 1000 \
  --results-per-call 100 \
  --query "(snow OR rain) has:media -is:retweet" \
  --print-stream
Stream json results to stdout and save to a file

search_tweets.py \
  --max-results 1000 \
  --results-per-call 100 \
  --query "(snow OR rain) has:media -is:retweet" \
  --filename-prefix beyonce_geo \
  --print-stream
Save to file without output

search_tweets.py \
  --max-results 100 \
  --results-per-call 100 \
  --query "(snow OR rain) has:media -is:retweet" \
  --filename-prefix beyonce_geo \
  --no-print-stream
One or more custom headers can be specified from the command line, using the --extra-headers argument and a JSON-formatted string representing a dictionary of extra headers:

search_tweets.py \
  --query "(snow OR rain) has:media -is:retweet" \
  --extra-headers '{"<MY_HEADER_KEY>":"<MY_HEADER_VALUE>"}'
Options can be passed via a configuration file (either ini or YAML). Example files can be found in the tools/api_config_example.config or ./tools/api_yaml_example.yaml files, which might look like this:

[search_rules]
start_time = 2020-05-01
end_time = 2020-05-01
query = (snow OR rain) has:media -is:retweet

[search_params]
results_per_call = 100
max_tweets = 10000

[output_params]
save_file = True
filename_prefix = weather-pics
results_per_file = 10000000

Or this:

search_rules:
    start_time: 2017-06-01
    end_time: 2017-09-01 01:01
    query: (snow OR rain) has:media -is:retweet

search_params:
    results-per-call: 100
    max-results: 500

output_params:
    save_file: True
    filename_prefix: (snow OR rain) has:media -is:retweet
    results_per_file: 10000000
Custom headers can be specified in a config file, under a specific credentials key:

search_tweets_api:
  endpoint: <FULL_URL_OF_ENDPOINT>
  bearer_token: <AAAAAloooooogString>
  extra_headers:
    <MY_HEADER_KEY>: <MY_HEADER_VALUE>
When using a config file in conjunction with the command-line utility, you need to specify your config file via the --config-file parameter. Additional command-line arguments will either be added to the config file args or overwrite the config file args if both are specified and present.

Example:

search_tweets.py \
  --config-file myapiconfig.config \
  --no-print-stream
Full options are listed below:

$ search_tweets.py -h

usage: search_tweets.py [-h] [--credential-file CREDENTIAL_FILE]
                      [--credential-file-key CREDENTIAL_YAML_KEY]



