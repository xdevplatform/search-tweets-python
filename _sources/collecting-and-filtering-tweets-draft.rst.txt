
*note*
======

This post is an early draft and we expect changes to be made to it, in
both code and content, before it is more broadly publicized. If you are
reading this and have any feedback for us regarding this post, please
reach out to either `\@binary\_aaron <https://twitter.com/binary_aaron>`__
or `\@notFromShrek <https://twitter.com/notFromShrek>`__ on Twitter or via
`email <mailto:agonzales@twitter.com>`__.

Working with Twitter Data Examples Series
=========================================

The Twitter Data Enterprise Solutions Data Science team wants to help
people get more out of Twitter data. We are going to publish a series of
focused examples that show how to work with various products in the
Twitter API ecosystem to help you get to answers more quickly.
Throughout our series, we will touch on many points on working with
Twitter data and how nuances of our data affect common data-processing
paradigms.

Data collection, filtering, and parsing
---------------------------------------

-- By Fiona Pigott (@notFromShrek), Twitter Data Scientist

In this inaugural post, I'll introduce data collection, filtering,
parsing, and summarizing. I want to be able to give readers an easy way
to spin up on the Twitter Search API, some tips around quickly examining
data, and guidelines around one of the most difficult and most
overlooked Twitter data challenges: making sure you get the right Tweets
for the job.

Caveat
^^^^^^

This post is not meant to be a tutorial in Python or the PyData
ecosystem and assumes that readers have a reasonable amount of technical
sophistication, such that they could find the right tweets for their use
case in any language or framework. Our group makes heavy use of the
PyData stack (python, pandas, numpy, etc.) and I suggest that you do to
for the ease of use in data science or analytics projects.

Using Twitter data to answer a question
---------------------------------------

Typically you will start with a very high-level question that requires
refinement to understand what data might be useful to you in answering
that question. For this post, let's start with a broad question:

::

    I want to understand airline customers while they fly.

We'll begin our refinement process from here.

*Why* do we want to know this?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Understanding the business need behind a question is paramount. Use it
to understand where it is important to spend extra time to be exact, and
where an estimation will suffice. Also use "why" to understand when the
analysis needs to be complete--the best analysis is not useful if it is
finished a month after a decision is made and presented.

*What* are we interested in?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use this question to help define where to begin with the analysis and
which data to pull. To understand airline customers' behavior while they
are flying and getting ready to fly, we are interested in people
actually in an airport or on a plane, but we are not interested in
people simple talking about airlines (sharing news stories about an
airline, for instance).

*When* is this information relevant?
^^^^^^^^^^^^^^^^^

Deciding on a relevant timeframe is all about the business use case: if
you're tracking a trend over a long period of time, you may need years
of data; if you're looking at the audience of a single TV premier, a few
days of data may be enough.

In the case of my air travel question, I'm only interested in any given
Twitter user in the few hours around their plane flight, so I don't
necessarily need to track Tweets over a long period of time. I do,
however, want to get enough of a sample to make generalizations about
how people Tweet before and after flights, so I should make sure I
collect enough data over a long enough period of time to examine
multiple flights.

*Who* are we interested in?
^^^^^^^^^^^^^^^^^

Using simple rule filters like country and language can go a long way
towards helping us analyze Tweets from the right people. For more
detail, we can use available Twitter and partner tools to determine some
demographics about users--how old they are, their gender, their
nationality and language.

In this case, we're interested in people from all demographics, as long
as they are *also* passengers on an airline. We can likely identify
those people through their language ("About to take off, headed home to
Boulder!") or their granular geo-tagged location or Twitter place
("Denver International Airport").

*Where* are they?
^^^^^^^^^^^^^^^^^

We can use Twitter's geo data and enrichments to make sure that our
users are in relevant locations, if that is important to the question.
Another way to approximate a user's location might be the language they
speak, or even the time that they are Tweeting (if you're collecting
Tweets at 2AM PST, don't expect to see a lot of content from
California).

Remember, selecting only users for whom we have a very granular
locations (like a geo-tag near an airport) means that we only get a
sample of users. For studies where we want to know generally what people
are talking about that might not be a problem, but it isn't as effective
for studies where we want an exact count. Keep those trade-offs in mind
when designing a data query.

--------------

Steps to get to an answer:
--------------------------

1. Consume Tweet data

   -  We need to get Tweets to analyze them. I'll walk through using the
      Python client for the Twitter Search API right inside this
      notebook. All you need is an account.

2. Parse Twitter data

   -  You can't analyze what you can't load. Understand the structure of
      the data, and get the pieces that are important to your analysis.

3. Describe Twitter data

   -  Descriptive statistics go a long way. What are the most popular
      hashtags? When are people Tweeting about these topics? Where is
      noise coming from? Are there specific URLs, hashtags, or
      @-mentions being shared that *aren't* relevant to your analysis?

4. Iterate on your search terms to filter the data

   -  We can't simply ask for every Tweet. A thoughtful analysis needs
      to work within the bounds of the Twitter data APIs to filter and
      retrieve the right data for the job--and for your data budget. Now
      that you know how to quickly edit rules to retrieve small
      quantities of data, as well as parse and describe a set of Tweets,
      it's time to iterate on filters to retrieve the data that is
      relevant to your question (and not pay for data that isn't).

--------------

1. Consume Tweet data: the Twitter Search API
---------------------------------------------

Twitter API query language
^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to pull Tweets from the Search API, you will first have to
understand how to write a search query in Twitter's Premium / Enterprise
Search API query language. The most important basics are these:

-  Token matches: A simple token match occurs within the text of the
   Tweet (includes the links that appear in that text, but, for
   instance, this would not include the text of the Tweet author's
   name). Token matches always disregard case.
-  AND: words (tokens) joined by a space are treated as queries and-ed
   together. For instance, the query "``cat dog``" would search for
   Tweets with both ``cat`` and ``dog`` somewhere in the text of the
   Tweet.
-  OR: the operator "``OR``" (capitalization is important here) between
   two tokens means that your rule will match on either term (without
   needing both to be present). The rule "``cat OR dog``" will match on
   a Tweet with *either* "``cat``" or "``dog``" in the Tweet text.
-  Grouping: use parentheses ``()`` to group tokens together. In the
   query-language order of operations, ``AND`` is applied before ``OR``,
   so use parenthese to make your groups explicit.
   "``cat dog OR bunny``" is different from "``cat (dog OR bunny)``"
   (can you see why?).
-  Negation: use the operator "``-``" to negate terms. You might search
   for Tweets about cats and *not* about dogs with this type of query
   "``cat -dog``".

Detailed information on operators can be found
`here <https://developer.twitter.com/en/docs/tweets/search/guides/premium-operators>`__.
I'll use and introduce some more advanced operators later.

Consuming Tweets
^^^^^^^^^^^^^^^^

In order to Search for Tweets, we're going to use Twitter's fully
supported, `enterprise-grade Twitter search
tool <https://developer.twitter.com/en/docs/tweets/search/overview/full-archive-search>`__.
This tools allows a user to make a request for Tweets by specifying a
rule (more on that in a minute) that matches some Tweets and retrieve
results. This tutorial is also compatible with the 30-day search API,
though you will have to change some of the dates for searching due to
the 30-day historic limitation.

Requesting some Tweets
^^^^^^^^^^^^^^^^^^^^^^

In order to search for Tweets, we have to understand specifically how
Twitter's search rules work. I'll outline a few simple rules, and we'll
talk more about details later when we iterate on our rules.

| **Time window for search**
| Look for Tweets within a certain time window by specifying the time
  window in minute granularity.

| **Search rules are simple, boolean, token matches**
| Tweets are tokenized on spaces and punctuation, and those tokens are
  matched to a rule. Let's look at a simple example:
| > **Tweet**:
  ``"Boarding the plane to fly to Tokyo in a few hours! So excited!"``
| > **Tokens** (capitalization is ignored):
  ``"boarding", "the", "plane", "to", "fly", "to", "tokyo", "in", "a", "few", "hours", "so, "excited"``

A rule that collected this Tweet might have been ``"plane"`` (because
the exact token ``"plane"`` is included in the token list). You should
note that these matches rely on complete tokens: this Tweet would
**not** match if our rule was ``"airplane"``.

| **You can search for more than one token in a rule**
| A search for Tweets about flying on planes might include any Tweet
  with the word ``"airplane"`` *or* the word ``"plane"`` *or* the word
  ``"flying"`` to get all of the relevant Tweets. In a single rule, use
  the operator ``OR`` (capitalization is important here) to search for
  *any* of a set of keywords.
| > ``"airplane OR plane OR flying"``

| **You can combine criteria using *and* logic, and combine tokens into
  phrases using quotation marks**
| Maybe you want the to find Tweet that include the word ``"flying"``
  and the word ``"plane"`` but only when they appear together. Here, you
  would want to use Boolean ``AND`` logic to combine tokens into a
  single rule. In the syntax of Twitter's Search API, ``AND`` is simply
  represented by a space. > **rule**: ``flying plane``
| > **match**: ``"I'm flying in a plane!"``
| > **no match**: ``"I'm flying!"`` or ``"I'm in a plane!"``

| You can also look for specific phrases (combinations of tokens) using
  quotation marks. Use ``"`` to combine tokens and look for them in a
  specific phrase. > **rule**: ``"air travel"``
| > **match**: ``"Air travel is great"``
| > **no match**: ``"Travel by air is great"`` or
  ``"Traveling in an airplane"``

| **You can exclude certain tokens that are irrelevant to your
  analysis**
| Keep in mind that tokens do not exactly map to meaning (especially on
  a colloquial platform like Twitter). If you are looking for Tweets
  about flying (on an airplane), and you submit the rule ``"flying"``,
  ``"I don't give a flying f**k what you do."`` would match your rule
  (true story: I've had to exclude the phrase ``"flying f**k"`` from
  this analysis 😳).
| Use a "``-``" to exclude, and use parentheses to group together
  logical clauses: > ``"(airplane OR plane OR flying) -fuck"``

This isn't a comprehensive guide, and more clarification can be found in
our
`documentation <http://support.gnip.com/apis/search_api2.0/rules.html>`__.

Getting the results
^^^^^^^^^^^^^^^^^^^

Twitter's Search API returns results in *pages*, with up to 500 Tweets
per page for paid tiers. For users in a sandbox environment, you can
receive a maximum of 100 Tweets per call. For a very low-volume search,
you might only need one page to retrieve all of the results. For a
high-volume search, you can choose to make multiple API call to receive
multiple pages of results.

Python client
^^^^^^^^^^^^^

Consuming data from Twitter APIs directly into an environment where we
can analyze them is important for fast iteration on queries. The data
science team has created some Python libraries that make it easy to
consume data from Twitter's Search API product directly into this
notebook.

This package can be found at
https://github.com/tw-ddis/twitter\_search\_api/ and implements a Python
wrapper to: - Create appropriately formatted rule payloads (date and
rule query parameters) - Make requests of the API - Gracefully handle
pagination of Search API results (be aware--the tool can make multiple
API calls, so but sure to set the ``max_tweets`` parameter, which I'll
point out) - Load the resultant Tweet text data as Python objects

Please go ahead and make a YAML file in your home directory that looks
like this:

.. code::


    twitter_search_api:
      endpoint: <FULL_URL_OF_ENDPOINT>
      account: <ACCOUNT_NAME>
      username: <USERNAME>
      password: <PW>
      bearer_token: <TOKEN>

The rest of the example will assume you have put this in a file called
``~/.twitter_keys.yaml``, though you can specify your connection
information directing in the notebook or using an environemnt variable
if you want.

If you are a premium user (or testing out premium), please set
``bearer_token``. If you have an enterprise account, please set your
account name and password. In the following cell, be sure to only
specify the relevant fields for your access method.

.. code:: python

    # Twitter data API libraries developed by the data science team to spin you up faster on Twitter data
    from tweet_parser.tweet import Tweet
    from twittersearch.result_stream import ResultStream, collect_results
    from twittersearch import gen_rule_payload
    import os
    import yaml
    
    # your account and password for enterprise access
    with open(os.path.expanduser("~/.twitter_keys.yaml")) as f:
        creds = yaml.load(f)
        
    search_args = {"username": creds["twitter_search_api"]["username"],
                   "password": creds["twitter_search_api"]["password"],
                   "endpoint": creds["twitter_search_api"]["endpoint"]}

.. code:: python

    # start with a very simple rule
    _rule_a = "(flying OR plane OR landed OR airport OR takeoff)"
    
    rule_a = gen_rule_payload(_rule_a,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            results_per_call=500) # the max_results parameter sets 
                                             # the number of Tweets I receive per API call.
                                             # this value can be at most 500
    
    # results
    # note: "collect_results" is a function that collects all of the results of (potentially many) API calls and
    #       stores them as a list. later, I'll use a ResultStream object to show you how to stream Tweets as an iterator
    #       (potentially avoid memory issues and speeding up working with very large quantities of Tweets).
    results_list = collect_results(rule_a, 
                                   max_results = 500, # this is the maximum number of Tweets you want to receive
                                                      # the number of API calls that you make will be roughly: 
                                                      #  = max_tweets / max_results
                                   result_stream_args=search_args)

.. code:: python

    # hark, a Tweet!
    results_list[0]




.. parsed-literal::

    {'contributors': None,
     'coordinates': None,
     'created_at': 'Mon Jul 31 23:59:59 +0000 2017',
     'entities': {'hashtags': [{'indices': [43, 50], 'text': 'defcon'}],
      'symbols': [],
      'urls': [],
      'user_mentions': []},
     'favorite_count': 0,
     'favorited': False,
     'filter_level': 'low',
     'geo': None,
     'id': 892173026116202498,
     'id_str': '892173026116202498',
     'in_reply_to_screen_name': None,
     'in_reply_to_status_id': None,
     'in_reply_to_status_id_str': None,
     'in_reply_to_user_id': None,
     'in_reply_to_user_id_str': None,
     'is_quote_status': False,
     'lang': 'en',
     'matching_rules': [{'tag': None}],
     'place': None,
     'quote_count': 0,
     'reply_count': 0,
     'retweet_count': 0,
     'retweeted': False,
     'source': '<a href="http://tapbots.com/tweetbot" rel="nofollow">Tweetbot for iΟS</a>',
     'text': 'Left for airport at 4:45AM, pleased to see #defcon hackers still partying at Caesars bars. Not pleased to be heading to airport at 4:45AM.',
     'truncated': False,
     'user': {'contributors_enabled': False,
      'created_at': 'Tue Jul 26 12:59:48 +0000 2016',
      'default_profile': True,
      'default_profile_image': False,
      'derived': {'klout': {'influence_topics': [{'id': '14711',
          'name': 'Computers',
          'score': 0.6900000000000001,
          'url': 'http://klout.com/topic/id/14711'},
         {'id': '10000000000000000013',
          'name': 'Armed Forces',
          'score': 0.54,
          'url': 'http://klout.com/topic/id/10000000000000000013'},
         {'id': '5715144008489027056',
          'name': 'Hacking',
          'score': 0.54,
          'url': 'http://klout.com/topic/id/5715144008489027056'},
         {'id': '6333513374221291742',
          'name': 'Information Security',
          'score': 0.44,
          'url': 'http://klout.com/topic/id/6333513374221291742'},
         {'id': '8339859935962972745',
          'name': 'Malware',
          'score': 0.4,
          'url': 'http://klout.com/topic/id/8339859935962972745'}],
        'interest_topics': [{'id': '6333513374221291742',
          'name': 'Information Security',
          'score': 0.7000000000000001,
          'url': 'http://klout.com/topic/id/6333513374221291742'},
         {'id': '8339859935962972745',
          'name': 'Malware',
          'score': 0.68,
          'url': 'http://klout.com/topic/id/8339859935962972745'},
         {'id': '10000000000000000013',
          'name': 'Armed Forces',
          'score': 0.67,
          'url': 'http://klout.com/topic/id/10000000000000000013'},
         {'id': '5715144008489027056',
          'name': 'Hacking',
          'score': 0.67,
          'url': 'http://klout.com/topic/id/5715144008489027056'},
         {'id': '14711',
          'name': 'Computers',
          'score': 0.62,
          'url': 'http://klout.com/topic/id/14711'}],
        'profile_url': 'http://klout.com/user/id/120189854649800254',
        'score': 12,
        'user_id': '120189854649800254'}},
      'description': 'davrik',
      'favourites_count': 1,
      'follow_request_sent': None,
      'followers_count': 15,
      'following': None,
      'friends_count': 27,
      'geo_enabled': False,
      'id': 757923373951422464,
      'id_str': '757923373951422464',
      'is_translator': False,
      'lang': 'en',
      'listed_count': 0,
      'location': 'cyber cyber cyber',
      'name': 'davrik',
      'notifications': None,
      'profile_background_color': 'F5F8FA',
      'profile_background_image_url': '',
      'profile_background_image_url_https': '',
      'profile_background_tile': False,
      'profile_banner_url': 'https://pbs.twimg.com/profile_banners/757923373951422464/1469539141',
      'profile_image_url': 'http://pbs.twimg.com/profile_images/757928014541905920/raYPrm1a_normal.jpg',
      'profile_image_url_https': 'https://pbs.twimg.com/profile_images/757928014541905920/raYPrm1a_normal.jpg',
      'profile_link_color': '1DA1F2',
      'profile_sidebar_border_color': 'C0DEED',
      'profile_sidebar_fill_color': 'DDEEF6',
      'profile_text_color': '333333',
      'profile_use_background_image': True,
      'protected': False,
      'screen_name': '0davrik',
      'statuses_count': 17,
      'time_zone': None,
      'translator_type': 'none',
      'url': None,
      'utc_offset': None,
      'verified': False}}



2. Parse Twitter data
---------------------

Let's take the 1st Tweet from our results list and discuss its various
elements.

Tweet data is returned from the API as JSON payloads: 1 JSON formatted
payload per Tweet, 1 Tweet per line (separated by ``\n``). The
``twittersearch`` package parses that data for you using our
``tweet_parser`` (https://github.com/tw-ddis/tweet\_parser) package and
handles any errors caused by non-Tweet messages (like logging messages),
returning ``Tweet`` objects (I'll explain about that in a second).

To better understand Tweets, you should check out
`support.gnip.com <http://support.gnip.com/sources/twitter/data_format.html>`__
for information on Tweet payload elements. For now, I'm going to explain
a few key elements of a Tweet and how to access them.

The nitty gritty: Tweet payloads
^^^^^^^^^^^^^^^^

.. code:: python

    # grab a single example Tweet: just the first one from our list
    # this is a Tweet object, but if we print it out, it looks like a python dictionary
    # that's because a Tweet object is just a Python dictionary with a few special properties defined
    example_tweet = results_list[0]
    example_tweet["id"]




.. parsed-literal::

    892173026116202498



| **A note on Tweet formatting and payload element naming**
| I happen to know that the format of this Tweet is "original format,"
  so I can look up the keys (names of payload elements) on our support
  website. It's possible (but unlikely) that your Search API stream is
  configured slightly differently, and you're looking at "activity
  streams" formatted Tweets (this is completely fine). I'll add the
  equivalent "activity streams" keys in the comments.

**Now, the text of a Tweet:**

.. code:: python

    # the text of the Tweet (the thing you type, the characters that display in the Tweet)
    # is stored as a top-level key called "text"
    print(results_list[0]["text"])
    
    # uncomment the following if you appear to have an activity-stream formatted Tweet
    # (the names of the payload elements are different, the data is similar):
    #results_list[0]["body"]


.. parsed-literal::

    Left for airport at 4:45AM, pleased to see #defcon hackers still partying at Caesars bars. Not pleased to be heading to airport at 4:45AM.


| **Other Tweet elements**
| Be sure to read the documentation, as I'm not going to enumerate every
  Tweet element here. I will note that certain fundamental and useful
  Tweet elements are extracted for you, such as a #hashtag or an
  @mention.

You can access, for instance, a Tweet's #hashtags like this:

.. code:: python

    results_list[0]["entities"]["hashtags"]
    
    # uncomment the following if you appear to have an activity-stream formatted Tweet
    #results_list[0]["twitter_entities"]["hashtags"]




.. parsed-literal::

    [{'indices': [43, 50], 'text': 'defcon'}]



.. code:: python

    # in case that first Tweet didn't actually have any hashtags:
    [x["entities"]["hashtags"] for x in results_list[0:10]]
    
    # uncomment the following if you appear to have an activity-stream formatted Tweet
    #[x["twitter_entities"]["hashtags"] for x in results_list[0:10]]




.. parsed-literal::

    [[{'indices': [43, 50], 'text': 'defcon'}],
     [],
     [{'indices': [22, 30], 'text': 'Algerie'}],
     [],
     [],
     [{'indices': [1, 5], 'text': 'New'}],
     [],
     [],
     [],
     []]



tweet\_parser
^^^^^^^^^^^^^^^^

You will always need to understand Tweet payloads to work with Tweets,
but a Python package from this team (``pip install tweet_parser``)
attempts to remove some of the hassle of accessing elements of a Tweet.
This package works seamlessly with both possible Twitter data formats,
and supplies the ``Tweet`` object I referred to earlier.

Before doing a lot of work with this package (but not right this
minute!), I would encourage you to read the documentation for the
``tweet_parser`` package at https://twitterdev.github.io/tweet\_parser/.
The package is open-source and available on GitHub at
https://github.com/twitterdev/tweet\_parser. Feel free to submit issues
or make pull requests.

The ``Tweet`` object has properties that allow you to access useful
elements of a Tweet without dealing with its format. For instance, we
can access the text of a Tweet with:

.. code:: python

    # there are several different methods that access some portion of the text of a Tweet
    print("Literally the content of the 'text' field: \n{}\n" .format(results_list[0].text))
    print("Other fields, like the content of a quoted tweet or the options of a poll: {}, {}".format(
        results_list[0].quoted_tweet.text if results_list[0].quoted_tweet else None,
        results_list[0].poll_options))


.. parsed-literal::

    Literally the content of the 'text' field: 
    Left for airport at 4:45AM, pleased to see #defcon hackers still partying at Caesars bars. Not pleased to be heading to airport at 4:45AM.
    
    Other fields, like the content of a quoted tweet or the options of a poll: None, []


.. code:: python

    # as the Twitter platform changes, so do the fields in the data payload.
    # for instance, "extended" and "truncated" tweets have been introduced to stop 280 character from causing 
    # breaking changes
    # the Tweet object has a conveinence property ".all_text" that gets "all" the text that a Tweet displays
    results_list[0].all_text




.. parsed-literal::

    'Left for airport at 4:45AM, pleased to see #defcon hackers still partying at Caesars bars. Not pleased to be heading to airport at 4:45AM.'



I'm not going to dive into detail on every property of ``Tweet`` that I
use in this notebook, but hopefully you get the idea. When I call
``.something`` on a ``Tweet``, that ``.something`` is provided in the
``tweet_parser`` package and documented there.

For now, I will describe the elements of the payload that I'm going to
use in this analysis.

-  **time**: The time that a Tweet was created. This is always reported
   in UTC in the Tweet payload, and you can look for the user's timezone
   in the "user" portion of a Tweet payload if you want to translate
   this time to the user's time-of-day. A string of time information can
   be found in the ``created_at`` element of a Tweet, but since we're
   using the ``tweet_parser`` package, we can access a Python datetime
   object with ``tweet.created_at_datetime`` or an integer representing
   seconds since Jan 1, 1970 with ``tweet.created_at_seconds``.
-  **user**: The user who created the Tweet. The "user" portion of a
   Tweet payload contains many valuable elements, including the user's
   id (``tweet["user"]["id"]``, or ``tweet.user_id`` with the
   ``tweet_parser`` package), the user's screen name
   (``tweet.screen_name``, keep in mind that the user name may change),
   the user's timezone, potentially their derived location, their bio (a
   user-entered description at, ``tweet.bio``) and more.
-  **text**: The text of the Tweet. As Tweets get more complex
   (Retweets, Quote Tweets, poll Tweets, Tweets with hidden @-mentions
   and links), the text that you read in a Tweet can appear in many
   different areas of a Tweet payload. Here I choose to use the
   ``tweet_parser``-provided attribute ``tweet.all_text``, which
   aggregates all of the possible text fields of a Tweet (the quoted
   text, the poll text, the hidden @-mentions, etc) into one string.
-  **hashtags**: Tweet payloads contain a field that list hashtags
   present in the Tweet (you do not have to parse them out yourself).
   The ``tweet_parser`` Tweet attribute ``tweet.hashtags`` provides a
   list of hashtags.
-  **mentions**: You don't have to parse out @-mentions yourself either.
   Use ``tweet.user_mentions`` for a list of users (names and ids)
   mentioned in a Tweet.
-  **URLs**: Many Tweet contain links to outside sources, articles or
   media. You can pull the literal link text from a Tweet, or use
   Twitter's URL enrichments (if you've purchased them) to unroll URLs
   and get insight into the linked content.
-  **geo**: For the small sample of Tweets where explicit lat/lon geo
   data is available, use ``tweet.geo_coordinates`` to get locations.

.. code:: python

    # if you're not familiar with pandas, it's a data analysis python framework and a tool that we use a lot
    # I'd recommend checking out [docs] when you're done here to familiraize yourself a little
    import pandas as pd
    
    # make a pandas dataframe
    data_df = pd.DataFrame([{"date": x.created_at_datetime,
                             "text": x.all_text,
                             "user": x.screen_name,
                             "bio": x.bio,
                             "at_mentions": [u["screen_name"] for u in x.user_mentions],
                             "hashtags": x.hashtags,
                             "urls": x.most_unrolled_urls,
                             "geo": x.geo_coordinates,
                             "type": x.tweet_type,
                             "id": x.id} for x in results_list]).set_index("date")

Before you read these Tweets
^^^^^^^^^^^^^^^^

You're going to look at this Tweet data and you (should) feel a little
sad. We did all that work talking about rules, you've heard so much
about Twitter data, and these Tweets mostly don't seem relevant to our
usecase at all. They're not from our target audience (people flying on
planes) and they're not even necessarily about plane trips. What gives?

There's a reason we started out with only one API call: we didn't want
to waste calls pulling Tweets using an unrefined ruleset. This notebook
is going to be about making better decisions about rules, iterating, and
refining them until you get the Tweets that you want. And those Tweets
are out there, I promise. There are, after all, *lots* of Tweets.

.. code:: python

    # data, parsed out and ready to analyze
    data_df.head()




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>at_mentions</th>
          <th>bio</th>
          <th>geo</th>
          <th>hashtags</th>
          <th>id</th>
          <th>text</th>
          <th>type</th>
          <th>urls</th>
          <th>user</th>
        </tr>
        <tr>
          <th>date</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-07-31 23:59:59</th>
          <td>[]</td>
          <td>davrik</td>
          <td>None</td>
          <td>[defcon]</td>
          <td>892173026116202498</td>
          <td>Left for airport at 4:45AM, pleased to see #de...</td>
          <td>tweet</td>
          <td>[]</td>
          <td>0davrik</td>
        </tr>
        <tr>
          <th>2017-07-31 23:59:58</th>
          <td>[God1stAmerica2d]</td>
          <td>Proudly Politically Incorrect. Widow of US Mar...</td>
          <td>None</td>
          <td>[]</td>
          <td>892173019040202752</td>
          <td>Why is this even a question. ID needed for lic...</td>
          <td>retweet</td>
          <td>[https://twitter.com/i/web/status/892144209418...</td>
          <td>AliasHere</td>
        </tr>
        <tr>
          <th>2017-07-31 23:59:57</th>
          <td>[LPLdirect]</td>
          <td>🇬🇳🇺🇸</td>
          <td>None</td>
          <td>[Algerie]</td>
          <td>892173017186435073</td>
          <td>🔴INFOS #Algerie\n\nDeux pilotes d' Air Algérie...</td>
          <td>retweet</td>
          <td>[https://twitter.com/i/web/status/892152194920...</td>
          <td>Wyzzyddl</td>
        </tr>
        <tr>
          <th>2017-07-31 23:59:57</th>
          <td>[Simbaki_]</td>
          <td>🏳️‍🌈 sc : kailabrielleeee / match ?</td>
          <td>None</td>
          <td>[]</td>
          <td>892173016372838400</td>
          <td>We are unappreciative... we don't deserve Take...</td>
          <td>retweet</td>
          <td>[]</td>
          <td>KailaBrielleee_</td>
        </tr>
        <tr>
          <th>2017-07-31 23:59:56</th>
          <td>[realDonaldTrump]</td>
          <td>follower of Christ • Consultant • 💻 Engineer •...</td>
          <td>None</td>
          <td>[]</td>
          <td>892173013625573376</td>
          <td>@realDonaldTrump Watch Trump get lost going fr...</td>
          <td>quote</td>
          <td>[https://twitter.com/i/web/status/892173013625...</td>
          <td>LoveRunandPray</td>
        </tr>
      </tbody>
    </table>
    </div>



3. Describe your data
---------------------

Descriptive statistics can tell you a lot about your dataset with very
little special effort and customization. Having a good set of
descriptive statistics coded up that you always run on a new dataset can
be helpful. Our team maintains
`Gnip-Tweet-Evaluation <https://github.com/tw-ddis/Gnip-Tweet-Evaluation>`__
a repository on GitHub that contains some tools to do quick evaluation
of a Tweet corpus (that package is useful as a command line tool, and as
a template for Tweet evaluation).

I'm going to walk through a few different statistics that might help us
understand the data better: - **What is generating the Tweets?**: One
statistic that is common and useful in understanding a group of Tweets
is understanding how many of them are Retweets or quote Tweets. Another
interesting data point can be looking at the application that created
the Tweet itself. - **Common words**: What are the most common words in
the corpus? Are they what we expected? Are they relevant to the topic of
interest? - **Who is Tweeting**: Who are the users who Tweet the most?
Are there spammy users that should be removed? Are they important users
that we need to pay attention to? - **Where are they Tweeting from**:
What's the distribution of Tweet locations? Is that surprising? - **Time
series**: Are there spikes in the Tweet volume? When do they occur? What
drives the spikes? For the sake of filtering out noise (or news stories
that we don't care about) it may be important to identify spikes and
filter out the Tweets that drive those spikes.

.. code:: python

    # plotting library
    import matplotlib.pyplot as plt
    plt.style.use("bmh")
    %matplotlib inline

How are people Tweeting?
^^^^^^^^^^^^^^^^

Briefly, I'd like to note that there are several different Twitter
platform actions that can create a Tweet. - **original Tweet**: the user
created a Tweet by typing it into the Tweet create box or otherwise
hitting the ``statuses/update`` endpoint - **Retweet**: the user
reposted the Tweet to their own timeline, without adding and comment -
**Quote Tweet**: user added commentary to a reposted Tweet, essentially
a Tweet with another Tweet embedded in it

This is sometimes an important distinction: how much do Retweets or
Quote Tweets represent the experience of the user reposting? Do we
actually want Retweets in our particular dataset? Are they likely to
tell us anything about users who are actually travelling (put it this
way: if a user Retweets a story about being at an airport, how likely
does it seem that they are at an airport)?

.. code:: python

    data_df[["type","id"]].groupby("type").count()




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
        </tr>
        <tr>
          <th>type</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>quote</th>
          <td>16</td>
        </tr>
        <tr>
          <th>retweet</th>
          <td>294</td>
        </tr>
        <tr>
          <th>tweet</th>
          <td>190</td>
        </tr>
      </tbody>
    </table>
    </div>



Common words
^^^^^^^^^^^^^^^^

Definitions: - **corpus**: A collection of all of the documents that we
are analyzing. - **document**: A single piece of writing, in our case, a
single Tweet - **token**: Some characters from a document. Ideally,
tokens would be common enough to occur in many documents, and have some
semantic meaning--they provide us with a way to infer semantic
correlation across documents. - **stop word**: A stop word (something
like "and","but","the") is a very common word with little semantic
meaning, and we often exclude these words from word counts or NLP
models.

Tokenization
^^^^^^^^^^^^

In order to count common terms, first we have to define our terms. The
easiest thing for me to count is a token--a single unit of characters in
a Tweet. Often we try to define tokens so that a token is basically a
word.

I'm going to tokenize the Tweets (split each Tweet into a list of
tokens) using the `nltk
TweetTokenizer <http://www.nltk.org/api/nltk.tokenize.html#module-nltk.tokenize.casual>`__,
which splits on spaces and throws away some punctuation. I'm also going
to throw away any tokens that contain no letters, and throw away any
tokens that are less than 3 characters long. These choices--how to
define a token, and which tokens to count, are somewhat arbitrary, but
depend greatly on how language is used in the dataset. For instance,
many tokenizers would remove the symbols "@" and "#" as punctuation, but
on Twitter, those symbols have important semantic meaning, and should
perhaps be preserved.

.. code:: python

    from nltk.tokenize import TweetTokenizer
    from nltk.stem.porter import PorterStemmer
    
    def tweet_tokenizer(verbatim):
        try:
            tokenizer = TweetTokenizer()
            all_tokens = tokenizer.tokenize(verbatim.lower())
            # this line filters out all tokens that are entirely non-alphabetic characters
            filtered_tokens = [t for t in all_tokens if t.islower()]
            # filter out all tokens that are <=2 chars
            filtered_tokens = [x for x in filtered_tokens if len(x)>2]
        except IndexError:
            filtered_tokens = []
        return(filtered_tokens)

Counting
^^^^^^^^

Of course, we could simply create a dictionary of tokens in our corpus
and iterate through the entire corpus of Tweets and adding "1" to a
count every time we encounter a certain token, but it's more convenient
to start using the scikit-learn API now and put our token counts into a
format that's easy to use later. If you're unfamiliar with scikit-learn,
it is an excellent Python machine learning framework that implements
many common ML algorithms in a common building-block-able API.

I am going to use `scikit-learn's
CountVectorizer <http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html>`__
to count tokens and turn the corpus into a document-term matrix. This
makes it easy to count token frequencies. Note that the CountVectorizer
allows us to count not only terms ("tokens") but n-grams (collections of
tokens). For instance, if "plane" and "trip" are both tokens split on
spaces, then explicit phrase "plane trip" might be a 2-gram in our
corpus.

.. code:: python

    # get the most common words in Tweets
    from sklearn.feature_extraction.text import CountVectorizer
    
    def get_frequent_terms(text_series, stop_words = None, ngram_range = (1,2)):
        count_vectorizer = CountVectorizer(analyzer = "word",
                                           tokenizer = tweet_tokenizer,
                                           stop_words = stop_words, # try changing the stopword sets that we use.
                                                                    # notice that many top terms are words like 
                                                                    # "and" and "the"
                                           ngram_range = ngram_range # you can change this to count frequencies of 
                                                               # ngrams as well as single tokens
                                                               # a range of (1,2) counts 1-grams (single tokens) and
                                                               # 2-grams (2-token phrases)
                                          )
        term_freq_matrix = count_vectorizer.fit_transform(text_series)
        terms = count_vectorizer.get_feature_names()
        term_frequencies = term_freq_matrix.sum(axis = 0).tolist()[0]
    
        term_freq_df = (pd.DataFrame(list(zip(terms, term_frequencies)), columns = ["token","count"])
                        .set_index("token")
                        .sort_values("count",ascending = False))
        return term_freq_df

.. code:: python

    term_freq_df = get_frequent_terms(data_df["text"], 
                                      stop_words = "english") # stop_words = "english" removes words like 'and'

.. code:: python

    term_freq_df.head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>airport</th>
          <td>195</td>
        </tr>
        <tr>
          <th>flying</th>
          <td>124</td>
        </tr>
        <tr>
          <th>plane</th>
          <td>97</td>
        </tr>
        <tr>
          <th>landed</th>
          <td>45</td>
        </tr>
        <tr>
          <th>today</th>
          <td>30</td>
        </tr>
        <tr>
          <th>just</th>
          <td>29</td>
        </tr>
        <tr>
          <th>home</th>
          <td>29</td>
        </tr>
        <tr>
          <th>trump</th>
          <td>27</td>
        </tr>
        <tr>
          <th>harry</th>
          <td>27</td>
        </tr>
        <tr>
          <th>flight</th>
          <td>24</td>
        </tr>
        <tr>
          <th>got</th>
          <td>24</td>
        </tr>
        <tr>
          <th>flying home</th>
          <td>23</td>
        </tr>
        <tr>
          <th>meeting</th>
          <td>23</td>
        </tr>
        <tr>
          <th>i'm</th>
          <td>22</td>
        </tr>
        <tr>
          <th>initial</th>
          <td>22</td>
        </tr>
        <tr>
          <th>g20</th>
          <td>21</td>
        </tr>
        <tr>
          <th>dictated</th>
          <td>21</td>
        </tr>
        <tr>
          <th>way</th>
          <td>21</td>
        </tr>
        <tr>
          <th>statement</th>
          <td>21</td>
        </tr>
        <tr>
          <th>son's</th>
          <td>20</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    term_freq_df.tail(10)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>flying https://t.co/lsdvzywfrr</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying https://t.co/ofhqdrxzxd</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying https://t.co/yez213svuo</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying i'm</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying job</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying kiss</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying kisses</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying machines</th>
          <td>1</td>
        </tr>
        <tr>
          <th>flying monkey</th>
          <td>1</td>
        </tr>
        <tr>
          <th>蕾阿蕾丶elahe https://t.co/y74vcswiuq</th>
          <td>1</td>
        </tr>
      </tbody>
    </table>
    </div>



Hand labeling
^^^^^^^^^^^^^

I'm not going to walk through the process in this notebook, but never
underestimate the value of reading through your data. Actually look at
the terms in the Tweets. Identify the Tweets that look like ones you are
actually interested in.

Who is Tweeting? Who is speaking?
^^^^^^^^^^^^^^^^

.. code:: python

    # get the most commonly Tweeting users
    # I'm using Pandas functionality here to groupby and aggregate
    # read the pandas docs for more information:
    #         http://pandas.pydata.org/pandas-docs/stable/groupby.html
    (data_df[["user","bio","geo","id"]]
        .groupby("user") 
        .agg({"id":"count","bio":"first","geo":"first"}) 
        .sort_values("id",ascending = False)).head(15)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>id</th>
          <th>bio</th>
          <th>geo</th>
        </tr>
        <tr>
          <th>user</th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>babyieturtle</th>
          <td>6</td>
          <td>ELF | YG/Rapper🌸</td>
          <td>None</td>
        </tr>
        <tr>
          <th>P3air</th>
          <td>3</td>
          <td>Worldwide insurance approved King Air Flight S...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>RPMSports18</th>
          <td>2</td>
          <td>24. University of South Alabama alum. Just liv...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>heskiwi94x</th>
          <td>2</td>
          <td>An adult fangirl &amp;attended too many concerts. ...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>CollectedN</th>
          <td>2</td>
          <td>Various News, Videos, Opinions.</td>
          <td>None</td>
        </tr>
        <tr>
          <th>Spotiflynet</th>
          <td>2</td>
          <td>None</td>
          <td>None</td>
        </tr>
        <tr>
          <th>DaveDuFourNBA</th>
          <td>2</td>
          <td>Basketball Coach, Host "On the NBA with Dave D...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>thunderzsx</th>
          <td>2</td>
          <td>สายหมี.</td>
          <td>None</td>
        </tr>
        <tr>
          <th>remypost</th>
          <td>2</td>
          <td>im remy | he/him | 22 | i play literally all o...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>___13Dec</th>
          <td>2</td>
          <td>Taylor swift. | H. | The 1975. | Kodaline. | C...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>EdyAntal</th>
          <td>2</td>
          <td>S A D  B O Y S</td>
          <td>None</td>
        </tr>
        <tr>
          <th>pdougmc</th>
          <td>2</td>
          <td>Retired, Interests: Gardening, photography, cl...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>billsplacehere</th>
          <td>2</td>
          <td>None</td>
          <td>None</td>
        </tr>
        <tr>
          <th>hopia0218</th>
          <td>1</td>
          <td>@BTS_twt BTS x A.R.M.Y. \n#LOVE_YOURSELF #LOVE...</td>
          <td>None</td>
        </tr>
        <tr>
          <th>hollythomp__</th>
          <td>1</td>
          <td>http://Instagram.com/hollythomp__/</td>
          <td>None</td>
        </tr>
      </tbody>
    </table>
    </div>



Time series plot
^^^^^^^^^^^^^^^^

Another great way to get a broader picture of our data is to understand
when people are tweeting about these keywords. Now, recall that earlier
we only grabbed a tiny sample of data, so those Tweets only cover a few
minutes of activity--not a good way to build a time series. If you have
access to the enterprise level API, you will be able to make an API call
to the `counts
endpoint <https://developer.twitter.com/en/docs/tweets/search/overview/enterprise>`__
to retrieve a time series *without* needing to use many calls to
retrieve all Tweets over a time period. Let's try it out.

Counts endpoint
^^^^^^^^^^^^^^^

The counts endpoint has exactly the same API as the search endpoint, but
instead of returning Tweets, it returns counts of Tweets. This is
especially useful when you want to quickly assess a large dataset
without retrieving a lot of data.

.. code:: python

    # use the same "_rule" string
    from twittersearch import change_to_count_endpoint
    print("Recall, our rule is: {}".format(_rule_a))
    count_rule_a = gen_rule_payload(_rule_a,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            results_per_call=500, 
                            count_bucket="hour")
    
    # the endpoint changes slightly to the "counts" endpoint
    count_args = {**search_args, **{"endpoint": change_to_count_endpoint(search_args["endpoint"])}}
    
    counts_list = collect_results(count_rule_a, max_results=24*31, result_stream_args=count_args)


.. parsed-literal::

    Recall, our rule is: (flying OR plane OR landed OR airport OR takeoff)


.. code:: python

    # this is what our counts_list looks like: a count and a (UTC!) timestamp
    counts_list[0:5]




.. parsed-literal::

    [{'count': 9105, 'timePeriod': '201707312300'},
     {'count': 10024, 'timePeriod': '201707312200'},
     {'count': 9376, 'timePeriod': '201707312100'},
     {'count': 9927, 'timePeriod': '201707312000'},
     {'count': 9426, 'timePeriod': '201707311900'}]



.. code:: python

    # plot a timeseries of the Tweet counts
    tweet_counts_original = (pd.DataFrame(counts_list)
         .assign(time_bucket = lambda x: pd.to_datetime(x["timePeriod"]))
         .drop("timePeriod",axis = 1)
         .set_index("time_bucket")
         .sort_index()
    )
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize = (15,5))
    (tweet_counts_original
     .plot(ax=axes[0],
           title = "Count of Tweets per hour",
           legend = False));
    (tweet_counts_original
     .resample("D")
     .sum()
     .plot(ax=axes[1],
           title="Count of Tweets per day",
           legend=False));



.. image:: collecting-and-filtering-tweets-draft_files/collecting-and-filtering-tweets-draft_39_0.png


How can we use this information to understand our search data?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Consider the type of Tweets that we are looking for: we're looking for
Tweets from people who are talking about air travel, hopefully people
talking about their own experiences using air travel. It's pretty likely
that air travel has a relatively regular pattern, with probably some big
seasonal fluctuations (Thanksgiving?) and some daily fluctuations
(people fly, for the most part during the day); it's unlikely that 2 or
3 times as many people fly on any given Monday vs the Mondays around it.

We can use an intuition about what spikes mean in our data to either
filter out high volume noise, or, in the case where spikes are what we
are seeking out (say we wanted the audience for a movie release that
happens on a specific day), zooming in on important time periods.

Let's choose a few large spikes in this data and investigate further,
then exclude that topic from our final Twitter dataset.

Note:
^^^^^

If you don't have access to the counts API, I would still recommend
taking a few small, time-boxed samples of data across the entire period
that you're interested in and doing the same exercise. It's harder to
specifically target spikes, but it will help you get a broader sample of
data.

.. code:: python

    # you can look at the plots to get a sense of what the highest-volume tiem periods are, or just sort your dataframe
    (tweet_counts_original
     .resample("D")
     .sum()
     .sort_values(by = "count", ascending = False)
     .head())




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>time_bucket</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-07-17</th>
          <td>337743</td>
        </tr>
        <tr>
          <th>2017-07-26</th>
          <td>304237</td>
        </tr>
        <tr>
          <th>2017-07-14</th>
          <td>288738</td>
        </tr>
        <tr>
          <th>2017-07-18</th>
          <td>279771</td>
        </tr>
        <tr>
          <th>2017-07-29</th>
          <td>262412</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    # let's look at the highest volume day
    spike_rule_717 = gen_rule_payload(_rule_a, #<-remember, same rule
                                  from_date="2017-07-17",
                                  to_date="2017-07-18",
                                  results_per_call=500) # the max_results parameter sets 
                                                   # the number of Tweets I receive per API call.
                                                   # this value can be at most 500
    
    spike_results_list_717 = collect_results(spike_rule_717, max_results=500, result_stream_args=search_args)

.. code:: python

    # what are these Tweets about?
    get_frequent_terms([x.all_text for x in spike_results_list_717],
                       stop_words = "english").head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>got</th>
          <td>449</td>
        </tr>
        <tr>
          <th>flying</th>
          <td>270</td>
        </tr>
        <tr>
          <th>security</th>
          <td>223</td>
        </tr>
        <tr>
          <th>instead</th>
          <td>222</td>
        </tr>
        <tr>
          <th>flying cars</th>
          <td>220</td>
        </tr>
        <tr>
          <th>cars</th>
          <td>220</td>
        </tr>
        <tr>
          <th>office</th>
          <td>219</td>
        </tr>
        <tr>
          <th>robot</th>
          <td>218</td>
        </tr>
        <tr>
          <th>instead got</th>
          <td>218</td>
        </tr>
        <tr>
          <th>robots</th>
          <td>218</td>
        </tr>
        <tr>
          <th>robot drowned</th>
          <td>218</td>
        </tr>
        <tr>
          <th>security robot</th>
          <td>218</td>
        </tr>
        <tr>
          <th>office building</th>
          <td>218</td>
        </tr>
        <tr>
          <th>got security</th>
          <td>218</td>
        </tr>
        <tr>
          <th>suicidal robots</th>
          <td>218</td>
        </tr>
        <tr>
          <th>cars instead</th>
          <td>218</td>
        </tr>
        <tr>
          <th>building</th>
          <td>218</td>
        </tr>
        <tr>
          <th>drowned promised</th>
          <td>218</td>
        </tr>
        <tr>
          <th>promised flying</th>
          <td>218</td>
        </tr>
        <tr>
          <th>promised</th>
          <td>218</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    # It's sometimes important to get the context of a full Tweet
    [x.all_text for x in spike_results_list_717 if "international" in x.all_text.lower()][0:10]




.. parsed-literal::

    ['Greater Southwest International (KGSW / GSW) airport has been opened #AWS #gameStatus #GW2',
     'BREAKING: Fire emergency @RDUAirport Raleigh Durham international airport entire airport being evaluated https://t.co/sCVOUvlq3J',
     'BREAKING: Fire emergency @RDUAirport Raleigh Durham international airport entire airport being evaluated https://t.co/sCVOUvlq3J',
     'BREAKING: Fire emergency @RDUAirport Raleigh Durham international airport entire airport being evaluated https://t.co/sCVOUvlq3J',
     'Goodbye #merauke semoga bisa berkunjung kembali #papua @ Mopah International Airport https://t.co/0cH3IsUNUx',
     'traveling to Incheon Airport from IGIA T3:  Indira Gandhi International Airport Terminal 3, New Delhi - India https://t.co/WSGheHhyUC',
     'BREAKING: Fire emergency @RDUAirport Raleigh Durham international airport entire airport being evaluated https://t.co/sCVOUvlq3J',
     '#Medellín (@ José María Córdova International Airport - @aeropuertomde in Rionegro, Antioquia) https://t.co/X1FWVYQvJO',
     'FINALMENTEEEE #PARTIU #ALAGOAS #DEUSNOCONTROLE @ São Paulo–Guarulhos International Airport https://t.co/Oeusimjsqy',
     'Aviation enthusiasts are upset a prime viewing spot near Ottawa International Airport @FlyYOW has been closed off. https://t.co/YPMXs2xeP5 https://t.co/KnN7YZHBMV']



.. code:: python

    [(x.all_text, x.tweet_type) for x in spike_results_list_717 if "anncoulter" in x.all_text.lower()][0:10]




.. parsed-literal::

    [('Flying with my friends @Delta from SFO tomorrow and proud they treated @AnnCoulter like the dog she is.',
      'tweet'),
     ("ON PLANE &amp; CAN'T BELIEVE MY SEAT IS MISSING THE IN-FLIGHT MAGAZINE! Just kidding, I'm not unhinged like @AnnCoulter by minor inconveniences. https://t.co/6jzB8lkc9A",
      'retweet'),
     ('@GixGidea True...\n\nNever mind, @AnnCoulter. Carry on bitching about completely trivial plane fares you were refunded. Go nuts-like squirrel turd nuts.',
      'tweet'),
     ('@CWSmets @jasondashbailey @AnnCoulter To be fair, I think "investigate" means making sure there are no non-white people flying the plane.',
      'tweet'),
     ("ON PLANE &amp; CAN'T BELIEVE MY SEAT IS MISSING THE IN-FLIGHT MAGAZINE! Just kidding, I'm not unhinged like @AnnCoulter by minor inconveniences. https://t.co/6jzB8lkc9A",
      'retweet')]



.. code:: python

    # let's look at the highest volume day
    spike_rule_726 = gen_rule_payload(_rule_a, #<-remember, same rule
                                  from_date="2017-07-26",
                                  to_date="2017-07-27",
                                  results_per_call=500) # the max_results parameter sets 
                                                   # the number of Tweets I receive per API call.
                                                   # this value can be at most 500
    
    spike_results_list_726 = collect_results(spike_rule_726, max_results=500, result_stream_args=search_args)

.. code:: python

    get_frequent_terms([x.all_text for x in spike_results_list_726], stop_words = "english").head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>airport</th>
          <td>267</td>
        </tr>
        <tr>
          <th>plane</th>
          <td>130</td>
        </tr>
        <tr>
          <th>gimpo</th>
          <td>117</td>
        </tr>
        <tr>
          <th>gimpo airport</th>
          <td>111</td>
        </tr>
        <tr>
          <th>crash</th>
          <td>69</td>
        </tr>
        <tr>
          <th>tokyo</th>
          <td>67</td>
        </tr>
        <tr>
          <th>flying</th>
          <td>64</td>
        </tr>
        <tr>
          <th>preview</th>
          <td>62</td>
        </tr>
        <tr>
          <th>airport tokyo</th>
          <td>58</td>
        </tr>
        <tr>
          <th>seohyun</th>
          <td>56</td>
        </tr>
        <tr>
          <th>sooyoung</th>
          <td>55</td>
        </tr>
        <tr>
          <th>utah</th>
          <td>48</td>
        </tr>
        <tr>
          <th>small</th>
          <td>48</td>
        </tr>
        <tr>
          <th>small plane</th>
          <td>47</td>
        </tr>
        <tr>
          <th>crash utah</th>
          <td>46</td>
        </tr>
        <tr>
          <th>#news</th>
          <td>46</td>
        </tr>
        <tr>
          <th>highway</th>
          <td>46</td>
        </tr>
        <tr>
          <th>plane die</th>
          <td>45</td>
        </tr>
        <tr>
          <th>https://t.co/sizpfmclq7</th>
          <td>45</td>
        </tr>
        <tr>
          <th>#news #almalki</th>
          <td>45</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    [(x.all_text, x.tweet_type) for x in spike_results_list_726 if "gimpo" in x.all_text.lower()][0:10]




.. parsed-literal::

    [('[HD PIC] 170726 Gimpo Airport - Our boys Eunhyuk, Leeteuk and Donghae looking so good in their airport fashion! [3P] (Cr:As Tagged) https://t.co/tKCT7QApsh',
      'retweet'),
     ('170726 Gimpo Airport #Donghae [卡卡_kaka_KAKA] https://t.co/UIAgC2SroA',
      'retweet'),
     ('[Preview] 170727 Seohyun - Gimpo airport by seohyuntwunion https://t.co/klNNEAf5Ko',
      'retweet'),
     ('[Preview] 170727 Sooyoung - Gimpo airport by jtt_muk https://t.co/uKrcF8lmNe',
      'retweet'),
     ('[Preview] 170727 Sooyoung - Gimpo airport by jtt_muk https://t.co/uKrcF8lmNe',
      'retweet'),
     ('[Preview] 170727 Seohyun - Gimpo airport by mr_zhang https://t.co/5gAgwJZudT',
      'retweet'),
     ('[PRESS] 170726 Mark at Gimpo airport departures to Tokyo, Japan (2) https://t.co/urWfCgwWJZ',
      'tweet'),
     ('170726 Gimpo airport to Tokyo - Taeyong press pics #NCT127 #태용 https://t.co/qV3jfRdFuy',
      'retweet'),
     ('170727 Heechul, Shindong at Gimpo Airport going to Japan for #SMTOWNLIVEinTokyo https://t.co/YWHSgX1XZW',
      'retweet'),
     ('170727 Gimpo Airport\n\n#KimHeechul #Heechul #김희철 #희철\n\n[特纸SAMA和希大人一起niconiconi] https://t.co/OJgH9EKSSC',
      'retweet')]



.. code:: python

    [(x.all_text, x.tweet_type) for x in spike_results_list_726 if "utah" in x.all_text.lower()][0:10]




.. parsed-literal::

    [('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet'),
     ('#News by #almalki : Four aboard small plane die in crash on Utah highway https://t.co/sizPfmclq7',
      'retweet')]



3. Iterate
----------

Now that we understand what we're matching on
^^^^^^^^^^^^^^^^

-  **Exclusions**: The most important part of refining rules is often
   excluding Tweets that are irrelevant. I mentinoed earlier that the
   Search API provides a negation operator (the "``-``" operator), which
   you should use for exclusions. Use the "``-``" operator to exclude
   terms that show up in irrelevant spikes, to exclude certain kinds of
   Tweets (say, exclude Retweets), or anything else that might mark a
   Tweet as irrelevant (spammy hashtags, news articles that aren't
   interesting, etc).

-  **Advanced operators**: examples with more advanced operators (I want
   to cover URL matching, some entities maybe?)

.. code:: python

    # expand based on what you see (these are top terms that didn't seem relevant, look at the frequent terms we saw)
    _rule_b = """
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    """
    
    rule_b = gen_rule_payload(_rule_a,
                              from_date="2017-07-01",
                              to_date="2017-08-01",
                              results_per_call=500)
    
    results_list = collect_results(rule_b, max_results=500, result_stream_args=search_args)

.. code:: python

    # look at frequent terms again
    get_frequent_terms([x.all_text for x in results_list], stop_words = "english", ngram_range = (2,3)).head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>flying home</th>
          <td>23</td>
        </tr>
        <tr>
          <th>g20 trump personally</th>
          <td>20</td>
        </tr>
        <tr>
          <th>home g20 trump</th>
          <td>20</td>
        </tr>
        <tr>
          <th>home g20</th>
          <td>20</td>
        </tr>
        <tr>
          <th>dictated son's</th>
          <td>20</td>
        </tr>
        <tr>
          <th>dictated son's initial</th>
          <td>20</td>
        </tr>
        <tr>
          <th>russian lawyer</th>
          <td>20</td>
        </tr>
        <tr>
          <th>russian lawyer meeting</th>
          <td>20</td>
        </tr>
        <tr>
          <th>personally dictated</th>
          <td>20</td>
        </tr>
        <tr>
          <th>personally dictated son's</th>
          <td>20</td>
        </tr>
        <tr>
          <th>g20 trump</th>
          <td>20</td>
        </tr>
        <tr>
          <th>son's initial</th>
          <td>20</td>
        </tr>
        <tr>
          <th>initial statement</th>
          <td>20</td>
        </tr>
        <tr>
          <th>statement russian lawyer</th>
          <td>20</td>
        </tr>
        <tr>
          <th>statement russian</th>
          <td>20</td>
        </tr>
        <tr>
          <th>son's initial statement</th>
          <td>20</td>
        </tr>
        <tr>
          <th>wapo flying home</th>
          <td>20</td>
        </tr>
        <tr>
          <th>lawyer meeting https://t.co/3optdabayw</th>
          <td>20</td>
        </tr>
        <tr>
          <th>initial statement russian</th>
          <td>20</td>
        </tr>
        <tr>
          <th>trump personally</th>
          <td>20</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    # use the same "_rule" string
    print("Recall, our rule is: {}".format(_rule_b))
    count_rule_b = gen_rule_payload(_rule_b,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            count_bucket="hour")
    
    # the endpoint changes slightly to the "counts" endpoint
    count_args = {**search_args, **{"endpoint": change_to_count_endpoint(search_args["endpoint"])}}
    
    counts_list = collect_results(count_rule_b, max_results=24*31, result_stream_args=count_args)
    
    # plot a timeseries of the Tweet counts
    tweet_counts = (pd.DataFrame(counts_list)
                    .assign(time_bucket = lambda x: pd.to_datetime(x["timePeriod"]))
                    .drop("timePeriod",axis = 1)
                    .set_index("time_bucket")
                    .sort_index())
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize = (15,5))
    (tweet_counts
     .plot(ax=axes[0],
           title = "Count of Tweets per hour", legend = False));
    (tweet_counts
     .resample("D")
     .sum()
     .plot(ax=axes[1],
           title="Count of Tweets per day",
           legend=False));


.. parsed-literal::

    Recall, our rule is: 
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    



.. image:: collecting-and-filtering-tweets-draft_files/collecting-and-filtering-tweets-draft_53_1.png


Look at that regular timeseries!
^^^^^^^^^^^^^^^^

Remember when I noted that the Tweet timeseries around flying is
unlikely to have big, irregular spikes? It seems like we got rid of most
of them, save one or two. Let's look into those last spikes and exclude
those too.

.. code:: python

    # let's look at the highest volume day
    spike_rule_711 = gen_rule_payload(_rule_b, #<-remember, same rule
                                      from_date="2017-07-11",
                                      to_date="2017-07-12",
                                      ) 
    
    # force results to evaluate (this step actually makes the API calls)
    spike_results_list_711 = collect_results(spike_rule_711, max_results=500, result_stream_args=search_args)

.. code:: python

    get_frequent_terms([x.all_text for x in spike_results_list_711], stop_words = "english", ngram_range = (1,1)).head(15)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>plane</th>
          <td>244</td>
        </tr>
        <tr>
          <th>airport</th>
          <td>197</td>
        </tr>
        <tr>
          <th>crash</th>
          <td>64</td>
        </tr>
        <tr>
          <th>landed</th>
          <td>47</td>
        </tr>
        <tr>
          <th>mississippi</th>
          <td>42</td>
        </tr>
        <tr>
          <th>international</th>
          <td>38</td>
        </tr>
        <tr>
          <th>marine</th>
          <td>38</td>
        </tr>
        <tr>
          <th>i'm</th>
          <td>36</td>
        </tr>
        <tr>
          <th>killed</th>
          <td>35</td>
        </tr>
        <tr>
          <th>vermont</th>
          <td>29</td>
        </tr>
        <tr>
          <th>flight</th>
          <td>23</td>
        </tr>
        <tr>
          <th>just</th>
          <td>22</td>
        </tr>
        <tr>
          <th>taxiway</th>
          <td>22</td>
        </tr>
        <tr>
          <th>san</th>
          <td>21</td>
        </tr>
        <tr>
          <th>air</th>
          <td>18</td>
        </tr>
      </tbody>
    </table>
    </div>



Frequent terms vs frequent "n-grams"
^^^^^^^^^^^^^^^^

We've talked about using frequent terms to identify what a corpus of
Tweets is about, but I want to mention frequent "n-grams" as a slightly
more sophisticated alternative.

**n-gram**: a sequence of *n* tokens from a document

Using frequent n-grams, you might be able to identify when words show
together, in the same sequence surprisingly often--potentially
indicating spam, promotional material, memes, lyrics, or reposted
content. Pay attention to words that appear together, and you can
exclude an n-gram by excluding an "exact phrase" from your Search query.

.. code:: python

    # let's look at 2- and 3- grams
    get_frequent_terms([x.all_text for x in spike_results_list_711], stop_words = "english", ngram_range = (2,3)).head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>plane crash</th>
          <td>58</td>
        </tr>
        <tr>
          <th>international airport</th>
          <td>37</td>
        </tr>
        <tr>
          <th>mississippi plane</th>
          <td>30</td>
        </tr>
        <tr>
          <th>mississippi plane crash</th>
          <td>30</td>
        </tr>
        <tr>
          <th>killed mississippi plane</th>
          <td>29</td>
        </tr>
        <tr>
          <th>marine vermont</th>
          <td>29</td>
        </tr>
        <tr>
          <th>marine vermont killed</th>
          <td>29</td>
        </tr>
        <tr>
          <th>vermont killed mississippi</th>
          <td>29</td>
        </tr>
        <tr>
          <th>vermont killed</th>
          <td>29</td>
        </tr>
        <tr>
          <th>killed mississippi</th>
          <td>29</td>
        </tr>
        <tr>
          <th>san francisco</th>
          <td>17</td>
        </tr>
        <tr>
          <th>military plane</th>
          <td>13</td>
        </tr>
        <tr>
          <th>nearly lands</th>
          <td>11</td>
        </tr>
        <tr>
          <th>plane ticket</th>
          <td>11</td>
        </tr>
        <tr>
          <th>greatest aviation</th>
          <td>10</td>
        </tr>
        <tr>
          <th>plane landed</th>
          <td>10</td>
        </tr>
        <tr>
          <th>greatest aviation disaster</th>
          <td>10</td>
        </tr>
        <tr>
          <th>air canada</th>
          <td>10</td>
        </tr>
        <tr>
          <th>aviation disaster</th>
          <td>10</td>
        </tr>
        <tr>
          <th>landed san</th>
          <td>9</td>
        </tr>
      </tbody>
    </table>
    </div>



In my data, I can see that "mississippi plane crash", "killed
mississippi plane ", "vermont killed mississippi" all show up
frequently, and they all show up *the same number of times*. Let me find
one of those Tweets to look at:

.. code:: python

    [x.all_text for x in spike_results_list_711 if "vermont" in x.all_text.lower()][0:5]




.. parsed-literal::

    ['Marine from Vermont killed in Mississippi plane\xa0crash https://t.co/RGnRfCI0lg',
     'KMBC  @kmbc\n Marine from Vermont killed in Mississippi plane crash https://t.co/DirY01X2Pd https://t.co/QTaRr1JkNQ',
     'Pittsburgh News Marine from Vermont killed in Mississippi plane crash https://t.co/dk71SLzkm5 https://t.co/JfgXcdO1yR',
     'Marine from Vermont killed in Mississippi plane crash https://t.co/HvjlG7vp6W https://t.co/Ij4MCBBFQn',
     'Marine from Vermont killed in Mississippi plane crash https://t.co/7hSTiZxMmX https://t.co/irB0fdy6Vs']



Doesn't have much to do with the exerience of flying in a plane. Let's
exclude it. In this case, I might exclude these Tweets pretty precisely
by excluding "Marine" (it's good to pick spefic, unambiguous terms for
exclusions, so that you don't do anything too broad), but for my example
I'm going to exclude "plane crash"--it's precise enough, will exclude
other similar news-type content, and I can demonstrate exact phrase
matching.

Add this to my rule: ``-"plane crash"``

.. code:: python

    # expand based on what you see
    _rule_c = """
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    -"plane crash"
    """
    
    spike_rule_704 = gen_rule_payload(_rule_c, #<-remember, same rule
                                      from_date="2017-07-04",
                                      to_date="2017-07-05",
                                      )
    
    spike_results_list_704 = collect_results(spike_rule_704, max_results=500, result_stream_args=search_args)

.. code:: python

    get_frequent_terms([x.all_text for x in spike_results_list_704], stop_words = "english", ngram_range = (2,3)).head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>citizens east hampton</th>
          <td>39</td>
        </tr>
        <tr>
          <th>east hampton airport</th>
          <td>39</td>
        </tr>
        <tr>
          <th>citizens east</th>
          <td>39</td>
        </tr>
        <tr>
          <th>hampton airport</th>
          <td>39</td>
        </tr>
        <tr>
          <th>east hampton</th>
          <td>39</td>
        </tr>
        <tr>
          <th>international airport</th>
          <td>31</td>
        </tr>
        <tr>
          <th>hampton airport james</th>
          <td>29</td>
        </tr>
        <tr>
          <th>airport james</th>
          <td>29</td>
        </tr>
        <tr>
          <th>airport james barron</th>
          <td>29</td>
        </tr>
        <tr>
          <th>james barron</th>
          <td>29</td>
        </tr>
        <tr>
          <th>barron nyt</th>
          <td>26</td>
        </tr>
        <tr>
          <th>james barron nyt</th>
          <td>26</td>
        </tr>
        <tr>
          <th>new york</th>
          <td>17</td>
        </tr>
        <tr>
          <th>#android #gameinsight</th>
          <td>16</td>
        </tr>
        <tr>
          <th>airport city</th>
          <td>15</td>
        </tr>
        <tr>
          <th>new york times</th>
          <td>14</td>
        </tr>
        <tr>
          <th>york times</th>
          <td>14</td>
        </tr>
        <tr>
          <th>barron nyt new</th>
          <td>13</td>
        </tr>
        <tr>
          <th>nyt new</th>
          <td>13</td>
        </tr>
        <tr>
          <th>nyt new york</th>
          <td>13</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    # no idea what that's about, honestly. let's find a Tweet. try searching on the hashtag:
    [x.all_text for x in spike_results_list_704 if "gameinsight" in x.hashtags][0:5]




.. parsed-literal::

    ['¡He completado la misión Día Desafortunado en el juego Airport-City! https://t.co/Ya2oVyXXHo #android #gameinsight',
     '¡He alcanzado el nivel 8 en el juego Airport-City! https://t.co/Ya2oVyXXHo #android #gameinsight',
     'New plane in my Airport City: Turboprop! https://t.co/Ky4J5dMyBT #iOS #gameinsight',
     "I've completed Party Like You Mean It quest in Airport City! https://t.co/QaJ1PIehi7 #android #gameinsight",
     "I've completed A Chinese Torture quest in Airport City! https://t.co/QaJ1PIehi7 #android #gameinsight"]



Well, that looks like spam. Let's exclude a hashtag this time: it's
specific, seems to appear in this content, and easy to exclude. Use the
hashtag and negation operator in Search like this:

Add ``-#gameinsight``

Also, I'm not sure that "gameinsight" is all of this spike. Try
searching for "hampton" too:

.. code:: python

    [x.all_text for x in spike_results_list_704 if "hampton" in x.all_text.lower()][0:5]




.. parsed-literal::

    ['The Citizens of East Hampton v. Its Airport https://t.co/xDRiyor0Ej',
     '"The Citizens of East Hampton v. Its Airport" https://t.co/Fm6NOXqRen',
     '"The Citizens of East Hampton v. Its Airport" by JAMES BARRON via NYT https://t.co/LAMg6kHkZN https://t.co/pHhMKTw8Kx',
     '#3Novices : The Citizens of East Hampton v. Its Airport The Supreme Court’s refusal last week to review local restrictions on flights is th…',
     '"The Citizens of East Hampton v. Its Airport" by JAMES BARRON via NYT https://t.co/eaW8rdnj4M']



Now, I could add: ``-"citizens of east hampton"`` and exclude this one
news story, but I think I've identified a larger pattern.

URL matching
^^^^^^^^^^^^

News stories about planes, crashes, etc are showing up a lot, and I'm
not sure I want to see any of them in my final dataset (again, this is
absolutely a choice, and it will eliminate a lot of data, for better or
for worse). I'm going to choose to exclude all Tweets with certain big
news URLs included in them. I'm not going to get this perfect here, but
I will show you how to use the URL matching rule, and give you more
ideas about how to filter Tweets.

The ``url:<token>`` operator performs a tokenized match on words in the
unrolled URL that was posted in the Tweet. I'll eliminate Tweets with:
"nytimes","bbc","washingtonpost", "cbsnews", "reuters", "apnews", and
"news" in the URL.

Add:
``-url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news``

.. code:: python

    # expand based on what you see
    _rule_d = """
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    -"plane crash"
    -"citizens of east hampton"
    -url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news
    """

.. code:: python

    # finally, let's look at that high volume hour on July 3rd
    tweet_counts.sort_values(by = "count", ascending = False).head(2)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>time_bucket</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2017-07-03 18:00:00</th>
          <td>5098</td>
        </tr>
        <tr>
          <th>2017-07-03 19:00:00</th>
          <td>4502</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    spike_rule_703 = gen_rule_payload(_rule_d, #<-remember, same rule
                                      from_date="2017-07-03T18:00",
                                      to_date="2017-07-03T19:01",
                                      )
    
    # force results to evaluate (this step actually makes the API calls)
    spike_results_list_703 = collect_results(spike_rule_703, max_results=500, result_stream_args=search_args)

.. code:: python

    get_frequent_terms([x.all_text for x in spike_results_list_703], stop_words = "english", ngram_range = (2,3)).head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>boston airport</th>
          <td>131</td>
        </tr>
        <tr>
          <th>near boston</th>
          <td>82</td>
        </tr>
        <tr>
          <th>near boston airport</th>
          <td>77</td>
        </tr>
        <tr>
          <th>logan airport</th>
          <td>68</td>
        </tr>
        <tr>
          <th>pedestrians near</th>
          <td>57</td>
        </tr>
        <tr>
          <th>vehicle near</th>
          <td>52</td>
        </tr>
        <tr>
          <th>vehicle near boston</th>
          <td>52</td>
        </tr>
        <tr>
          <th>pedestrians struck</th>
          <td>50</td>
        </tr>
        <tr>
          <th>pedestrians struck vehicle</th>
          <td>50</td>
        </tr>
        <tr>
          <th>struck vehicle near</th>
          <td>50</td>
        </tr>
        <tr>
          <th>airport injured</th>
          <td>50</td>
        </tr>
        <tr>
          <th>struck vehicle</th>
          <td>50</td>
        </tr>
        <tr>
          <th>boston airport injured</th>
          <td>44</td>
        </tr>
        <tr>
          <th>international airport</th>
          <td>35</td>
        </tr>
        <tr>
          <th>boston's logan</th>
          <td>35</td>
        </tr>
        <tr>
          <th>boston's logan airport</th>
          <td>34</td>
        </tr>
        <tr>
          <th>people injured</th>
          <td>33</td>
        </tr>
        <tr>
          <th>multiple people</th>
          <td>30</td>
        </tr>
        <tr>
          <th>car strikes</th>
          <td>30</td>
        </tr>
        <tr>
          <th>near logan</th>
          <td>30</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    # read some Tweets
    [x.all_text for x in spike_results_list_703 if "Boston" in x.all_text][0:10]




.. parsed-literal::

    ['#gossip Car Strikes Crowd at East Boston Airport, Multiple People Injured https://t.co/lK1EIbm9OJ',
     'Tru Town Films Car Strikes Crowd at East Boston Airport, Multiple People Injured https://t.co/eUy8dWqXuD',
     'Car Strikes Crowd at East Boston Airport, Multiple People Injured https://t.co/4YcPZ3QkZA',
     'Car Strikes Crowd at East Boston Airport, Multiple People\xa0Injured https://t.co/yyijNbPa4p',
     'Pedestrians struck by vehicle near Boston airport, several injuries reported https://t.co/yOnQ9bGWBk #p2 #ctl https://t.co/ugVOtnwzLs\n\n— …',
     "The Times Picayune - Vehicle hits pedestrians near Boston's Logan Airport: report https://t.co/BpDCYg2i5R",
     'Police: Boston airport crash injures 10 pedestrians https://t.co/YlGlcHFd8u',
     'Update: Taxi incident near Boston airport being treated as accident, not terrorism, law enforcement sources say https://t.co/kgvXLkd4Zk',
     'Car Strikes Crowd at East Boston Airport, Multiple People Injured https://t.co/PfJ7xhgPLT',
     'Taxi strikes pedestrians near Boston airport, police\xa0say https://t.co/gKwp3D5sA9']



I don't want to eliminate all mentions of "Boston Airport" (because many
of those mentions are likely relevant to my study). Instead, I'll
eliminate a few common phrases like "pedestrians struck", "pedestrians
injured", "car strikes", "taxi strikes".

Add:
``-"pedestrians struck" -"pedstrians injured" -"car strikes" -"taxi strikes" -"car hits"``

.. code:: python

    # expand based on what you see
    _rule_e = """
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    -"plane crash"
    -#gameinsight
    -"citizens of east hampton"
    -url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news
    -"pedestrians struck" -"pedstrians injured" -"car strikes" -"taxi strikes" -"car hits"
    """
    
    rule_e = gen_rule_payload(_rule_e,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            )
    
    results_list = collect_results(rule_e, max_results=500, result_stream_args=search_args)

.. code:: python

    print("Recall, our new rule is: {}".format(_rule_e))
    count_rule_e = gen_rule_payload(_rule_e,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            count_bucket="hour")
    
    # the endpoint changes slightly to the "counts" endpoint
    count_args = {**search_args, **{"endpoint": change_to_count_endpoint(search_args["endpoint"])}}
    
    counts_list = collect_results(count_rule_e, max_results=24*31, result_stream_args=count_args)
    
    # plot a timeseries of the Tweet counts
    tweet_counts = (pd.DataFrame(counts_list)
         .assign(time_bucket = lambda x: pd.to_datetime(x["timePeriod"]))
         .drop("timePeriod",axis = 1)
         .set_index("time_bucket")
         .sort_index()
    )
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize = (15,5))
    _ = tweet_counts.plot(ax=axes[0], title = "Count of Tweets per hour", legend = False)
    _ = tweet_counts.resample("D").sum().plot(ax=axes[1], title = "Count of Tweets per day", legend = False)


.. parsed-literal::

    Recall, our new rule is: 
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    -"plane crash"
    -#gameinsight
    -"citizens of east hampton"
    -url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news
    -"pedestrians struck" -"pedstrians injured" -"car strikes" -"taxi strikes" -"car hits"
    



.. image:: collecting-and-filtering-tweets-draft_files/collecting-and-filtering-tweets-draft_75_1.png


Look how much irrelevant data we've eliminated
^^^^^^^^^^^^^^^^

Let's compare the volume of our first (un-refined) rule to our most
recent one.

Spoiler: We've eliminated a huge amount of unhelpful data!

Now you can begin to think about using this data in an analysis.

.. code:: python

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize = (15,5))
    tweet_counts_original.resample("D").sum().plot(ax=axes, title = "Count of Tweets per day", legend = False)
    tweet_counts.resample("D").sum().plot(ax=axes, title = "Count of Tweets per day", legend = False)




.. parsed-literal::

    <matplotlib.axes._subplots.AxesSubplot at 0x11ff3b128>




.. image:: collecting-and-filtering-tweets-draft_files/collecting-and-filtering-tweets-draft_77_1.png


.. code:: python

    get_frequent_terms([x.all_text for x in results_list], stop_words = "english", ngram_range = (1,2)).head(20)




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>count</th>
        </tr>
        <tr>
          <th>token</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>airport</th>
          <td>249</td>
        </tr>
        <tr>
          <th>plane</th>
          <td>177</td>
        </tr>
        <tr>
          <th>landed</th>
          <td>63</td>
        </tr>
        <tr>
          <th>i'm</th>
          <td>35</td>
        </tr>
        <tr>
          <th>international</th>
          <td>34</td>
        </tr>
        <tr>
          <th>just</th>
          <td>34</td>
        </tr>
        <tr>
          <th>international airport</th>
          <td>32</td>
        </tr>
        <tr>
          <th>like</th>
          <td>23</td>
        </tr>
        <tr>
          <th>people</th>
          <td>21</td>
        </tr>
        <tr>
          <th>time</th>
          <td>18</td>
        </tr>
        <tr>
          <th>security</th>
          <td>17</td>
        </tr>
        <tr>
          <th>takeoff</th>
          <td>15</td>
        </tr>
        <tr>
          <th>flight</th>
          <td>15</td>
        </tr>
        <tr>
          <th>don't</th>
          <td>15</td>
        </tr>
        <tr>
          <th>got</th>
          <td>14</td>
        </tr>
        <tr>
          <th>today</th>
          <td>14</td>
        </tr>
        <tr>
          <th>passenger</th>
          <td>14</td>
        </tr>
        <tr>
          <th>hours</th>
          <td>13</td>
        </tr>
        <tr>
          <th>know</th>
          <td>12</td>
        </tr>
        <tr>
          <th>just landed</th>
          <td>12</td>
        </tr>
      </tbody>
    </table>
    </div>



Pulling our dataset
^^^^^^^^^^^^^^^^

It's always possible to continue refining a dataset, and we should
definitely continue that work after pulling the Tweets. The key in early
data-cleaning steps is to eliminate a large bulk of irrelevant Tweets
that you don't want to store or pay for (we did that).

Now (**warning!** this will use quite a few API calls and you might want
to think twice before actually running it, I've changed the cell type so
you can't run it on accident) let's pull data with our final rule.

.. code:: python

    # the twittersearch package provides a conveinence function to show you how many API calls you've already used
    print("You have used {} API calls in this session".format(ResultStream.session_request_counter))


.. parsed-literal::

    You have used 11 API calls in this session


Store the data you pull!
^^^^^^^^^^^^^^^^^^^^^^^^

You don't want to pull this much data without saving it for later. I'm
going to use the ``ResultStream`` object to make API calls, stream data
in an iterator, hold relevant data information in memory in my Python
session, and (importantly!) stream raw Tweets to a file for later use.

Even if you don't want to run these exact API calls, pay attention to
how I do this for your own work.

Finalize your rule
^^^^^^^^^^^^^^^^^^

.. code:: python

    # this is our final rule
    print(rule_e)


.. parsed-literal::

    {"query":"(plane OR landed OR airport OR takeoff OR #wheelsup) -is:retweet -trump -harry -anncoulter -\"ann coulter\" -g20 -lawyer -gimpo -fuck -\"plane crash\" -#gameinsight -\"citizens of east hampton\" -url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news -\"pedestrians struck\" -\"pedstrians injured\" -\"car strikes\" -\"taxi strikes\" -\"car hits\"","maxResults":500,"toDate":"201708010000","fromDate":"201707010000"}


No surprises
^^^^^^^^^^^^

You should always have a guess at how many Tweets you're going to pull
*before* you pull them. Use the Counts API (if possible), or extrapolate
based on a smaller time period of data.

.. code:: python

    # I can sum up the counts endpoint results to guess how may Tweets I'll get 
    # (or, if you don't have access to the counts endpoints, try extrapolating from a single day)
    tweet_counts.sum()




.. parsed-literal::

    count    1580076
    dtype: int64



Narrowing your dataset further
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You might refine your rule and find that there are still millions of
Tweets about a topic on Twitter (this happens, there are lots of
Tweets).

If your rule is still going to pull an unrealistic number of Tweets,
maybe maybe narrow the scope of your investigation. You can: - **Narrow
the time period**: do you really need a month of data? or maybe you
could sample just a few days? - **Select more specific Tweets**: maybe
it would be helpful to your analysis to have only Tweets that are geo
tagged (this reduces data volume significantly)? Or only pull Tweets
from users with profile locations? Putting stringent requirements on
data can help speed up your analysis and make your data volume smaller.
- **Sampling**: Search API doesn't support random sampling the way that
the Historical APIs do. You'll have to come up with balanced ways of
selecting for less data, or you can sample based on geography, time,
Tweet language--anything to narrow your scope.

I'm going to show one example of this by *only* pulling Tweets from
users with a profile location (you can read up more on what a "profile
location" means in our documentation) in the state of Colorado (this is
for illustrative purposes, depending on your use case, I'd probably
recommend narrowing the time scope first).

Add: ``profile_country:US profile_region:Colorado`` to my Twitter Search
rule.

.. code:: python

    final_rule = """
    (plane OR landed OR airport OR takeoff OR #wheelsup)
    -is:retweet
    -trump
    -harry
    -anncoulter
    -"ann coulter"
    -g20
    -lawyer
    -gimpo
    -fuck
    -"plane crash"
    -#gameinsight
    -"citizens of east hampton"
    -url:nytimes -url:bbc -url:washingtonpost -url:cbsnews -url:reuters -url:apnews -url:news
    -"pedestrians struck" -"pedstrians injured" -"car strikes" -"taxi strikes" -"car hits"
    profile_country:US profile_region:"Colorado"
    """
    
    count_rule = gen_rule_payload(final_rule,
                            from_date="2017-07-01",
                            to_date="2017-08-01",
                            count_bucket="hour")
    
    # the endpoint changes slightly to the "counts" endpoint
    count_args = {**search_args, **{"endpoint": change_to_count_endpoint(search_args["endpoint"])}}
    
    counts_list = collect_results(count_rule, max_results=24*31, result_stream_args=count_args)
    
    # plot a timeseries of the Tweet counts
    tweet_counts = (pd.DataFrame(counts_list)
         .assign(time_bucket = lambda x: pd.to_datetime(x["timePeriod"]))
         .drop("timePeriod",axis = 1)
         .set_index("time_bucket")
         .sort_index()
    )
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize = (15,5))
    _ = tweet_counts.plot(ax=axes[0], title = "Count of Tweets per hour", legend = False)
    _ = tweet_counts.resample("D").sum().plot(ax=axes[1], title = "Count of Tweets per day", legend = False)



.. image:: collecting-and-filtering-tweets-draft_files/collecting-and-filtering-tweets-draft_87_0.png


.. code:: python

    tweet_counts.sum()




.. parsed-literal::

    count    7233
    dtype: int64



Save Tweets to a file, and stream them into memory
^^^^^^^^^^^^^^^^

Seems like a reasonable number of Tweets. Let's go get them.

This time, I'm going to use the ResultStream object and stream the full
Tweet payloads to a file while simultaneously creating a Pandas
DataFrame in memory of the limited Tweet fields that I care about.

If you actually want to run the cell below, you'll have to set the cell
type to "code."

.. code::

    final_rule_payload = gen_rule_payload(final_rule,
                                          from_date="2017-07-01",
                                          to_date="2017-08-01")

    stream = ResultStream(**search_args,
                           rule_payload=final_rule_payload,
                           max_results=None) # should collect all of the results

    # write_ndjson is a utility function that writes the results to a file and passes them through the iterator
    from twittersearch.utils import write_ndjson

    limited_fields = []
    for x in write_ndjson("air_travel_data.json", stream.stream()):
        limited_fields.append({"date": x.created_at_datetime,
                               "text": x.all_text,
                               "user": x.screen_name,
                               "bio": x.bio,
                               "at_mentions": [u["screen_name"] for u in x.user_mentions],
                               "hashtags": x.hashtags,
                               "urls": x.most_unrolled_urls,
                               "geo": x.geo_coordinates,
                               "type": x.tweet_type,
                               "id": x.id})
    # create a dataframe
    final_dataset_df = pd.DataFrame(limited_fields)
    final_dataset_df.head()



