
Using the Twitter Search API
============================

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

    enterprise_search_args, enterprise_count_args = load_credentials("~/.twitter_keys.yaml",
                                                                     account_type="enterprise")

Premium Setup
-------------

Premium customers will use a bearer token for authentication. Use the
following cell for setup:

.. code:: python

    premium_search_args, premium_count_args = load_credentials("~/.twitter_keys.yaml",
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
                             resut_stream_args=enterprise_search_args) # change this if you need to

By default, tweet payloads are lazily parsed into a ``Tweet`` object. An
overwhelming number of tweet attributes are made available directly, as
such:

.. code:: python

    [print(unidecode(tweet.all_text)) for tweet in tweets[0:10]];


.. parsed-literal::

    3 years ago today, beyonce surprise dropped the fastest selling album on itunes EVER then posted this on instagram like nothing happened https://t.co/F416MG2aCZ
    .@Beyonce sells OVER 80,000 copies of her new album in 3 hours: http://t.co/PKSARIvE67
    Perfect Duet with Beyonce and Ed Sheeran is the perfect combo ughhh
    As we celebrate the anniversary of 'BEYONCE,' I would just like to say that it is easily THE swankiest vinyl I own.
    Beyonce talks about natural disasters and climate change at 'Hand In Hand' Harvey Relief Telethon https://t.co/rP0wTIoUGx
    Perfect Duet (with Beyonce) by Ed Sheeran is number 2 in Austria #iTunes top 100 songs https://t.co/qqlBFLHpzl
    beyonce has truly delivered within the past week https://t.co/DDboQFBIgG
    I'll never forget waking up in the morning to a number of tweets from my friends. I was so confused. I switched on my computer, got onto iTunes and there it was... Beyonce EVERYWHERE! I screamed &amp; jumped up &amp; down in excitement and disbelief! Iconic! https://t.co/peN7Oyc5po
    Beyonce explaining her intent behind the BEYONCE visual album &amp; how she wanted to reinstate the idea of an album release as a significant, exciting event which had lost meaning in the face of hype created around singles.  https://t.co/pK2MB35vYl
    i had like 25 dollars in my account and used half of them to buy that album. songs AND VIDEOS??? BEYONCE WYD???? Man what a night.
    Ed Sheeran released the song without Beyonce and it didn't go #1. He released the song with Beyonce and it did go #1. it's clear and simple. he needed her to go #1 https://t.co/RteEZBzJu8


.. code:: python

    [print(tweet.created_at_datetime) for tweet in tweets[0:10]];


.. parsed-literal::

    2017-10-27 18:22:07
    2017-10-27 18:17:37
    2017-10-27 01:25:39
    2017-10-26 14:24:05
    2017-10-26 13:50:40
    2017-10-26 13:36:19
    2017-10-26 13:35:57
    2017-10-26 02:40:25
    2017-10-26 00:07:23
    2017-10-25 20:15:19


.. code:: python

    [print(tweet.generator.get("name")) for tweet in tweets[0:10]];


.. parsed-literal::

    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
    Twitter for iPhone
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

.. code:: python

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
    [print(unidecode(tweet.all_text)) for tweet in tweets[0:10]];


.. parsed-literal::

    BEYONCE WANTS ME DEAD https://t.co/6ztOJpz9dt
    in my college dorm and the Beyonce album popped up on iTunes and I thought it was fake because there was a Drake feature and I was like "bey would never" LITTLE DID I KNOW.... then this bitch gon post vegan cupcakes on instagram like she didn't just fuck the industry up... https://t.co/tRNo4O11uh
    When in doubt , watch a Beyonce documentary .
    Beyonce changed the game w/ that digital drop 4 years ago today! 
    
    * #1 debut on Billboard
    * Sold 617K in the US / over 828K WW in only 3 days
    * Fastest-selling album on iTunes of all time
    * Reached #1 in 118 countries
    * Widespread acclaim; hailed as her magnum opus https://t.co/lDCdVs6em3
    Beyonce x JAY Z  https://t.co/czJoAwt4eJ
    On this very day 4 years ago, as we were finishing up Scandal season finale and putting on our bonnets and Durags to sleep Beyonce said https://t.co/YFBGRmTWVY
    Everyone: *still dragging Jay for cheating*
    
    Beyonce: https://t.co/2z1ltlMQiJ
    quem e que tem dificuldades a admitir que a beyonce e a voz mais iconica da nossa geracao
    Beyonce on how nervous she was to release her self-titled... https://t.co/fru23c6DYC
    i'm bout to jump into my feelings because four years ago today i was so broke and dusty and beyonce came into my life and took the pain away.


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

    count_rule = gen_rule_payload("beyonce", count_bucket="day")
    
    counts = collect_results(count_rule, result_stream_args=enterprise_count_args)

Our results are pretty straightforward and can be rapidly used.

.. code:: python

    counts




.. parsed-literal::

    [{'count': 68745, 'timePeriod': '201712130000'},
     {'count': 95305, 'timePeriod': '201712120000'},
     {'count': 114641, 'timePeriod': '201712110000'},
     {'count': 166070, 'timePeriod': '201712100000'},
     {'count': 102049, 'timePeriod': '201712090000'},
     {'count': 87710, 'timePeriod': '201712080000'},
     {'count': 196157, 'timePeriod': '201712070000'},
     {'count': 210664, 'timePeriod': '201712060000'},
     {'count': 88572, 'timePeriod': '201712050000'},
     {'count': 96794, 'timePeriod': '201712040000'},
     {'count': 177595, 'timePeriod': '201712030000'},
     {'count': 120102, 'timePeriod': '201712020000'},
     {'count': 186758, 'timePeriod': '201712010000'},
     {'count': 151212, 'timePeriod': '201711300000'},
     {'count': 79311, 'timePeriod': '201711290000'},
     {'count': 107175, 'timePeriod': '201711280000'},
     {'count': 58192, 'timePeriod': '201711270000'},
     {'count': 48327, 'timePeriod': '201711260000'},
     {'count': 59638, 'timePeriod': '201711250000'},
     {'count': 85201, 'timePeriod': '201711240000'},
     {'count': 91542, 'timePeriod': '201711230000'},
     {'count': 64129, 'timePeriod': '201711220000'},
     {'count': 92065, 'timePeriod': '201711210000'},
     {'count': 101617, 'timePeriod': '201711200000'},
     {'count': 84733, 'timePeriod': '201711190000'},
     {'count': 74887, 'timePeriod': '201711180000'},
     {'count': 76091, 'timePeriod': '201711170000'},
     {'count': 81849, 'timePeriod': '201711160000'},
     {'count': 58423, 'timePeriod': '201711150000'},
     {'count': 78004, 'timePeriod': '201711140000'},
     {'count': 118078, 'timePeriod': '201711130000'}]



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

    # using unidecode only to 
    [print(unidecode(tweet.all_text)) for tweet in tweets[0:10]];


.. parsed-literal::

    More clarity on our private information policy and enforcement. Working to build as much direct context into the product too https://t.co/IrwBexPrBA
    To provide more clarity on our private information policy, we've added specific examples of what is/is not a violation and insight into what we need to remove this type of content from the service. https://t.co/NGx5hh2tTQ
    Launching violent groups and hateful images/symbols policy on November 22nd https://t.co/NaWuBPxyO5
    We will now launch our policies on violent groups and hateful imagery and hate symbols on Nov 22. During the development process, we received valuable feedback that we're implementing before these are published and enforced. See more on our policy development process here  https://t.co/wx3EeH39BI
    @WillStick @lizkelley Happy birthday Liz!
    Off-boarding advertising from all accounts owned by Russia Today (RT) and Sputnik.
    
    We're donating all projected earnings ($1.9mm) to support external research into the use of Twitter in elections, including use of malicious automation and misinformation. https://t.co/zIxfqqXCZr
    @TMFJMo @anthonynoto Thank you
    @gasca @stratechery @Lefsetz letter
    @gasca @stratechery Bridgewater's Daily Observations
    Yup!!!! [?][?][?][?] #davechappelle https://t.co/ybSGNrQpYF
    @ndimichino Sometimes
    Setting up at @CampFlogGnaw https://t.co/nVq8QjkKsf

