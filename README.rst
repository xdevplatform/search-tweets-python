.. .. image:: https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2
..   :target: https://developer.twitter.com/en/docs/twitter-api
..   :alt: Twitter API v2

Python client for the Twitter API v2 recent search endpoint
===========================================================

Welcome to the ``v2`` branch of the Python search client. This branch was born from the main branch that supports
premium and enterprise tiers of Twitter search. This branch supports the `Twitter API v2 recent search endpoint <https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction>`__ only, and drops support for the premium and enterprise tiers.

This project serves as a wrapper for the Twitter API v2 recent search endpoint, providing a command-line utility and a Python library.

To download and install this package, go to: https://pypi.org/project/searchtweets-v2/

If you are looking for the original version that works with premium and enterprise versions of search, head on over to
the main or ``enterprise-premium`` branch. (Soon, the v2 version will be promoted to the main branch.)


Features
========

- Supports Twitter API v2 recent search.
- Supports the configuration of v2 `expansions <https://developer.twitter.com/en/docs/twitter-api/expansions>`_ and `fields <https://developer.twitter.com/en/docs/twitter-api/fields>`_.
- Supports a new "polling" mode using the ``since-id`` search request parameter. The ``since-id``, along with the new ``until-id`` provide a way to navigate the public Tweet archive by Tweet ID.
- Supports additional ways to specify ``start-time`` and ``end-time`` request parameters:

  - d# - For example, 'd2' sets ``start-time`` to (exactly) two days ago.
  - h# - For example, 'h12' sets ``start-time`` to (exactly) twelve hours ago.
  - m# - For example, 'm15' sets ``start-time`` to (exactly) fifteen minutes ago.

  These are handy for kicking off searches with a backfill period, and also work with the ``end-time`` request parameter.

These features were inherited from the enterprise/premium version:

-  Command-line utility is pipeable to other tools (e.g., ``jq``).
-  Automatically handles pagination of search results with specifiable limits.
-  Delivers a stream of data to the user for low in-memory requirements.
-  Handles OAuth 2 and Bearer Token authentication.
-  Flexible usage within a python program.


Twitter API v2 recent search updates
====================================

Twitter API v2 represents an opportunity to apply previous learnings from building Twitter API v1.1. and the premium and enterprise tiers of endpoints, and redesign and rebuild from the ground up. While building this v2 version of the `search-tweets-python` library,
we took the opportunity to update fundamental things. This library provides example scripts, and one example is updating their command-line arguments to better match new v2 conventions. Instead of setting search periods with `start-datetime` and `end-datetime`,
they have been shortened to match current search request parameters: `start-time` and `end-time`. Throughout the code, we no longer use parlance that references `rules` and `PowerTrack`, and now reference `queries` and the v2 recent search endpoint.

When migrating this Python search client to v2 from the enterprise and premium tiers, the following updates were made:

- Added support for GET requests (and removed POST support for now).
- Added support for ``since_id`` and ``until_id`` request parameters.
- Updated pagination details.
- Updated app command-line parlance:
      -  --start-datetime → --start-time
      -  --end-datetime → --end-time
      -  --filter-rule → --query
      -  --max-results → --max-tweets
      - Dropped --account-type. No longer required since support for Premium and Enterprise search tiers have been dropped.
      - Dropped --count-bucket. Removed search 'counts' endpoint support. This endpoint is currently not available in v2.

In this spirit of updating the parlance used, note that a core method provided by searchtweets/result_stream.py has been renamed. The method `gen_rule_payload` has been updated to `gen_request_parameters`. 

**One key update is handling the changes in how the search endpoint returns its data.** The v2 search endpoint returns matching Tweets in a `data` array, along with an `includes` array that provides supporting objects that result from specifying `expansions`.
These expanded objects include Users, referenced Tweets, and attached media.  In addition to the `data` and `includes` arrays, the search endpoint also provides a `meta` object that provides the max and min Tweet IDs included in the response,
along with a `next_token` if there is another 'page' of data to request.

Currently, the v2 client returns the Tweets in the `data` array as individual (and atomic) JSON Tweet objects. This matches the behavior of the original search client. However, after yielding the individual Tweet objects, the client outputs arrays of User, Tweet, and media objects from the `includes` array, followed by the `meta` object.

Finally, the original version of search-tweets-python used a `Tweet Parser <https://twitterdev.github.io/tweet_parser/>`__ to help manage the differences between two different JSON formats ("original" and "Activity Stream"). With v2, there is just one version of Tweet JSON, so this Tweet Parser is not used.
In the original code, this Tweet parser was envoked with a `tweetify=True directive. With this v2 version, this use of the Tweet Parser is turned off by instead using `tweetify=False`.


Command-line options
====================

.. code:: bash

  usage: search_tweets.py [-h] [--credential-file CREDENTIAL_FILE]
   [--credential-file-key CREDENTIAL_YAML_KEY]
   [--env-overwrite ENV_OVERWRITE]
   [--config-file CONFIG_FILENAME]
   [--query QUERY]
   [--start-time START_TIME]
   [--end-time END_TIME]
   [--since-id SINCE_ID]
   [--until-id UNTIL_ID]
   [--results-per-call RESULTS_PER_CALL]
   [--expansions EXPANSIONS]
   [--tweet-fields TWEET_FIELDS]
   [--user-fields USER_FIELDS]
   [--media-fields MEDIA_FIELDS]
   [--place-fields PLACE_FIELDS]
   [--poll-fields POLL_FIELDS]
   [--max-tweets MAX_TWEETS]
   [--max-pages MAX_PAGES]
   [--results-per-file RESULTS_PER_FILE]
   [--filename-prefix FILENAME_PREFIX]
   [--no-print-stream]
   [--print-stream]
   [--extra-headers EXTRA_HEADERS]
   [--debug]

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
   --query QUERY         Search query. (See:
                        https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-rule)
   --start-time START_TIME
                        Start of datetime window, format 'YYYY-mm-DDTHH:MM'
                        (default: -7 days)
   --end-time END_TIME   End of datetime window, format 'YYYY-mm-DDTHH:MM'
                        (default: most recent date)
   --since-id SINCE_ID   Tweet ID, will start search from Tweets after this
                        one. (See:
                        https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate)
   --until-id UNTIL_ID   Tweet ID, will end search from Tweets before this one.
                        (See:
                        https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate)
   --results-per-call RESULTS_PER_CALL
                        Number of results to return per call (default 10; max
                        100) - corresponds to 'max_results' in the API
   --expansions EXPANSIONS
                        A comma-delimited list of object expansions to include
                        in endpoint responses. (API default: "")
   --tweet-fields TWEET_FIELDS
                        A comma-delimited list of Tweet JSON attributions to
                        include in endpoint responses. (API default: "id, text")
   --user-fields USER_FIELDS
                        A comma-delimited list of user JSON attributions to
                        include in endpoint responses. (API default: "id")
   --media-fields MEDIA_FIELDS
                        A comma-delimited list of media JSON attributions to
                        include in endpoint responses. (API default: "id")
   --place-fields PLACE_FIELDS
                        A comma-delimited list of Twitter Place JSON
                        attributions to include in endpoint responses. (API
                        default: "id")
   --poll-fields POLL_FIELDS
                        A comma-delimited list of Tweet Poll JSON attributions
                        to include in endpoint responses. (API default: "id")
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
                        HTTP request headers
   --debug               print all info and warning messages


Installation
=============

The updated Pypi install package for the v2 version is at:

https://pypi.org/project/searchtweets-v2/

Another option to work directly with this code by cloning the repository, installing the required Python packages, setting up your credentials, and start making requests.

To confirm the your code is ready to go, run the ``$python3 scripts/search-tweets.py -h`` command. You should see the help details shown above.

Credential Handling
===================

The Twitter API v2 recent search endpoint uses app-only authentication. You have the choice to configure your application consumer key and secret, or a Bearer Token you have generated. If you supply the application key and secret, the client will generate a Bearer Token for you.

Many developers might find providing your application key and secret more straightforward and letting this library manage your Bearer Token generation for you. Please see `HERE <https://developer.twitter.com/en/docs/basics/authentication/oauth-2-0>`_ for an overview of the app-only authentication method.

We support both YAML-file based methods and environment variables for storing credentials, and provide flexible handling with sensible defaults.

YAML method
===========

The simplest credential file should look like this:

.. code:: yaml

  search_tweets_api:
    endpoint:  https://api.twitter.com/2/tweets/search/recent
    consumer_key: <CONSUMER_KEY>
    consumer_secret: <CONSUMER_SECRET>
    bearer_token: <BEARER_TOKEN>

By default, this library expects this file at "~/.twitter_keys.yaml", but you can pass the relevant location as needed, either with the --credential-file flag for the command-line app or as demonstrated below in a Python program.

Both above examples require no special command-line arguments or in-program arguments. The credential parsing methods, unless otherwise specified, will look for a YAML key called search_tweets_api.

For developers who have multiple endpoints and/or search products, you can keep all credentials in the same file and specify specific keys to use. --credential-file-key specifies this behavior in the command line app. An example:

.. code:: yaml

  search_tweets_v2:
    endpoint: https://api.twitter.com/2/tweets/search/recent
    consumer_key: <KEY>
    consumer_secret: <SECRET>
    (optional) bearer_token: <TOKEN>

  search_tweets_labsv2:
    endpoint: https://api.twitter.com/labs/2/tweets/search
    consumer_key: <KEY>
    consumer_secret: <SECRET>
    (optional) bearer_token: <TOKEN>

Environment Variables
=====================

If you want or need to pass credentials via environment variables, you can set the appropriate variables:

::

  export SEARCHTWEETS_ENDPOINT=
  export SEARCHTWEETS_BEARER_TOKEN=
  export SEARCHTWEETS_CONSUMER_KEY=
  export SEARCHTWEETS_CONSUMER_SECRET=

The ``load_credentials`` function will attempt to find these variables if it cannot load fields from the YAML file, and it will **overwrite any credentials from the YAML file that are present as environment variables** if they have been parsed. This behavior can be changed by setting the ``load_credentials`` parameter ``env_overwrite`` to ``False``.

The following cells demonstrates credential handling in the Python library.

.. code:: python

  from searchtweets import load_credentials

.. code:: python

  load_credentials(filename="./search_tweets_creds_example.yaml",
                   yaml_key="search_tweets_v2_example",
                   env_overwrite=False)

::

  {'bearer_token': '<A_VERY_LONG_MAGIC_STRING>',
   'endpoint': 'https://api.twitter.com/2/tweets/search/recent',
   'extra_headers_dict': None}

Environment Variable Overrides
------------------------------

If we set our environment variables, the program will look for them
regardless of a YAML file's validity or existence.

.. code:: python

   import os
   os.environ["SEARCHTWEETS_BEARER_TOKEN"] = "<ENV_BEARER_TOKEN>"
   os.environ["SEARCHTWEETS_ENDPOINT"] = "<https://endpoint>"

   load_credentials(filename="nothing_here.yaml", yaml_key="no_key_here")

::

   cannot read file nothing_here.yaml
   Error parsing YAML file; searching for valid environment variables

::

   {'bearer_token': '<ENV_BEARER_TOKEN>',
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

The library includes an application, ``search_tweets.py``, that provides rapid access to Tweets. When you use ``pip`` to install this package, ``search_tweets.py`` is installed globally. The file is located in the ``scripts/`` directory for those who want to run it locally.

Note that the ``--results-per-call`` flag specifies an argument to the API, not as a hard max to number of results returned from this program. The argument ``--max-tweets`` defines the maximum number of results to return from a single run of the ``search-tweets.py``` script. All examples assume that your credentials are set up correctly in the default location - ``.twitter_keys.yaml`` or in environment variables.

**Stream json results to stdout without saving**

.. code:: bash

  search_tweets.py \
    --max-tweets 10000 \
    --results-per-call 100 \
    --query "(snow OR rain) has:media -is:retweet" \
    --print-stream

**Stream json results to stdout and save to a file**

.. code:: bash

  search_tweets.py \
    --max-tweets 10000 \
    --results-per-call 100 \
    --query "(snow OR rain) has:media -is:retweet" \
    --filename-prefix weather_pics \
    --print-stream

**Save to file without output**

.. code:: bash

  search_tweets.py \
    --max-tweets 10000 \
    --results-per-call 100 \
    --query "(snow OR rain) has:media -is:retweet" \
    --filename-prefix weather_pics \
    --no-print-stream

One or more custom headers can be specified from the command line, using the ``--extra-headers`` argument and a JSON-formatted string representing a dictionary of extra headers:

.. code:: bash

  search_tweets.py \
    --query "(snow OR rain) has:media -is:retweet" \
    --extra-headers '{"<MY_HEADER_KEY>":"<MY_HEADER_VALUE>"}'

Options can be passed via a configuration file (either ini or YAML). Example files can be found in the ``config/api_config_example.config`` or ``config/api_yaml_example.yaml`` files, which might look like this:

.. code:: bash

  [search_rules]
  start_time = 2020-05-01
  end_time = 2020-05-01
  query = (snow OR rain) has:media -is:retweet

  [search_params]
  results_per_call = 100
  max_tweets = 10000

  [output_params]
  save_file = True
  filename_prefix = weather_pics
  results_per_file = 10000000

Or this:

.. code:: bash

  search_rules:
      start_time: 2020-05-01
      end_time: 2020-05-01 01:01
      query: (snow OR rain) has:media -is:retweet

  search_params:
      results_per_call: 100
      max_results: 500

  output_params:
      save_file: True
      filename_prefix: (snow OR rain) has:media -is:retweet
      results_per_file: 10000000

Custom headers can be specified in a config file, under a specific credentials key:

.. code:: yaml

  search_tweets_api:
    endpoint: <FULL_URL_OF_ENDPOINT>
    bearer_token: <AAAAAloooooogString>
    extra_headers:
      <MY_HEADER_KEY>: <MY_HEADER_VALUE>

When using a config file in conjunction with the command-line utility, you need to specify your config file via the ``--config-file`` parameter. Additional command-line arguments will either be added to the config file args or overwrite the config file args if both are specified and present.

Example:

::

  search_tweets.py \
    --config-file myapiconfig.config \
    --no-print-stream

------------------

Using the Twitter Search APIs' Python Wrapper
=============================================

Working with the API within a Python program is straightforward.

We'll assume that credentials are in the default location,
``~/.twitter_keys.yaml``.

.. code:: python

   from searchtweets import ResultStream, gen_request_parameters, load_credentials


Twitter API v2 Setup
--------------------

.. code:: python

   search_args = load_credentials("~/.twitter_keys.yaml",
                                          yaml_key="search_tweets_v2",
                                          env_overwrite=False)
                                          

There is a function that formats search API rules into valid json queries called ``gen_request_parameters``. It has sensible defaults, such as pulling more Tweets per call than the default 10, and not including dates. Discussing the finer points of
generating search rules is out of scope for these examples; we encourage you to see the docs to learn the nuances within, but for now let's see what a query looks like.

.. code:: python

   rule = gen_request_parameters("snow", results_per_call=100) 
   print(rule)

::

   {"query":"snow","max_results":100}

This rule will match tweets that have the text ``snow`` in them.

From this point, there are two ways to interact with the API. There is a quick method to collect smaller amounts of Tweets to memory that requires less thought and knowledge, and interaction with the ``ResultStream`` object which will be introduced later.

Fast Way
--------

We'll use the ``search_args`` variable to power the configuration point for the API. The object also takes a valid search query and has options to cutoff search when hitting limits on both number of Tweets and endpoint calls.

We'll be using the ``collect_results`` function, which has three parameters.

-  query: a valid search query, referenced earlier
-  max_results: as the API handles pagination, it will stop collecting
   when we get to this number
-  result_stream_args: configuration args that we've already specified.

Let's see how it goes:

.. code:: python

   from searchtweets import collect_results

.. code:: python

   tweets = collect_results(query,
                            max_tweets=100,
                            result_stream_args=search_args) # change this if you need to

An overwhelming number of Tweet attributes are made available directly, as such:

.. code:: python

   [print(tweet.text, end='\n\n') for tweet in tweets[0:10]];

::

   @CleoLoughlin Rain after the snow? Do you have ice now?

   @koofltxr Rain, 134340, still with you, winter bear, Seoul, crystal snow, sea, outro:blueside

   @TheWxMeister Sorry it ruined your camping. I was covering plants in case we got snow in the Mountain Shadows area. Thankfully we didn\u2019t. At least it didn\u2019t stick to the ground. The wind was crazy! Got just over an inch of rain. Looking forward to better weather.

   @brettlorenzen And, the reliability of \u201cNeither snow nor rain nor heat nor gloom of night stays these couriers (the #USPS) from the swift completion of their appointed rounds.\u201d
   
   Because black people get killed in the rain, black lives matter in the rain. It matters all the time. Snow, rain, sleet, sunny days. We're not out here because it's sunny. We're not out here for fun. We're out here because black lives matter. 
   
   Some of the master copies of the film \u201cGone With the Wind\u201d are archived at the @librarycongress near \u201cSnow White and the Seven Dwarfs\u201d and \u201cSingin\u2019 in the Rain.\u201d GWTW isn\u2019t going to vanish off the face of the earth.
   
   Snow Man\u306eD.D.\u3068\nSixTONES\u306eImitation Rain\n\u6d41\u308c\u305f\u301c
   
   @Nonvieta Yup I work in the sanitation industry. I'm in the office however. Life would not go on without our garbage men and women out there. All day everyday rain snow or shine they out there.
   
   This picture of a rainbow in WA proves nothing. How do we know if this rainbow was not on Mars or the ISS? Maybe it was drawn in on the picture. WA has mail-in voting so we do have to worry aboug rain, snow, poll workers not showing up or voting machines broke on election day !! https://t.co/5WdHx0acS0 https://t.co/BEKtTpBW9g
   
   Weather in Oslo at 06:00: Clear Temp: 10.6\u00b0C Min today: 9.1\u00b0C Rain today:0.0mm Snow now: 0.0cm Wind N Conditions: Clear Daylight:18:39 hours Sunset: 22:36

Voila, we have some Tweets. For interactive environments and other cases where you don't care about collecting your data in a single load or don't need to operate on the stream of Tweets directly, I recommend using this convenience function.

Working with the ResultStream
-----------------------------

The ResultStream object will be powered by the ``search_args``, and takes the query and other configuration parameters, including a hard stop on number of pages to limit your API call usage.

.. code:: python

   rs = ResultStream(query=query,
                     max_results=500,
                     max_pages=1,
                     **search_args)

   print(rs)
   
 ::
 
    ResultStream: 
   	{
       "endpoint":"https:\/\/api.twitter.com\/2\/tweets\/search\/recent",
       "request_parameters":{
           "query":"snow",
           "max_results":100
       },
       "tweetify":false,
       "max_results":1000
   }
   
There is a function, ``.stream``, that seamlessly handles requests and pagination for a given query. It returns a generator, and to grab our 1000 Tweets that mention ``snow`` we can do this:

.. code:: python

   tweets = list(rs.stream())

.. code:: python

   # using unidecode to prevent emoji/accents printing 
   [print(tweet) for tweet in tweets[0:10]];

::

{"id": "1270572563505254404", "text": "@CleoLoughlin Rain after the snow? Do you have ice now?"}
{"id": "1270570767038599168", "text": "@koofltxr Rain, 134340, still with you, winter bear, Seoul, crystal snow, sea, outro:blueside"}
{"id": "1270570621282340864", "text": "@TheWxMeister Sorry it ruined your camping. I was covering plants in case we got snow in the Mountain Shadows area. Thankfully we didn\u2019t. At least it didn\u2019t stick to the ground. The wind was crazy! Got just over an inch of rain. Looking forward to better weather."}
{"id": "1270569070287630337", "text": "@brettlorenzen And, the reliability of \u201cNeither snow nor rain nor heat nor gloom of night stays these couriers (the #USPS) from the swift completion of their appointed rounds.\u201d"}
{"id": "1270568690447257601", "text": "\"Because black people get killed in the rain, black lives matter in the rain. It matters all the time. Snow, rain, sleet, sunny days. We're not out here because it's sunny. We're not out here for fun. We're out here because black lives matter.\" @wisn12news https://t.co/3kZZ7q2MR9"}
{"id": "1270568607605575680", "text": "Some of the master copies of the film \u201cGone With the Wind\u201d are archived at the @librarycongress near \u201cSnow White and the Seven Dwarfs\u201d and \u201cSingin\u2019 in the Rain.\u201d GWTW isn\u2019t going to vanish off the face of the earth."}
{"id": "1270568437916426240", "text": "Snow Man\u306eD.D.\u3068\nSixTONES\u306eImitation Rain\n\u6d41\u308c\u305f\u301c"}
{"id": "1270568195519373313", "text": "@Nonvieta Yup I work in the sanitation industry. I'm in the office however. Life would not go on without our garbage men and women out there. All day everyday rain snow or shine they out there."}
{"id": "1270567737283117058", "text": "This picture of a rainbow in WA proves nothing. How do we know if this rainbow was not on Mars or the ISS? Maybe it was drawn in on the picture. WA has mail-in voting so we do have to worry aboug rain, snow, poll workers not showing up or voting machines broke on election day !! https://t.co/5WdHx0acS0 https://t.co/BEKtTpBW9g"}
{"id": "1270566386524356608", "text": "Weather in Oslo at 06:00: Clear Temp: 10.6\u00b0C Min today: 9.1\u00b0C Rain today:0.0mm Snow now: 0.0cm Wind N Conditions: Clear Daylight:18:39 hours Sunset: 22:36"}

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
