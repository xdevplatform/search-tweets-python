Python Twitter Search API
=========================

This library serves as a python interface to the `Twitter premium and enterprise search APIs <https://developer.twitter.com/en/docs/tweets/search/overview/30-day-search>`_. It provides a command-line utility and a library usable from within python. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.

Pretty docs can be seen `here <https://twitterdev.github.io/search_tweets_api/>`_.


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

We will host the package on PyPi so it's pip-friendly.

.. code:: bash

  pip install searchtweets

Or the development version locally via

.. code:: bash

  git clone https://github.com/twitterdev/search-tweets-python
  cd search-tweets-python
  pip install -e .



Using the Comand Line Application
=================================

We provide a utility, ``search_tweets.py``, in the ``tools`` directory that provides rapid access to tweets.
Premium customers should use ``--bearer-token``; enterprise customers should use ``--user-name`` and ``--password``.

The ``--endpoint`` flag will specify the full URL of your connection, e.g.:


.. code:: bash

  https://api.twitter.com/1.1/tweets/search/30day/dev.json

You can find this url in your developer console.

Note that the ``--results-per-call`` flag specifies an argument to the API call ( ``maxResults``, results returned per CALL), not as a hard max to number of results returned from this program. use ``--max-results`` for that for now.



**Stream json results to stdout without saving**

.. code:: bash

  python search_tweets.py \
    --bearer-token <BEARER_TOKEN> \
    --endpoint <MY_ENDPOINT> \
    --max-results 1000 \
    --results-per-call 100 \
    --filter-rule "beyonce has:hashtags" \
    --print-stream


**Stream json results to stdout and save to a file**

.. code:: bash

  python search_tweets.py \
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

  python search_tweets.py \
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

  python search_tweets.py \
    --config-file myapiconfig.config \
    --no-print-stream


Using the Twitter Search APIs within Python
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

Your credentials should be put into a YAML file that looks like this:

.. code:: .yaml


    search_tweets_api:
      endpoint: <FULL_URL_OF_ENDPOINT>
      account: <ACCOUNT_NAME>
      username: <USERNAME>
      password: <PW>
      bearer_token: <TOKEN>

And filling in the keys that are appropriate for your account type.
Premium users should only have the ``endpoint`` and ``bearer_token``;
Enterprise customers should have ``account``, ``username``,
``endpoint``, and ``password``.

Our credential reader will default this file being in
``"~/.twitter_keys.yaml"``, but you can pass the relevant location as
needed. You can also specify a different key in the yaml file, which can
be useful if you have different endpoints, e.g., ``dev``, ``test``,
``prod``, etc. The file might look like this:

.. code:: .yaml


    search_tweets_dev:
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      
    search_tweets_prod:
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      

The following cell demonstrates the basic setup that will be referenced
throughout your program's session.

.. code:: python

    from searchtweets import ResultStream, gen_rule_payload, load_credentials

Enterprise setup
----------------

If you are an enterprise customer, you'll need to authenticate with a
basic username/password method. You can specify that here:

.. code:: python

    enterprise_search_args = load_credentials("~/.twitter_keys.yaml",
                                              account_type="enterprise")

Premium Setup
-------------

Premium customers will use a bearer token for authentication. Use the
following cell for setup:

.. code:: python

    premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                           yaml_key="search_tweets_premium",
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

    It was okay for Beyonce to stay when Jay Z cheated but not okay for Cardi to stay with Offset. You people and your double standards man.
    
    @Captivate 🔥🔥 Black Kings &amp; Queens🔥🔥 
    https://t.co/RvpJNpKEA1
    #tidal #Spotify #blackish #BlackTwitter #BlackExcellence #RevoltNow @BadBoyEnt @RocNation @djkhaled @S_C_ @DJInfamousATL @djenvy @Diddy @Beyonce #bmore #baltimorecity #share  IG; kingdavid_2022
    
    *Beyoncé comes on* Friends: please don't do it i swear it's so embarras-- 
    
    Me: https://t.co/tqup7M67jI
    
    Somebody just said Beyoncé gone release the twins on tidal. https://t.co/4kmk8w9pFf
    
    los gringos tienen como 200k d rts acá tenemos 2k y nos sentimos beyoncé
    
    @BarbaraLafranc2 🔥🔥 Black Kings &amp; Queens🔥🔥 
    https://t.co/RvpJNpKEA1
    #tidal #Spotify #blackish #BlackTwitter #BlackExcellence #RevoltNow @BadBoyEnt @RocNation @djkhaled @S_C_ @DJInfamousATL @djenvy @Diddy @Beyonce #bmore #baltimorecity #share  IG; kingdavid_2022
    
    The president of the United States is busy calling this country a shithole, meanwhile Beyoncé’s charity is entering its EIGTH year of supporting their charities after a devastating earthquake killed thousands.  https://t.co/9qVtPQKp8W
    8 years ago today an earthquake hit Haiti that devastated families. We responded and launched #BEYGOODHAITI to help revitalize Saint Damien Pediatric Hospital. We remain in partnership with them and encourage you to also support: https://t.co/Sb1AS8rA4g https://t.co/iMuk00Zllv
    
    So after a few days I finally figured out witch song has the best Intro and everyone agreed with me 😂 It has to be Beyoncé ... https://t.co/cc5rcJD1YJ
    
    Jay Z and Beyoncé don't even follow each other. That's a real relationship goal bitch mind ya business.
    
    Hold Up by Beyoncé 
    #BadLiar #BestMusicVideo #iHeartAwards https://t.co/fTgMBccdc1
    78. If Selena had to reenact and lip sync to this Music Video, which one you want it to be, 'Hold Up' by Beyonce or 'Side To Side' by Ariana
    


.. code:: python

    [print(tweet.created_at_datetime) for tweet in tweets[0:10]];


.. parsed-literal::

    2018-01-12 21:05:39
    2018-01-12 21:05:39
    2018-01-12 21:05:36
    2018-01-12 21:05:34
    2018-01-12 21:05:34
    2018-01-12 21:05:33
    2018-01-12 21:05:32
    2018-01-12 21:05:31
    2018-01-12 21:05:31
    2018-01-12 21:05:30


.. code:: python

    [print(tweet.generator.get("name")) for tweet in tweets[0:10]];


.. parsed-literal::

    Twitter for iPhone
    Twitter for iPhone
    Twitter for Android
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

    Me when Beyoncé disappears for days. https://t.co/jPBt94K9xR
    Why is it okay for
    Beyoncé to make $50
    million and not okay
    for a CEO who has
    3000 employees and
    $100 million in profit to
    make $5 million?
    Just saw some dude say Tomi Lahren look better than Beyonce
    
    ...boy https://t.co/9YsVVMcEqy
    @writemombritt @GAPeachMeg @skb_sara @PaulLee85 @TheSlimSupreme @MistaBRONCO @TheBeard1611 @Redheaded_Jenn @Keque_Mage @Flewbys @W_C_Patriot Jay Z watches Beyoncé kissing Barack Obama
    A partir du moment ou un homme qui était dans une télé-réalité et sur un ring de catch se retrouve a la tête de la 1ere puissance mondiale j'exclu plus rien dans ma vie, donc la j'ai comme objectif de baiser Beyoncé
    23) ANYTHING FOR YOU BEYONCE
    https://t.co/MoZNaAoT0i
    Cardi B ties Beyonce’s Billboard Hot R&amp;B/Hip-Hop songs record https://t.co/wd2EIBC0zM https://t.co/S1Ul8wqO41
    BEYONCÉ still holds the record for #1s in the most countries on iTunes when it topped 117 charts in 2013 simultaneously. https://t.co/XTcfncnWzj
    I love Beyoncé but she is a beautiful demon Michelle looks like she’s in an abusive relationship https://t.co/HvGngt4iCk
    future sings with way more passion that beyoncé if we keeping it a buck


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

    [{'count': 41513, 'timePeriod': '201801120000'},
     {'count': 42012, 'timePeriod': '201801110000'},
     {'count': 47334, 'timePeriod': '201801100000'},
     {'count': 66070, 'timePeriod': '201801090000'},
     {'count': 96729, 'timePeriod': '201801080000'},
     {'count': 162544, 'timePeriod': '201801070000'},
     {'count': 105965, 'timePeriod': '201801060000'},
     {'count': 93191, 'timePeriod': '201801050000'},
     {'count': 110430, 'timePeriod': '201801040000'},
     {'count': 127657, 'timePeriod': '201801030000'},
     {'count': 132053, 'timePeriod': '201801020000'},
     {'count': 176279, 'timePeriod': '201801010000'},
     {'count': 57287, 'timePeriod': '201712310000'},
     {'count': 72341, 'timePeriod': '201712300000'},
     {'count': 72151, 'timePeriod': '201712290000'},
     {'count': 76440, 'timePeriod': '201712280000'},
     {'count': 61644, 'timePeriod': '201712270000'},
     {'count': 55203, 'timePeriod': '201712260000'},
     {'count': 59181, 'timePeriod': '201712250000'},
     {'count': 106356, 'timePeriod': '201712240000'},
     {'count': 115224, 'timePeriod': '201712230000'},
     {'count': 73473, 'timePeriod': '201712220000'},
     {'count': 89280, 'timePeriod': '201712210000'},
     {'count': 192571, 'timePeriod': '201712200000'},
     {'count': 85625, 'timePeriod': '201712190000'},
     {'count': 57924, 'timePeriod': '201712180000'},
     {'count': 70558, 'timePeriod': '201712170000'},
     {'count': 41087, 'timePeriod': '201712160000'},
     {'count': 62799, 'timePeriod': '201712150000'},
     {'count': 55363, 'timePeriod': '201712140000'},
     {'count': 98255, 'timePeriod': '201712130000'}]



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

