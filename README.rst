Python Twitter Search API
=========================

This project serves as a wrapper for the `Twitter premium and enterprise
search
APIs <https://developer.twitter.com/en/products/tweets/search>`__,
providing a command-line utility and a Python library. Pretty docs can
be seen `here <https://twitterdev.github.io/search-tweets-python/>`__.

Features
========

-  Supports 30-day Search and Full Archive Search (not the standard
   Search API at this time).
-  Command-line utility is pipeable to other tools (e.g., ``jq``).
-  Automatically handles pagination of search results with specifiable
   limits
-  Delivers a stream of data to the user for low in-memory requirements
-  Handles enterprise and premium authentication methods
-  Flexible usage within a python program
-  Compatible with our group's `Tweet
   Parser <https://github.com/twitterdev/tweet_parser>`__ for rapid
   extraction of relevant data fields from each tweet payload
-  Supports the Search Counts endpoint, which can reduce API call usage
   and provide rapid insights if you only need Tweet volumes and not
   Tweet payloads

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

--------------

Credential Handling
===================

The premium and enterprise Search APIs use different authentication
methods and we attempt to provide a seamless way to handle
authentication for all customers. We know credentials can be tricking or
annoying - please read this in its entirety.

Premium clients will require the ``bearer_token`` and ``endpoint``
fields; Enterprise clients require ``username``, ``password``, and
``endpoint``. If you do not specify the ``account_type``, we attempt to
discern the account type and declare a warning about this behavior.

For premium search products, we are using app-only authentication and
the bearer tokens are not delivered with an expiration time. You can
provide either: - your application key and secret (the library will
handle bearer-token authentication) - a bearer token that you get
yourself

Many developers might find providing your application key and secret
more straightforward and letting this library manage your bearer token
generation for you. Please see
`here <https://developer.twitter.com/en/docs/basics/authentication/overview/application-only>`__
for an overview of the premium authentication method.

We support both YAML-file based methods and environment variables for
storing credentials, and provide flexible handling with sensible
defaults.

YAML method
-----------

For premium customers, the simplest credential file should look like
this:

.. code:: yaml

   search_tweets_api:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     consumer_key: <CONSUMER_KEY>
     consumer_secret: <CONSUMER_SECRET>

For enterprise customers, the simplest credential file should look like
this:

.. code:: yaml

   search_tweets_api:
     account_type: enterprise
     endpoint: <FULL_URL_OF_ENDPOINT>
     username: <USERNAME>
     password: <PW>

By default, this library expects this file at
``"~/.twitter_keys.yaml"``, but you can pass the relevant location as
needed, either with the ``--credential-file`` flag for the command-line
app or as demonstrated below in a Python program.

Both above examples require no special command-line arguments or
in-program arguments. The credential parsing methods, unless otherwise
specified, will look for a YAML key called ``search_tweets_api``.

For developers who have multiple endpoints and/or search products, you
can keep all credentials in the same file and specify specific keys to
use. ``--credential-file-key`` specifies this behavior in the command
line app. An example:

.. code:: yaml

   search_tweets_30_day_dev:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     consumer_key: <KEY>
     consumer_secret: <SECRET>
     (optional) bearer_token: <TOKEN>


   search_tweets_30_day_prod:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     bearer_token: <TOKEN>

   search_tweets_fullarchive_dev:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     bearer_token: <TOKEN>

   search_tweets_fullarchive_prod:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     bearer_token: <TOKEN>

Environment Variables
---------------------

If you want or need to pass credentials via environment variables, you
can set the appropriate variables for your product of the following:

::

   export SEARCHTWEETS_ENDPOINT=
   export SEARCHTWEETS_USERNAME=
   export SEARCHTWEETS_PASSWORD=
   export SEARCHTWEETS_BEARER_TOKEN=
   export SEARCHTWEETS_ACCOUNT_TYPE=
   export SEARCHTWEETS_CONSUMER_KEY=
   export SEARCHTWEETS_CONSUMER_SECRET=

The ``load_credentials`` function will attempt to find these variables
if it cannot load fields from the YAML file, and it will **overwrite any
credentials from the YAML file that are present as environment
variables** if they have been parsed. This behavior can be changed by
setting the ``load_credentials`` parameter ``env_overwrite`` to
``False``.

The following cells demonstrates credential handling in the Python
library.

.. code:: python

   from searchtweets import load_credentials

.. code:: python

   load_credentials(filename="./search_tweets_creds_example.yaml",
                    yaml_key="search_tweets_ent_example",
                    env_overwrite=False)

::

   {'username': '<MY_USERNAME>',
    'password': '<MY_PASSWORD>',
    'endpoint': '<MY_ENDPOINT>'}

.. code:: python

   load_credentials(filename="./search_tweets_creds_example.yaml",
                    yaml_key="search_tweets_premium_example",
                    env_overwrite=False)

::

   {'bearer_token': '<A_VERY_LONG_MAGIC_STRING>',
    'endpoint': 'https://api.twitter.com/1.1/tweets/search/30day/dev.json',
    'extra_headers_dict': None}

Environment Variable Overrides
------------------------------

If we set our environment variables, the program will look for them
regardless of a YAML file's validity or existence.

.. code:: python

   import os
   os.environ["SEARCHTWEETS_USERNAME"] = "<ENV_USERNAME>"
   os.environ["SEARCHTWEETS_PASSWORD"] = "<ENV_PW>"
   os.environ["SEARCHTWEETS_ENDPOINT"] = "<https://endpoint>"

   load_credentials(filename="nothing_here.yaml", yaml_key="no_key_here")

::

   cannot read file nothing_here.yaml
   Error parsing YAML file; searching for valid environment variables

::

   {'username': '<ENV_USERNAME>',
    'password': '<ENV_PW>',
    'endpoint': '<https://endpoint>'}

Command-line app
----------------

the flags:

-  ``--credential-file <FILENAME>``
-  ``--credential-file-key <KEY>``
-  ``--env-overwrite``

are used to control credential behavior from the command-line app.

--------------

Using the Comand Line Application
=================================

The library includes an application, ``search_tweets.py``, that provides
rapid access to Tweets. When you use ``pip`` to install this package,
``search_tweets.py`` is installed globally. The file is located in the
``tools/`` directory for those who want to run it locally.

Note that the ``--results-per-call`` flag specifies an argument to the
API ( ``maxResults``, results returned per CALL), not as a hard max to
number of results returned from this program. The argument
``--max-results`` defines the maximum number of results to return from a
given call. All examples assume that your credentials are set up
correctly in the default location - ``.twitter_keys.yaml`` or in
environment variables.

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

One or more custom headers can be specified from the command line, using
the ``--extra-headers`` argument and a JSON-formatted string
representing a dictionary of extra headers:

.. code:: bash

   search_tweets.py \
     --filter-rule "beyonce has:hashtags" \
     --extra-headers '{"<MY_HEADER_KEY>":"<MY_HEADER_VALUE>"}'

Options can be passed via a configuration file (either ini or YAML).
Example files can be found in the ``tools/api_config_example.config`` or
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

Custom headers can be specified in a config file, under a specific
credentials key:

.. code:: yaml

   search_tweets_api:
     account_type: premium
     endpoint: <FULL_URL_OF_ENDPOINT>
     username: <USERNAME>
     password: <PW>
     extra_headers:
       <MY_HEADER_KEY>: <MY_HEADER_VALUE>

When using a config file in conjunction with the command-line utility,
you need to specify your config file via the ``--config-file``
parameter. Additional command-line arguments will either be *added* to
the config file args or **overwrite** the config file args if both are
specified and present.

Example:

::

   search_tweets.py \
     --config-file myapiconfig.config \
     --no-print-stream

--------------

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
                         [--no-print-stream] [--print-stream]
                         [--extra-headers EXTRA_HEADERS] [--debug]

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
     --extra-headers EXTRA_HEADERS
                           JSON-formatted str representing a dict of additional
                           request headers
     --debug               print all info and warning messages

--------------

Using the Twitter Search APIs' Python Wrapper
=============================================

Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

We'll assume that credentials are in the default location,
``~/.twitter_keys.yaml``.

.. code:: python

   from searchtweets import ResultStream, gen_rule_payload, load_credentials

Enterprise setup
----------------

.. code:: python

   enterprise_search_args = load_credentials("~/.twitter_keys.yaml",
                                             yaml_key="search_tweets_enterprise",
                                             env_overwrite=False)

Premium Setup
-------------

.. code:: python

   premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                          yaml_key="search_tweets_premium",
                                          env_overwrite=False)

There is a function that formats search API rules into valid json
queries called ``gen_rule_payload``. It has sensible defaults, such as
pulling more Tweets per call than the default 100 (but note that a
sandbox environment can only have a max of 100 here, so if you get
errors, please check this) not including dates, and defaulting to hourly
counts when using the counts api. Discussing the finer points of
generating search rules is out of scope for these examples; I encourage
you to see the docs to learn the nuances within, but for now let's see
what a rule looks like.

.. code:: python

   rule = gen_rule_payload("beyonce", results_per_call=100) # testing with a sandbox account
   print(rule)

::

   {"query":"beyonce","maxResults":100}

This rule will match tweets that have the text ``beyonce`` in them.

From this point, there are two ways to interact with the API. There is a
quick method to collect smaller amounts of Tweets to memory that
requires less thought and knowledge, and interaction with the
``ResultStream`` object which will be introduced later.

Fast Way
--------

We'll use the ``search_args`` variable to power the configuration point
for the API. The object also takes a valid PowerTrack rule and has
options to cutoff search when hitting limits on both number of Tweets
and API calls.

We'll be using the ``collect_results`` function, which has three
parameters.

-  rule: a valid PowerTrack rule, referenced earlier
-  max_results: as the API handles pagination, it will stop collecting
   when we get to this number
-  result_stream_args: configuration args that we've already specified.

For the remaining examples, please change the args to either premium or
enterprise depending on your usage.

Let's see how it goes:

.. code:: python

   from searchtweets import collect_results

.. code:: python

   tweets = collect_results(rule,
                            max_results=100,
                            result_stream_args=enterprise_search_args) # change this if you need to

By default, Tweet payloads are lazily parsed into a ``Tweet``
`object <https://twitterdev.github.io/tweet_parser/>`__. An overwhelming
number of Tweet attributes are made available directly, as such:

.. code:: python

   [print(tweet.all_text, end='\n\n') for tweet in tweets[0:10]];

::

   Jay-Z &amp; Beyoncé sat across from us at dinner tonight and, at one point, I made eye contact with Beyoncé. My limbs turned to jello and I can no longer form a coherent sentence. I have seen the eyes of the lord.

   Beyoncé and it isn't close. https://t.co/UdOU9oUtuW

   As you could guess.. Signs by Beyoncé will always be my shit.

   When Beyoncé adopts a dog 🙌🏾 https://t.co/U571HyLG4F

   Hold up, you can't just do that to Beyoncé
   https://t.co/3p14DocGqA

   Why y'all keep using Rihanna and Beyoncé gifs to promote the show when y'all let Bey lose the same award she deserved 3 times and let Rihanna leave with nothing but the clothes on her back? https://t.co/w38QpH0wma

   30) anybody tell you that you look like Beyoncé https://t.co/Vo4Z7bfSCi

   Mi Beyoncé favorita https://t.co/f9Jp600l2B
   Beyoncé necesita ver esto. Que diosa @TiniStoessel 🔥🔥🔥 https://t.co/gadVJbehQZ

   Joanne Pearce Is now playing IF I WAS A BOY - BEYONCE.mp3 by !

   I'm trynna see beyoncé's finsta before I die

.. code:: python

   [print(tweet.created_at_datetime) for tweet in tweets[0:10]];

::

   2018-01-17 00:08:50
   2018-01-17 00:08:49
   2018-01-17 00:08:44
   2018-01-17 00:08:42
   2018-01-17 00:08:42
   2018-01-17 00:08:42
   2018-01-17 00:08:40
   2018-01-17 00:08:38
   2018-01-17 00:08:37
   2018-01-17 00:08:37

.. code:: python

   [print(tweet.generator.get("name")) for tweet in tweets[0:10]];

::

   Twitter for iPhone
   Twitter for iPhone
   Twitter for iPhone
   Twitter for iPhone
   Twitter for iPhone
   Twitter for iPhone
   Twitter for Android
   Twitter for iPhone
   Airtime Pro
   Twitter for iPhone

Voila, we have some Tweets. For interactive environments and other cases
where you don't care about collecting your data in a single load or
don't need to operate on the stream of Tweets or counts directly, I
recommend using this convenience function.

Working with the ResultStream
-----------------------------

The ResultStream object will be powered by the ``search_args``, and
takes the rules and other configuration parameters, including a hard
stop on number of pages to limit your API call usage.

.. code:: python

   rs = ResultStream(rule_payload=rule,
                     max_results=500,
                     max_pages=1,
                     **premium_search_args)

   print(rs)

::

   ResultStream: 
   	{
       "username":null,
       "endpoint":"https:\/\/api.twitter.com\/1.1\/tweets\/search\/30day\/dev.json",
       "rule_payload":{
           "query":"beyonce",
           "maxResults":100
       },
       "tweetify":true,
       "max_results":500
   }

There is a function, ``.stream``, that seamlessly handles requests and
pagination for a given query. It returns a generator, and to grab our
500 Tweets that mention ``beyonce`` we can do this:

.. code:: python

   tweets = list(rs.stream())

Tweets are lazily parsed using our `Tweet
Parser <https://twitterdev.github.io/tweet_parser/>`__, so tweet data is
very easily extractable.

.. code:: python

   # using unidecode to prevent emoji/accents printing 
   [print(tweet.all_text) for tweet in tweets[0:10]];

::

   gente socorro kkkkkkkkkk BEYONCE https://t.co/kJ9zubvKuf
   Jay-Z &amp; Beyoncé sat across from us at dinner tonight and, at one point, I made eye contact with Beyoncé. My limbs turned to jello and I can no longer form a coherent sentence. I have seen the eyes of the lord.
   Beyoncé and it isn't close. https://t.co/UdOU9oUtuW
   As you could guess.. Signs by Beyoncé will always be my shit.
   When Beyoncé adopts a dog 🙌🏾 https://t.co/U571HyLG4F
   Hold up, you can't just do that to Beyoncé
   https://t.co/3p14DocGqA
   Why y'all keep using Rihanna and Beyoncé gifs to promote the show when y'all let Bey lose the same award she deserved 3 times and let Rihanna leave with nothing but the clothes on her back? https://t.co/w38QpH0wma
   30) anybody tell you that you look like Beyoncé https://t.co/Vo4Z7bfSCi
   Mi Beyoncé favorita https://t.co/f9Jp600l2B
   Beyoncé necesita ver esto. Que diosa @TiniStoessel 🔥🔥🔥 https://t.co/gadVJbehQZ
   Joanne Pearce Is now playing IF I WAS A BOY - BEYONCE.mp3 by !

Counts Endpoint
---------------

We can also use the Search API Counts endpoint to get counts of Tweets
that match our rule. Each request will return up to *30* results, and
each count request can be done on a minutely, hourly, or daily basis.
The underlying ``ResultStream`` object will handle converting your
endpoint to the count endpoint, and you have to specify the
``count_bucket`` argument when making a rule to use it.

The process is very similar to grabbing Tweets, but has some minor
differences.

*Caveat - premium sandbox environments do NOT have access to the Search
API counts endpoint.*

.. code:: python

   count_rule = gen_rule_payload("beyonce", count_bucket="day")

   counts = collect_results(count_rule, result_stream_args=enterprise_search_args)

Our results are pretty straightforward and can be rapidly used.

.. code:: python

   counts

::

   [{'count': 366, 'timePeriod': '201801170000'},
    {'count': 44580, 'timePeriod': '201801160000'},
    {'count': 61932, 'timePeriod': '201801150000'},
    {'count': 59678, 'timePeriod': '201801140000'},
    {'count': 44014, 'timePeriod': '201801130000'},
    {'count': 46607, 'timePeriod': '201801120000'},
    {'count': 41523, 'timePeriod': '201801110000'},
    {'count': 47056, 'timePeriod': '201801100000'},
    {'count': 65506, 'timePeriod': '201801090000'},
    {'count': 95251, 'timePeriod': '201801080000'},
    {'count': 162883, 'timePeriod': '201801070000'},
    {'count': 106344, 'timePeriod': '201801060000'},
    {'count': 93542, 'timePeriod': '201801050000'},
    {'count': 110415, 'timePeriod': '201801040000'},
    {'count': 127523, 'timePeriod': '201801030000'},
    {'count': 131952, 'timePeriod': '201801020000'},
    {'count': 176157, 'timePeriod': '201801010000'},
    {'count': 57229, 'timePeriod': '201712310000'},
    {'count': 72277, 'timePeriod': '201712300000'},
    {'count': 72051, 'timePeriod': '201712290000'},
    {'count': 76371, 'timePeriod': '201712280000'},
    {'count': 61578, 'timePeriod': '201712270000'},
    {'count': 55118, 'timePeriod': '201712260000'},
    {'count': 59115, 'timePeriod': '201712250000'},
    {'count': 106219, 'timePeriod': '201712240000'},
    {'count': 114732, 'timePeriod': '201712230000'},
    {'count': 73327, 'timePeriod': '201712220000'},
    {'count': 89171, 'timePeriod': '201712210000'},
    {'count': 192381, 'timePeriod': '201712200000'},
    {'count': 85554, 'timePeriod': '201712190000'},
    {'count': 57829, 'timePeriod': '201712180000'}]

Dated searches / Full Archive Search
------------------------------------

**Note that this will only work with the full archive search option**,
which is available to my account only via the enterprise options. Full
archive search will likely require a different endpoint or access
method; please see your developer console for details.

Let's make a new rule and pass it dates this time.

``gen_rule_payload`` takes timestamps of the following forms:

-  ``YYYYmmDDHHMM``
-  ``YYYY-mm-DD`` (which will convert to midnight UTC (00:00)
-  ``YYYY-mm-DD HH:MM``
-  ``YYYY-mm-DDTHH:MM``

Note - all Tweets are stored in UTC time.

.. code:: python

   rule = gen_rule_payload("from:jack",
                           from_date="2017-09-01", #UTC 2017-09-01 00:00
                           to_date="2017-10-30",#UTC 2017-10-30 00:00
                           results_per_call=500)
   print(rule)

::

   {"query":"from:jack","maxResults":500,"toDate":"201710300000","fromDate":"201709010000"}

.. code:: python

   tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: python

   [print(tweet.all_text) for tweet in tweets[0:10]];

::

   More clarity on our private information policy and enforcement. Working to build as much direct context into the product too https://t.co/IrwBexPrBA
   To provide more clarity on our private information policy, we’ve added specific examples of what is/is not a violation and insight into what we need to remove this type of content from the service. https://t.co/NGx5hh2tTQ
   Launching violent groups and hateful images/symbols policy on November 22nd https://t.co/NaWuBPxyO5
   We will now launch our policies on violent groups and hateful imagery and hate symbols on Nov 22. During the development process, we received valuable feedback that we’re implementing before these are published and enforced. See more on our policy development process here 👇 https://t.co/wx3EeH39BI
   @WillStick @lizkelley Happy birthday Liz!
   Off-boarding advertising from all accounts owned by Russia Today (RT) and Sputnik.

   We’re donating all projected earnings ($1.9mm) to support external research into the use of Twitter in elections, including use of malicious automation and misinformation. https://t.co/zIxfqqXCZr
   @TMFJMo @anthonynoto Thank you
   @gasca @stratechery @Lefsetz letter
   @gasca @stratechery Bridgewater’s Daily Observations
   Yup!!!! ❤️❤️❤️❤️ #davechappelle https://t.co/ybSGNrQpYF
   @ndimichino Sometimes
   Setting up at @CampFlogGnaw https://t.co/nVq8QjkKsf

.. code:: python

   rule = gen_rule_payload("from:jack",
                           from_date="2017-09-20",
                           to_date="2017-10-30",
                           count_bucket="day",
                           results_per_call=500)
   print(rule)

::

   {"query":"from:jack","toDate":"201710300000","fromDate":"201709200000","bucket":"day"}

.. code:: python

   counts = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: python

   [print(c) for c in counts];

::

   {'timePeriod': '201710290000', 'count': 0}
   {'timePeriod': '201710280000', 'count': 0}
   {'timePeriod': '201710270000', 'count': 3}
   {'timePeriod': '201710260000', 'count': 6}
   {'timePeriod': '201710250000', 'count': 4}
   {'timePeriod': '201710240000', 'count': 4}
   {'timePeriod': '201710230000', 'count': 0}
   {'timePeriod': '201710220000', 'count': 0}
   {'timePeriod': '201710210000', 'count': 3}
   {'timePeriod': '201710200000', 'count': 2}
   {'timePeriod': '201710190000', 'count': 1}
   {'timePeriod': '201710180000', 'count': 6}
   {'timePeriod': '201710170000', 'count': 2}
   {'timePeriod': '201710160000', 'count': 2}
   {'timePeriod': '201710150000', 'count': 1}
   {'timePeriod': '201710140000', 'count': 64}
   {'timePeriod': '201710130000', 'count': 3}
   {'timePeriod': '201710120000', 'count': 4}
   {'timePeriod': '201710110000', 'count': 8}
   {'timePeriod': '201710100000', 'count': 4}
   {'timePeriod': '201710090000', 'count': 1}
   {'timePeriod': '201710080000', 'count': 0}
   {'timePeriod': '201710070000', 'count': 0}
   {'timePeriod': '201710060000', 'count': 1}
   {'timePeriod': '201710050000', 'count': 3}
   {'timePeriod': '201710040000', 'count': 5}
   {'timePeriod': '201710030000', 'count': 8}
   {'timePeriod': '201710020000', 'count': 5}
   {'timePeriod': '201710010000', 'count': 0}
   {'timePeriod': '201709300000', 'count': 0}
   {'timePeriod': '201709290000', 'count': 0}
   {'timePeriod': '201709280000', 'count': 9}
   {'timePeriod': '201709270000', 'count': 41}
   {'timePeriod': '201709260000', 'count': 13}
   {'timePeriod': '201709250000', 'count': 6}
   {'timePeriod': '201709240000', 'count': 7}
   {'timePeriod': '201709230000', 'count': 3}
   {'timePeriod': '201709220000', 'count': 0}
   {'timePeriod': '201709210000', 'count': 1}
   {'timePeriod': '201709200000', 'count': 7}

Contributing
============

Any contributions should follow the following pattern:

1. Make a feature or bugfix branch, e.g.,
   ``git checkout -b my_new_feature``
2. Make your changes in that branch
3. Ensure you bump the version number in ``searchtweets/_version.py`` to
   reflect your changes. We use `Semantic
   Versioning <https://semver.org>`__, so non-breaking enhancements
   should increment the minor version, e.g., ``1.5.0 -> 1.6.0``, and
   bugfixes will increment the last version, ``1.6.0 -> 1.6.1``.
4. Create a pull request

After the pull request process is accepted, package maintainers will
handle building documentation and distribution to Pypi.

For reference, distributing to Pypi is accomplished by the following
commands, ran from the root directory in the repo:

.. code:: bash

   python setup.py bdist_wheel
   python setup.py sdist
   twine upload dist/*

How to build the documentation:

Building the documentation requires a few Sphinx packages to build the
webpages:

.. code:: bash

   pip install sphinx
   pip install sphinx_bootstrap_theme
   pip install sphinxcontrib-napoleon

Then (once your changes are committed to master) you should be able to
run the documentation-generating bash script and follow the
instructions:

.. code:: bash

   bash build_sphinx_docs.sh master searchtweets

Note that this README is also generated, and so after any README changes
you'll need to re-build the README (you need pandoc version 2.1+ for
this) and commit the result:

.. code:: bash

   bash make_readme.sh
