Python Twitter Search API
=========================


This library serves as a python interface to the Twitter/GNIP Search API. It allows use both from a command-line utility and from with a python program. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.

Pretty docs can be seen `here <https://tw-ddis.github.io/twitter_search_api/index.html>`_.


Features
========

- delivers a stream of data to the user for low in-memory requirements
- automatically handles pagination of results with specifiable limits
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
  output_file_prefix = beyonce


When using a config file in conjunction with the command-line utility, you need to specify your config file via the ``--config-file`` parameter. Additional command-line arguments will either be *added* to the config file args or **overwrite** the config file args if both are specified and present.

example::

  python twitter_search_api.py \
    --config-file myapiconfig.config \
    --no-print-stream


Using the Twitter Search API
============================

Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

Our group's python `tweet parser library <https://github.com/tw-ddis/tweet_parser>`__ is a requirement.

Prior to starting your program, an easy way to define your secrets will
be setting an environment variable. If you are an enterprise client,
your authentication will be a (username, password) pair. If you are a
premium client, you'll need to get a bearer token that will be passed
with each call for authentication.

::

    export TWITTER_SEARCH_PW=<password>
    export TWITTER_SEARCH_ACCOUNT_NAME=<account_name>
    export TWITTER_SEARCH_BEARER_TOKEN=<token>

The other points that you will have to set in the program are your
endpoint, the api you want to use. There are functions to generate
correct API endpoints from this info as well as flags to use the
``counts`` endpoint instead of the regular endpoint.

The following cell demonstrates the basic setup that will be referenced
throughout your program's session. Note that any method of storing your
credentials is valid here; I am using environment variables for ease of
use.

.. code:: python

    import os
    import json
    from twittersearch import ResultStream, gen_endpoint, gen_rule_payload

Enterprise setup
----------------

If you are an enterprise customer, you'll need to authenticate with a
basic username/password method. You can specify that here:

.. code:: python

    # set your environment variables here for enterprise access if you need to
    # os.environ["TWITTER_SEARCH_ACCOUNT_NAME"] = ""
    # os.environ["TWITTER_SEARCH_PW"] = ""


    enterprise_search_endpoint = gen_endpoint(kind="enterprise", 
                                              search_api="fullarchive",
                                              account_name=os.environ["TWITTER_SEARCH_ACCOUNT_NAME"],
                                              label="ogformat.json",
                                              count_endpoint=False)

    enterprise_search_args = {"username": "agonzales@twitter.com",
                              "password": os.environ["TWITTER_SEARCH_PW"],
                              "url": enterprise_search_endpoint,
                             }



    print(enterprise_search_endpoint.replace(os.environ["TWITTER_SEARCH_ACCOUNT_NAME"], '<account_name>'))

::

    https://gnip-api.twitter.com/search/fullarchive/accounts/<account_name>/ogformat.json

Premium Setup
-------------

Premium customers will use a bearer token for authentication. Use the
following cell for setup:

.. code:: python

    # set your environment variables here for premium access if you need to
    # os.environ["TWITTER_SEARCH_BEARER_TOKEN"] = ""


    premium_search_endpoint = gen_endpoint(kind="premium",
                                           search_api="30day",
                                           label="dev",
                                           count_endpoint=False)

    premium_search_args = {"bearer_token": os.environ["TWITTER_SEARCH_BEARER_TOKEN"],
                           "url": premium_search_endpoint,
                          }

    print(premium_search_endpoint)

::

    https://api.twitter.com/1.1/tweets/search/30day/dev.json

There is a function that formats search API rules into valid json
queries called ``gen_rule_payload``. It has sensible defaults, such as
pulling more tweets per call than the default 100 (but note that a
sandbox environment can only have a max of 100 here, so if you get
errors, please check this) not including dates, and defaulting to hourly
counts when using the counts api. Discussing the finer points of
generating search rules is out of scope for these examples; I encourage
you to see the docs to learn the nuances within, but for now let's see
what a rule looks like.

.. code:: python

    rule = gen_rule_payload("@robotprincessfi", max_results=100) # testing with a sandbox account
    print(rule)

::

    {"query":"@robotprincessfi","maxResults":100}

This rule will match tweets that mention ``@robotprincessfi``.

From this point, there are two ways to interact with the API. There is a
quick method to collect smaller amounts of tweets to memory that
requires less thought and knowledge, and interaction with the
``ResultStream`` object which will be introduced later.

Fast Way
--------

We'll use the ``search_args`` variable to power the configuration point
for the API. The object also takes a valid PowerTrack rule and has
options to cutoff search when hitting limits on both number of tweets
and API calls.

We'll be using the ``collect_results`` function, which has three
parameters.

-  rule: a valid powertrack rule, referenced earlier
-  max\_results: as the api handles pagination, it will stop collecting
   when we get to this number
-  result\_stream\_args: configuration args that we've already
   specified.

For the remaining examples, please change the args to either premium or
enterprise depending on your usage.

Let's see how it goes:

.. code:: python

    from twittersearch import collect_results

.. code:: python

    tweets = collect_results(rule, max_results=500, result_stream_args=premium_search_args) # change this if you need to

::

    using bearer token for authentication

.. code:: python

    [(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]

::

    [('920754829873606657', "@ericmbudd I'm super cute.", []),
     ('920754352716783616', "@RobotPrincessFi that's super cute", []),
     ('920543141614067712', '@RobotPrincessFi https://t.co/z6AioxZkwE', []),
     ('920383435209891841', '@robotprincessfi hi there Fiona', [])]

Voila, we have some tweets. For interactive environments and other cases
where you don't care about collecting your data in a single load or
don't need to operate on the stream of tweets or counts directly, I
recommend using this convenience function.

Working with the ResultStream
-----------------------------

The ResultStream object will be powered by the ``search_args``, and
takes the rules and other configuration parameters, including a hard
stop on number of pages to limit your API call usage.

.. code:: python

    rs = ResultStream(**premium_search_args, rule_payload=rule, max_results=500, max_pages=1, )

.. code:: python

    print(str(rs).replace(os.environ["TWITTER_SEARCH_ACCOUNT_NAME"], '<account_name>'))

::

    ResultStream: 
        {
        "username":null,
        "url":"https:\/\/api.twitter.com\/1.1\/tweets\/search\/30day\/dev.json",
        "rule_payload":{
            "query":"@robotprincessfi",
            "maxResults":100
        },
        "tweetify":true,
        "max_results":500
    }

There is a function, ``.stream``, that seamlessly handles requests and
pagination for a given query. It returns a generator, and to grab our
500 tweets that mention ``@robotprincessfi`` we can do this:

.. code:: python

    tweets = list(rs.stream())

::

    using bearer token for authentication

Tweets are lazily parsed using our Tweet Parser, so tweet data is very
easily extractable.

.. code:: python

    [(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]

::

    [('920754829873606657', "@ericmbudd I'm super cute.", []),
     ('920754352716783616', "@RobotPrincessFi that's super cute", []),
     ('920543141614067712', '@RobotPrincessFi https://t.co/z6AioxZkwE', []),
     ('920383435209891841', '@robotprincessfi hi there Fiona', [])]

Let's make a new rule and pass it dates this time. ``gen_rule_payload``
takes dates of the forms ``YYYY-mm-DD`` and ``YYYYmmDD``. Note that this
will only work with the full archive search option, which is available
to my account only via the enterprise options.

.. code:: python

    rule = gen_rule_payload("from:jack", from_date="2017-09-01", to_date="2017-10-15", max_results=100)
    print(rule)

::

    {"query":"from:jack","maxResults":100,"toDate":"201710150000","fromDate":"201709010000"}

.. code:: python

    tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

::

    using username and password for authentication

.. code:: python

    [(str(tweet.created_at_datetime), tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]
      

::

    [('2017-10-14 22:57:23',
      'I love to see Palestinians dancing and having fun. Good &amp;positive stories deserve to go viral as well. Watch this: https://t.co/42vOrC40Fu',
      []),
     ('2017-10-14 22:55:25',
      "But don't argue with people on twitter about whether policies and laws are racist. Argue with your City Council and your state reps and senators and Mayor and alderman. And if you don't like how that argument went\nfire em.",
      []),
     ('2017-10-14 21:30:26',
      'I saw @solangeknowles perform at Chinati last weekend. It was the most beautiful thing I’ve ever seen. Can’t stop thinking about it. https://t.co/1wNLiNCaxb',
      []),
     ('2017-10-14 19:17:33', '1', []),
     ('2017-10-14 17:30:01',
      '@monteiro @JohnPaczkowski @cwarzel Never asked for credit Mike',
      []),
     ('2017-10-14 17:26:00',
      '@cwarzel @JohnPaczkowski Will keep everyone updated on the original thread',
      []),
     ('2017-10-14 17:03:38',
      '@davewiner Listened to it all. Doesn’t mean we are going to implement everything! ;)',
      []),
     ('2017-10-14 17:00:56',
      '@davewiner @realDonaldTrump Also not true. It’s a moment in time',
      []),
     ('2017-10-14 17:00:20',
      '@davewiner Come on. This isn’t true. We care. We have to build a business to fund the service',
      []),
     ('2017-10-14 16:59:21',
      '@yaelwrites @JohnPaczkowski @cwarzel @jilliancyork Never said that. We are considering. Need to prioritize.',
      [])]
