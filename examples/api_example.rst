
Working with the API within a Python program is straightforward both for
Premium and Enterprise clients.

We'll assume that credentials are in the default location,
``~/.twitter_keys.yaml``.

.. code:: ipython3

    from searchtweets import ResultStream, gen_rule_payload, load_credentials

Enterprise setup
----------------

.. code:: ipython3

    enterprise_search_args = load_credentials("~/.twitter_keys.yaml",
                                              yaml_key="search_tweets_enterprise",
                                              env_overwrite=False)

Premium Setup
-------------

.. code:: ipython3

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

.. code:: ipython3

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
-  max\_results: as the API handles pagination, it will stop collecting
   when we get to this number
-  result\_stream\_args: configuration args that we've already
   specified.

For the remaining examples, please change the args to either premium or
enterprise depending on your usage.

Let's see how it goes:

.. code:: ipython3

    from searchtweets import collect_results

.. code:: ipython3

    tweets = collect_results(rule,
                             max_results=100,
                             result_stream_args=enterprise_search_args) # change this if you need to

By default, Tweet payloads are lazily parsed into a ``Tweet``
`object <https://twitterdev.github.io/tweet_parser/>`__. An overwhelming
number of Tweet attributes are made available directly, as such:

.. code:: ipython3

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
    


.. code:: ipython3

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


.. code:: ipython3

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

.. code:: ipython3

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

.. code:: ipython3

    tweets = list(rs.stream())

Tweets are lazily parsed using our `Tweet
Parser <https://twitterdev.github.io/tweet_parser/>`__, so tweet data is
very easily extractable.

.. code:: ipython3

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

.. code:: ipython3

    count_rule = gen_rule_payload("beyonce", count_bucket="day")
    
    counts = collect_results(count_rule, result_stream_args=enterprise_search_args)

Our results are pretty straightforward and can be rapidly used.

.. code:: ipython3

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

.. code:: ipython3

    rule = gen_rule_payload("from:jack",
                            from_date="2017-09-01", #UTC 2017-09-01 00:00
                            to_date="2017-10-30",#UTC 2017-10-30 00:00
                            results_per_call=500)
    print(rule)


::

    {"query":"from:jack","maxResults":500,"toDate":"201710300000","fromDate":"201709010000"}


.. code:: ipython3

    tweets = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: ipython3

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


.. code:: ipython3

    rule = gen_rule_payload("from:jack",
                            from_date="2017-09-20",
                            to_date="2017-10-30",
                            count_bucket="day",
                            results_per_call=500)
    print(rule)


::

    {"query":"from:jack","toDate":"201710300000","fromDate":"201709200000","bucket":"day"}


.. code:: ipython3

    counts = collect_results(rule, max_results=500, result_stream_args=enterprise_search_args)

.. code:: ipython3

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

