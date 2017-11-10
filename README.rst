Python Twitter Search API
=========================

This library serves as a python interface to the `Twitter premium and enterprise search APIs <https://developer.twitter.com/en/docs/tweets/search/overview/30-day-search>`_. It provides a command-line utility and a library usable from within python. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.

Pretty docs can be seen `here <https://tw-ddis.github.io/twitter_search_api/index.html>`_.


Features
========

- Command-line utility is pipeable to other tools (e.g., ``jq``).
- Delivers a stream of data to the user for low in-memory requirements
- Automatically handles pagination of results with specifiable limits
- Handles Enterprise and Premium authentication methods
- Flexible usage within a python program
- Compatible with our group's Tweet Parser for rapid extraction of relevant data fields from each tweet payload
- Supports the Counts API, which can reduce API call usage and provide rapid insights if you only need volumes and not tweet payloads



Installation
============

We will soon handle releases via PyPy, but you can also install the current master version via

.. code:: bash

  pip install git+https://github.com/tw-ddis/twitter_search_api.git

Or the development version locally via

.. code:: bash

  git clone https://github.com/tw-ddis/twitter_search_api.git
  cd twitter_search_api
  pip install -e .



Using the Comand Line Application
=================================

We provide a utility, ``twitter_search.py``, in the ``tools`` directory that provides rapid access to tweets.
Premium customers should use ``--bearer-token`` instead of ``--user-name`` and ``--password``.

**Stream json results to stdout without saving**

.. code:: bash

  python twitter_search.py \
    --user-name <USERNAME> \
    --password <PW> \
    --endpoint <MY_ENDPOINT> \
    --max-tweets 1000 \
    --filter-rule "beyonce has:geo" \
    --print-stream


**Stream json results to stdout and save to a file**

.. code:: bash

  python twitter_search.py \
    --user-name <USERNAME> \
    --password <PW> \
    --endpoint <MY_ENDPOINT> \
    --max-tweets 1000 \
    --filter-rule "beyonce has:geo" \
    --filename-prefix beyonce_geo \
    --print-stream


**Save to file without output**

.. code:: bash

  python twitter_search.py \
    --user-name <USERNAME> \
    --password <PW> \
    --endpoint <MY_ENDPOINT> \
    --max-tweets 100 \
    --filter-rule "beyonce has:geo" \
    --filename-prefix beyonce_geo \
    --no-print-stream



It can be far easier to specify your information in a configuration file. An example file can be found in the ``tools/api_config_example.config`` file, but will look something like this:

.. code:: bash

  [credentials]
  account_name = <account_name>
  username =  <user_name>
  password = <password>
  bearer_token = <token>

  [api_info]
  endpoint = <endpoint>

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


Using the Twitter Search API within Python
==========================================

Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

Our group's python `tweet parser
library <https://github.com/tw-ddis/tweet_parser>`__ is a requirement.

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
    from twittersearch import ResultStream, gen_rule_payload

Enterprise setup
----------------

If you are an enterprise customer, you'll need to authenticate with a
basic username/password method. You can specify that here:

.. code:: python

    # set your environment variables here for enterprise access if you need to
    # os.environ["TWITTER_SEARCH_ACCOUNT_NAME"] = ""
    # os.environ["TWITTER_SEARCH_PW"] = ""
    
    enterprise_endpoint = "<ENTER YOUR ENDPOINT HERE>"
    enterprise_search_args = {"username": "agonzales@twitter.com",
                              "password": os.environ["TWITTER_SEARCH_PW"],
                              "endpoint": enterprise_endpoint
                             }

Premium Setup
-------------

Premium customers will use a bearer token for authentication. Use the
following cell for setup:

.. code:: python

    # set your environment variables here for premium access if you need to
    # os.environ["TWITTER_SEARCH_BEARER_TOKEN"] = ""
    
    premium_search_endpoint = "https://api.twitter.com/1.1/tweets/search/30day/dev.json"
    
    premium_search_args = {"bearer_token": os.environ["TWITTER_SEARCH_BEARER_TOKEN"],
                           "endpoint": premium_search_endpoint,
                          }
    
    print(premium_search_endpoint)


.. parsed-literal::

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


.. parsed-literal::

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


.. parsed-literal::

    using bearer token for authentication


By default, tweet payloads are lazily parsed into a ``Tweet`` object. An
overwhelming number of tweet attributes are made available directly, as
such:

.. code:: python

    [(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]




.. parsed-literal::

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

    print(rs)


.. parsed-literal::

    ResultStream: 
    	{
        "username":null,
        "endpoint":"https:\/\/api.twitter.com\/1.1\/tweets\/search\/30day\/dev.json",
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


.. parsed-literal::

    using bearer token for authentication


Tweets are lazily parsed using our Tweet Parser, so tweet data is very
easily extractable.

.. code:: python

    [(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]




.. parsed-literal::

    [('920754829873606657', "@ericmbudd I'm super cute.", []),
     ('920754352716783616', "@RobotPrincessFi that's super cute", []),
     ('920543141614067712', '@RobotPrincessFi https://t.co/z6AioxZkwE', []),
     ('920383435209891841', '@robotprincessfi hi there Fiona', [])]



Counts API
----------

We can also use the counts api to get counts of tweets that match our
rule. Each request will return up to *30* results, and each count
request can be done on a minutely, hourly, or daily basis. There is a
utility function that will convert your regular endpoint to the count
endpoint.

The process is very similar to grabbing tweets, but has some minor
differneces.

**Caveat - premium sandbox environments do NOT have access to the counts
API.**

.. code:: python

    from twittersearch import change_to_count_endpoint
    count_endpoint = change_to_count_endpoint("https://gnip-api.twitter.com/search/fullarchive/accounts/shendrickson/ogformat.json")
    
    count_args = {"username": "agonzales@twitter.com",
                              "password": os.environ["TWITTER_SEARCH_PW"],
                              "endpoint": count_endpoint,
                             }
    
    count_rule = gen_rule_payload("beyonce", count_bucket="day")
    
    counts = collect_results(count_rule, result_stream_args=count_args)


.. parsed-literal::

    using username and password for authentication


Our results are pretty straightforward and can be rapidly used.

.. code:: python

    counts


.. parsed-literal::

    [{'count': 135320, 'timePeriod': '201711100000'},
     {'count': 68532, 'timePeriod': '201711090000'},
     {'count': 67138, 'timePeriod': '201711080000'},
     {'count': 73017, 'timePeriod': '201711070000'},
     {'count': 52290, 'timePeriod': '201711060000'},
     {'count': 79338, 'timePeriod': '201711050000'},
     {'count': 200519, 'timePeriod': '201711040000'},
     {'count': 160512, 'timePeriod': '201711030000'},
     {'count': 220683, 'timePeriod': '201711020000'},
     {'count': 190959, 'timePeriod': '201711010000'},
     {'count': 121580, 'timePeriod': '201710310000'},
     {'count': 39473, 'timePeriod': '201710300000'},
     {'count': 35441, 'timePeriod': '201710290000'},
     {'count': 36198, 'timePeriod': '201710280000'},
     {'count': 36149, 'timePeriod': '201710270000'},
     {'count': 34197, 'timePeriod': '201710260000'},
     {'count': 41497, 'timePeriod': '201710250000'},
     {'count': 47648, 'timePeriod': '201710240000'},
     {'count': 49087, 'timePeriod': '201710230000'},
     {'count': 44945, 'timePeriod': '201710220000'},
     {'count': 54865, 'timePeriod': '201710210000'},
     {'count': 74324, 'timePeriod': '201710200000'},
     {'count': 76643, 'timePeriod': '201710190000'},
     {'count': 115587, 'timePeriod': '201710180000'},
     {'count': 82581, 'timePeriod': '201710170000'},
     {'count': 72372, 'timePeriod': '201710160000'},
     {'count': 64522, 'timePeriod': '201710150000'},
     {'count': 56092, 'timePeriod': '201710140000'},
     {'count': 80265, 'timePeriod': '201710130000'},
     {'count': 137717, 'timePeriod': '201710120000'},
     {'count': 86203, 'timePeriod': '201710110000'}]



Dated searches / Full Archive Search
------------------------------------

Let's make a new rule and pass it dates this time.

``gen_rule_payload`` takes dates of the forms ``YYYY-mm-DD`` and
``YYYYmmDD``.

**Note that this will only work with the full archive search option**,
which is available to my account only via the enterprise options. Full
archive search will likely require a different endpoint or access
method; please see your developer console for details.

.. code:: python

    rule = gen_rule_payload("from:jack", from_date="2017-09-01", to_date="2017-10-30", max_results=100)
    print(rule)


.. parsed-literal::

    {"query":"from:jack","maxResults":100,"toDate":"201710300000","fromDate":"201709010000"}


.. code:: python

    tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)


.. parsed-literal::

    using username and password for authentication


.. code:: python

    [(str(tweet.created_at_datetime), tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]


.. parsed-literal::

    [('2017-10-27 18:22:07',
      'More clarity on our private information policy and enforcement. Working to build as much direct context into the product too https://t.co/IrwBexPrBA\nTo provide more clarity on our private information policy, we’ve added specific examples of what is/is not a violation and insight into what we need to remove this type of content from the service. https://t.co/NGx5hh2tTQ',
      []),
     ('2017-10-27 18:17:37',
      'Launching violent groups and hateful images/symbols policy on November 22nd https://t.co/NaWuBPxyO5\nWe will now launch our policies on violent groups and hateful imagery and hate symbols on Nov 22. During the development process, we received valuable feedback that we’re implementing before these are published and enforced. See more on our policy development process here 👇 https://t.co/wx3EeH39BI',
      []),
     ('2017-10-27 01:25:39', '@WillStick @lizkelley Happy birthday Liz!', []),
     ('2017-10-26 14:24:05',
      'Off-boarding advertising from all accounts owned by Russia Today (RT) and Sputnik.\n\nWe’re donating all projected earnings ($1.9mm) to support external research into the use of Twitter in elections, including use of malicious automation and misinformation. https://t.co/zIxfqqXCZr',
      []),
     ('2017-10-26 13:50:40', '@TMFJMo @anthonynoto Thank you', []),
     ('2017-10-26 13:36:19', '@gasca @stratechery @Lefsetz letter', []),
     ('2017-10-26 13:35:57',
      '@gasca @stratechery Bridgewater’s Daily Observations',
      []),
     ('2017-10-26 02:40:25',
      'Yup!!!! ❤️❤️❤️❤️ #davechappelle https://t.co/ybSGNrQpYF',
      ['davechappelle']),
     ('2017-10-26 00:07:23', '@ndimichino Sometimes', []),
     ('2017-10-25 20:15:19',
      'Setting up at @CampFlogGnaw https://t.co/nVq8QjkKsf',
      [])]
