
Using the Twitter Search API
============================

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

.. code:: ipython3

    import os
    import json
    from twittersearch import ResultStream, gen_rule_payload

Enterprise setup
----------------

If you are an enterprise customer, you'll need to authenticate with a
basic username/password method. You can specify that here:

.. code:: ipython3

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

.. code:: ipython3

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

.. code:: ipython3

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

.. code:: ipython3

    from twittersearch import collect_results

.. code:: ipython3

    tweets = collect_results(rule, max_results=500, result_stream_args=premium_search_args) # change this if you need to


.. parsed-literal::

    using bearer token for authentication


.. code:: ipython3

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

.. code:: ipython3

    rs = ResultStream(**premium_search_args, rule_payload=rule, max_results=500, max_pages=1, )

.. code:: ipython3

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

.. code:: ipython3

    tweets = list(rs.stream())


.. parsed-literal::

    using bearer token for authentication


Tweets are lazily parsed using our Tweet Parser, so tweet data is very
easily extractable.

.. code:: ipython3

    [(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]




.. parsed-literal::

    [('920754829873606657', "@ericmbudd I'm super cute.", []),
     ('920754352716783616', "@RobotPrincessFi that's super cute", []),
     ('920543141614067712', '@RobotPrincessFi https://t.co/z6AioxZkwE', []),
     ('920383435209891841', '@robotprincessfi hi there Fiona', [])]



Let's make a new rule and pass it dates this time. ``gen_rule_payload``
takes dates of the forms ``YYYY-mm-DD`` and ``YYYYmmDD``. Note that this
will only work with the full archive search option, which is available
to my account only via the enterprise options.

.. code:: ipython3

    rule = gen_rule_payload("from:jack", from_date="2017-09-01", to_date="2017-10-30", max_results=100)
    print(rule)


.. parsed-literal::

    {"query":"from:jack","maxResults":100,"toDate":"201710300000","fromDate":"201709010000"}


.. code:: ipython3

    tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)


.. parsed-literal::

    using username and password for authentication


.. code:: ipython3

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


