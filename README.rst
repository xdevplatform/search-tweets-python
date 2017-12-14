Python Twitter Search API
=========================

This library serves as a python interface to the `Twitter premium and enterprise search APIs <https://developer.twitter.com/en/docs/tweets/search/overview/30-day-search>`_. It provides a command-line utility and a library usable from within python. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.

Pretty docs can be seen `here <https://twitterdev.github.io/twitter_search_api/>`_.


Features
========

- Command-line utility is pipeable to other tools (e.g., ``jq``).
- Automatically handles pagination of results with specifiable limits
- Delivers a stream of data to the user for low in-memory requirements
- Handles Enterprise and Premium authentication methods
- Flexible usage within a python program
- Compatible with our group's Tweet Parser for rapid extraction of relevant data fields from each tweet payload
- Supports the Counts API, which can reduce API call usage and provide rapid insights if you only need volumes and not tweet payloads



Installation
============

We will soon handle releases via PyPy, but you can also install the current master version via

.. code:: bash

  pip install git+https://github.com/twitterdev/twitter_search_api.git

Or the development version locally via

.. code:: bash

  git clone https://github.com/twitterdev/twitter_search_api.git
  cd twitter_search_api
  pip install -e .



Using the Comand Line Application
=================================

We provide a utility, ``twitter_search.py``, in the ``tools`` directory that provides rapid access to tweets.
Premium customers should use ``--bearer-token``; enterprise customers should use ``--user-name`` and ``--password``.

The ``--endpoint`` flag will specify the full URL of your connection, e.g.:


.. code:: bash

  https://api.twitter.com/1.1/tweets/search/30day/dev.json

You can find this url in your developer console.

Note that the ``--results-per-call`` flag specifies an argument to the API call ( ``maxResults``, results returned per CALL), not as a hard max to number of results returned from this program. use ``--max-results`` for that for now.



**Stream json results to stdout without saving**

.. code:: bash

  python twitter_search.py \
    --bearer-token <BEARER_TOKEN> \
    --endpoint <MY_ENDPOINT> \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --print-stream


**Stream json results to stdout and save to a file**

.. code:: bash

  python twitter_search.py \
    --user-name <USERNAME> \
    --password <PW> \
    --endpoint <MY_ENDPOINT> \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --filename-prefix beyonce_geo \
    --print-stream


**Save to file without output**

.. code:: bash

  python twitter_search.py \
    --user-name <USERNAME> \
    --password <PW> \
    --endpoint <MY_ENDPOINT> \
    --max-results 100 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
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
  results_per_call = 100
  pt_rule = beyonce has:hashtags


  [search_params]
  max_results = 500

  [output_params]
  output_file_prefix = beyonce

Soon, we will update this behavior and remove the credentials section from the config file to be handled differently.

When using a config file in conjunction with the command-line utility, you need to specify your config file via the ``--config-file`` parameter. Additional command-line arguments will either be *added* to the config file args or **overwrite** the config file args if both are specified and present.


Example::

  python twitter_search_api.py \
    --config-file myapiconfig.config \
    --no-print-stream


Using the Twitter Search API within Python
==========================================

Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

Our group's python `tweet parser
library <https://github.com/twitterdev/tweet_parser>`__ is a
requirement.

Prior to starting your program, an easy way to define your secrets will
be setting an environment variable. If you are an enterprise client,
your authentication will be a (username, password) pair. If you are a
premium client, you'll need to get a bearer token that will be passed
with each call for authentication.

We advocate putting your API info in a yaml file such as this:

.. code:: .yaml


    twitter_search_api:
      endpoint: <FULL_URL_OF_ENDPOINT>
      account: <ACCOUNT_NAME>
      username: <USERNAME>
      password: <PW>
      bearer_token: <TOKEN>

And filling in the keys that are appropriate for your account type.
Premium users should only have the ``endpoint`` and ``bearer_token``;
Enterprise customers should have ``account``, ``username``,
``endpoint``, and ``password``.

Our credential reader will default to expecing this file in
``"~/.twitter_search.yaml"``, but you can pass the relevant location as
needed.

The following cell demonstrates the basic setup that will be referenced
throughout your program's session.

.. code:: python

    import os
    import json
    from unidecode import unidecode
    
    from twittersearch import ResultStream, gen_rule_payload, load_credentials

Enterprise setup
----------------

If you are an enterprise customer, you'll need to authenticate with a
basic username/password method. You can specify that here:

.. code:: python

    from twittersearch import infer_endpoint

.. code:: python

    enterprise_search_args = load_credentials("~/.twitter_keys.yaml",
                                              account_type="enterprise")

Premium Setup
-------------

Premium customers will use a bearer token for authentication. Use the
following cell for setup:

.. code:: python

    premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                           account_type="premium")

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

    rule = gen_rule_payload("beyonce", results_per_call=100) # testing with a sandbox account
    print(rule)


.. parsed-literal::

    {"query":"beyonce","maxResults":100}


This rule will match tweets that have the text ``beyonce`` in them.

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

    tweets = collect_results(rule,
                             max_results=100,
                             result_stream_args=enterprise_search_args) # change this if you need to

By default, tweet payloads are lazily parsed into a ``Tweet`` object. An
overwhelming number of tweet attributes are made available directly, as
such:

.. code:: python

    [print(tweet.all_text) for tweet in tweets[0:10]];


.. parsed-literal::

    That deep sigh Beyoncé took once she realized she wouldn’t be able to get the earpiece out of her hair before the dance break 😂.  https://t.co/dU1K2KMT7i
    4 Years ago today, "BEYONCÉ" by Beyoncé was surprise released. It received acclaim from critics,  debuted at #1 and certified 2x Platinum in the US. https://t.co/wB3C7DuX9o
    me mata la gente que se cree superior por sus gustos de música escuches queen beyonce o el polaco no sos mas ni menos que nadie
    I’m literally not Beyoncé https://t.co/LwIkllCx6P
    #BEYONCÉ ‣ 𝐌𝐄𝐀𝐃𝐃𝐅𝐀𝐍 𝐎𝐅𝐈𝐂𝐈𝐀𝐋 - I Am... 𝐖𝐎𝐑𝐋𝐃 𝐓𝐎𝐔𝐑! https://t.co/TyyeDdXKiM
    Beyoncé on how nervous she was to release her self-titled... https://t.co/fru23c6DYC
    AAAA ansiosa por esse feat da Beyoncé com Jorge Ben Jor &lt;3 https://t.co/NkKJhC9JUd
    I am world tour, the Beyonce experience, revamped hmt. https://t.co/pb07eMyNka
    Tell me what studio versions of any artists would u like me to do? https://t.co/Z6YWsAJuhU
    Billboard's best female artists over the last decade:
    
    2017: Ariana Grande
    2016: Adele
    2015: Taylor Swift
    2014: Katy Perry
    2013: Taylor Swift
    2012: Adele
    2011: Adele
    2010: Lady Gaga
    2009: Taylor Swift
    2008: Rihanna
    
    Beyonce = 0
    
    Taylor Swift = 3 👑
    Beyoncé explaining her intent behind the BEYONCÉ visual album &amp; how she wanted to reinstate the idea of an album release as a significant, exciting event which had lost meaning in the face of hype created around singles. 👑 https://t.co/pK2MB35vYl


.. code:: python

    [print(tweet.created_at_datetime) for tweet in tweets[0:10]];


.. parsed-literal::

    2017-12-13 21:18:17
    2017-12-13 21:18:16
    2017-12-13 21:18:16
    2017-12-13 21:18:15
    2017-12-13 21:18:15
    2017-12-13 21:18:13
    2017-12-13 21:18:12
    2017-12-13 21:18:12
    2017-12-13 21:18:11
    2017-12-13 21:18:10


.. code:: python

    [print(tweet.generator.get("name")) for tweet in tweets[0:10]];


.. parsed-literal::

    Twitter for Android
    Twitter for Android
    Twitter for Android
    Twitter for iPhone
    Meadd
    Twitter for iPhone
    Twitter for Android
    Twitter for iPhone
    Twitter for iPhone
    Twitter for Android


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

    rs = ResultStream(rule_payload=rule,
                      max_results=500,
                      max_pages=1,
                      **premium_search_args)
    
    print(rs)


.. parsed-literal::

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
500 tweets that mention ``beyonce`` we can do this:

.. code:: python

    tweets = list(rs.stream())

Tweets are lazily parsed using our Tweet Parser, so tweet data is very
easily extractable.

.. code:: python

    # using unidecode to prevent emoji/accents printing 
    [print(tweet.all_text) for tweet in tweets[0:10]];


.. parsed-literal::

    Everyone: *still dragging Jay for cheating*
    
    Beyoncé: https://t.co/2z1ltlMQiJ
    Beyoncé changed the game w/ that digital drop 4 years ago today! 🎉
    
    • #1 debut on Billboard
    • Sold 617K in the US / over 828K WW in only 3 days
    • Fastest-selling album on iTunes of all time
    • Reached #1 in 118 countries
    • Widespread acclaim; hailed as her magnum opus https://t.co/lDCdVs6em3
    Beyoncé 🔥 #444Tour https://t.co/sCvZzjLwqx
    Se presentan casos de feminismo pop basado en sugerencias de artistas famosos en turno, Emma Watson, Beyoncé.
    Beyonce. Are you kidding me with this?! #Supreme #love #everything
    Dear Beyoncé, https://t.co/5visfVK2LR
    At this time 4 years ago today, Beyoncé released her self-titled album BEYONCÉ exclusively on the iTunes Store without any prior announcement. The album remains the ONLY album in history to reach #1 in 118 countries &amp; the fastest-selling album in the history of the iTunes Store. https://t.co/ZZb4QyQYf0
    4 years ago today, Beyoncé released her self-titled visual album "BEYONCÉ" and shook up the music world forever. 🙌🏿 https://t.co/aGtUSq9R3u
    Everyone: *still dragging Jay for cheating*
    
    Beyoncé: https://t.co/2z1ltlMQiJ
    And Beyonce hasn't had a solo #1 hit since the Bush administration soooo... https://t.co/WCd7ni8DwN


Counts API
----------

We can also use the counts api to get counts of tweets that match our
rule. Each request will return up to *30* results, and each count
request can be done on a minutely, hourly, or daily basis. The
underlying ``ResultStream`` object will handle converting your endpoint
to the count endpoint, and you have to specify the ``count_bucket``
argument when making a rule to use it.

The process is very similar to grabbing tweets, but has some minor
differneces.

**Caveat - premium sandbox environments do NOT have access to the counts
API.**

.. code:: python

    count_rule = gen_rule_payload("beyonce", count_bucket="day")
    
    counts = collect_results(count_rule, result_stream_args=enterprise_search_args)

Our results are pretty straightforward and can be rapidly used.

.. code:: python

    counts




.. parsed-literal::

    [{'count': 85660, 'timePeriod': '201712130000'},
     {'count': 95231, 'timePeriod': '201712120000'},
     {'count': 114540, 'timePeriod': '201712110000'},
     {'count': 165964, 'timePeriod': '201712100000'},
     {'count': 102022, 'timePeriod': '201712090000'},
     {'count': 87630, 'timePeriod': '201712080000'},
     {'count': 195794, 'timePeriod': '201712070000'},
     {'count': 209629, 'timePeriod': '201712060000'},
     {'count': 88742, 'timePeriod': '201712050000'},
     {'count': 96795, 'timePeriod': '201712040000'},
     {'count': 177595, 'timePeriod': '201712030000'},
     {'count': 120102, 'timePeriod': '201712020000'},
     {'count': 186759, 'timePeriod': '201712010000'},
     {'count': 151212, 'timePeriod': '201711300000'},
     {'count': 79311, 'timePeriod': '201711290000'},
     {'count': 107175, 'timePeriod': '201711280000'},
     {'count': 58192, 'timePeriod': '201711270000'},
     {'count': 48327, 'timePeriod': '201711260000'},
     {'count': 59639, 'timePeriod': '201711250000'},
     {'count': 85201, 'timePeriod': '201711240000'},
     {'count': 91544, 'timePeriod': '201711230000'},
     {'count': 64129, 'timePeriod': '201711220000'},
     {'count': 92065, 'timePeriod': '201711210000'},
     {'count': 101617, 'timePeriod': '201711200000'},
     {'count': 84733, 'timePeriod': '201711190000'},
     {'count': 74887, 'timePeriod': '201711180000'},
     {'count': 76091, 'timePeriod': '201711170000'},
     {'count': 81849, 'timePeriod': '201711160000'},
     {'count': 58423, 'timePeriod': '201711150000'},
     {'count': 78004, 'timePeriod': '201711140000'},
     {'count': 118077, 'timePeriod': '201711130000'}]



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

    rule = gen_rule_payload("from:jack", from_date="2017-09-01", to_date="2017-10-30", results_per_call=500)
    print(rule)


.. parsed-literal::

    {"query":"from:jack","maxResults":500,"toDate":"201710300000","fromDate":"201709010000"}


.. code:: python

    tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: python

    # usiing unidecode only to 
    [print(tweet.all_text) for tweet in tweets[0:10]];


.. parsed-literal::

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

    premium_search_args.keys()




.. parsed-literal::

    dict_keys(['bearer_token', 'endpoint'])



.. code:: python

    rule = gen_rule_payload("from:jack",
                            from_date="2017-09-20",
                            to_date="2017-10-30",
                            count_bucket="day",
                            results_per_call=500)
    print(rule)


.. parsed-literal::

    {"query":"from:jack","toDate":"201710300000","fromDate":"201709200000","bucket":"day"}


.. code:: python

    counts = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: python

    [print(c) for c in counts];


.. parsed-literal::

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

