Python Twitter Search API
=========================

This library serves as a python interface to the `Twitter premium and enterprise search APIs
<https://developer.twitter.com/en/docs/tweets/search/overview/30-day-search>`_.
It provides a command-line utility and a library usable from within python. It
comes with tools for assisting in dynamic generation of search rules and for
parsing tweets.

Pretty docs can be seen `here <https://twitterdev.github.io/search_tweets_api/>`_.


Features
========

- Command-line utility is pipeable to other tools (e.g., ``jq``).
- Automatically handles pagination of results with specifiable limits
- Delivers a stream of data to the user for low in-memory requirements
- Handles Enterprise and Premium authentication methods
- Flexible usage within a python program
- Compatible with our group's Tweet Parser for rapid extraction of relevant data fields from each tweet payload
- Supports the Search Counts endpoint, which can reduce API call usage and provide rapid insights if you only need volumes and not tweet payloads


Installation
============

the ``searchtweets`` library is on Pypi:

.. code:: bash

  pip install searchtweets

Or you can install the development version locally via

.. code:: bash

  git clone https://github.com/twitterdev/search-tweets-python
  cd search-tweets-python
  pip install -e .


Credential Handling
===================


YAML
~~~~

The premium and enterprise Search APIs use different authentication schemes and we
attempt to provide methods of seamless handling for all customers. The Python API
and the command-line app support YAML-file based methods and environment variables.

A credential file can be stored anywhere, but the library will default to looking 
for it at ``~/..twitter_keys.yaml``.

.. code:: .yaml

    <key>:
      account_type: <OPTIONAL PREMIUM_OR_ENTERPRISE>
      endpoint: <FULL_URL_OF_ENDPOINT>
      username: <USERNAME>
      password: <PW>
      bearer_token: <TOKEN>

Premium clients will require the ``bearer_token`` and ``endpoint``
fields; Enterprise clients require ``username``, ``password``, and
``endpoint``. If you do not specify the ``account_type``, we attempt to
discern the account type and declare a warning about this behavior. The
``load_credentials`` function also allows ``account_type`` to be set.

You can also specify a different key in the yaml file, which can
be useful if you have different endpoints, e.g., ``dev``, ``test``,
``prod``, etc. The credential reader will default to looking for ``search_tweets_api``.

Your credential file might look like this:

.. code:: .yaml

    search_tweets_dev:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>

    search_tweets_prod:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>


Environment Variables
~~~~~~~~~~~~~~~~~~~~~

If you want or need to pass credentials via environment variables, you
can set the appropriate variables of the following:

::

    export SEARCHTWEETS_ENDPOINT=
    export SEARCHTWEETS_USERNAME=
    export SEARCHTWEETS_PASSWORD=
    export SEARCHTWEETS_BEARER_TOKEN=
    export SEARCHTWEETS_ACCOUNT_TYPE=


Loading credentials
~~~~~~~~~~~~~~~~~~~


The ``load_credentials`` function will attempt to find these variables
if it cannot load fields from the yaml file, and it will **overwrite any
found credentials from the YAML file** if they have been parsed. This
behavior can be changed by setting the ``load_credentials`` parameter
``env_overwrite`` to ``False``.

The following cells demonstrates credential handling process within a Python program.

.. code:: python

    from searchtweets import ResultStream, gen_rule_payload, load_credentials
    import os

.. code:: python

    load_credentials(filename="./search_tweets_creds_example.yaml",
                     yaml_key="search_tweets_ent_example",
                     env_overwrite=False)



.. parsed-literal::

    {'endpoint': '<MY_ENDPOINT>',
     'password': '<MY_PASSWORD>',
     'username': '<MY_USERNAME>'}



.. code:: python

    load_credentials(filename="./search_tweets_creds_example.yaml",
                     yaml_key="search_tweets_premium_example",
                     env_overwrite=False)




.. parsed-literal::

    {'bearer_token': '<A_VERY_LONG_MAGIC_STRING>',
     'endpoint': 'https://api.twitter.com/1.1/tweets/search/30day/dev.json'}



Environment Variable Overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If we set our environment variables, the program will look for them
regardless of a YAML file's validity or existence.

.. code:: python

    os.environ["SEARCHTWEETS_USERNAME"] = "ENV_USERNAME"
    os.environ["SEARCHTWEETS_PASSWORD"] = "ENV_PW"
    os.environ["SEARCHTWEETS_ENDPOINT"] = "https://endpoint"

    load_credentials(filename="nothing", yaml_key="no_key_here")


.. parsed-literal::

    cannot read file nothing
    Error parsing YAML file; searching for valid environment variables




.. parsed-literal::

    {'endpoint': 'https://endpoint',
     'password': 'ENV_PW',
     'username': 'ENV_USERNAME'}




Using the Comand Line Application
=================================

The library includes an application, ``search_tweets.py``, in the ``tools`` directory that provides rapid access to Tweets.

Note that the ``--results-per-call`` flag specifies an argument to the API call
( ``maxResults``, results returned per CALL), not as a hard max to number of
results returned from this program. The argument ``--max-results`` defines the
maximum number of results to return from a given call. All examples assume that
your credentials are set up correctly in a default location
- ``.twitter_keys.yaml`` or in environment variables.


**Stream json results to stdout without saving**

.. code:: bash

  python search_tweets.py \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --print-stream


**Stream json results to stdout and save to a file**

.. code:: bash

  python search_tweets.py \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --filename-prefix beyonce_geo \
    --print-stream


**Save to file without output**

.. code:: bash

  python search_tweets.py \
    --endpoint <MY_ENDPOINT> \
    --max-results 100 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --filename-prefix beyonce_geo \
    --no-print-stream


Options can be passed via a configuration file (either ini or YAML). An
example file can be found in the ``tools/api_config_example.config`` or ``./tools/api_yaml_example.yaml`` files, which might look like this:

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


or this:

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

  python search_tweets.py \
    --config-file myapiconfig.config \
    --no-print-stream



Using the Twitter Search APIs Python Wrapper
============================================

Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

Our group's python `tweet parser
library <https://github.com/twitterdev/tweet_parser>`__ is a
requirement.


Search API usage
----------------

We'll now load our proper credentials and move on with the example.

Enterprise setup
~~~~~~~~~~~~~~~~

.. code:: python

    enterprise_search_args = load_credentials("~/.twitter_keys.yaml",
                                              yaml_key="search_tweets_enterprise",
                                              env_overwrite=False)

Premium Setup
~~~~~~~~~~~~~

.. code:: python

    premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                           yaml_key="search_tweets_premium",
                                           env_overwrite=False)

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

-  rule: a valid PowerTrack rule, referenced earlier
-  max\_results: as the API handles pagination, it will stop collecting
   when we get to this number
-  result\_stream\_args: configuration args that we've already
   specified.

For the remaining examples, please change the args to either premium or
enterprise depending on your usage.

Let's see how it goes:

.. code:: python

    from searchtweets import collect_results

.. code:: python

    tweets = collect_results(rule,
                             max_results=100,
                             result_stream_args=enterprise_search_args) # change this if you need to

By default, tweet payloads are lazily parsed into a ``Tweet`` object. An
overwhelming number of tweet attributes are made available directly, as
such:

.. code:: python

    [print(tweet.all_text, end='\n\n') for tweet in tweets[0:10]];


.. parsed-literal::

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


.. parsed-literal::

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


.. parsed-literal::

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

We can also use the Search API Counts endpoint to get counts of tweets
that match our rule. Each request will return up to *30* results, and
each count request can be done on a minutely, hourly, or daily basis.
The underlying ``ResultStream`` object will handle converting your
endpoint to the count endpoint, and you have to specify the
``count_bucket`` argument when making a rule to use it.

The process is very similar to grabbing tweets, but has some minor
differences.

*Caveat - premium sandbox environments do NOT have access to the Search
API counts endpoint.*

.. code:: python

    count_rule = gen_rule_payload("beyonce", count_bucket="day")
    
    counts = collect_results(count_rule, result_stream_args=enterprise_search_args)

Our results are pretty straightforward and can be rapidly used.

.. code:: python

    counts




.. parsed-literal::

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

Let's make a new rule and pass it dates this time.

``gen_rule_payload`` takes dates of the forms ``YYYY-mm-DD`` and
``YYYYmmDD``.

**Note that this will only work with the full archive search option**,
which is available to my account only via the enterprise options. Full
archive search will likely require a different endpoint or access
method; please see your developer console for details.

.. code:: python

    rule = gen_rule_payload("from:jack",
                            from_date="2017-09-01",
                            to_date="2017-10-30",
                            results_per_call=500)
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
