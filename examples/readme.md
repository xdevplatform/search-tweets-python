
## Using the twitter search API

Working with the API within a Python program is straightforward both for Premium and Enterprise clients. You can start by installing the api via

`pip install twittersearch`

Our group's python tweet parser library is a requirement.

Prior to starting your program, an easy way to define your secrets will be setting an environment variable. If you are an enterprise client, your authentication will be a (username, password) pair. If you are a premium client, you'll need to get a bearer token that will be passed with each call for authentication.

```
export TWITTER_SEARCH_PW=<password>
export TWITTER_SEARCH_ACCOUNT_NAME=<account_name>
export TWITTER_SEARCH_BEARER_TOKEN=<token>
```


The other points that you will have to set in the program are your endpoint, the api you want to use. There are functions to generate correct API endpoints from this info as well as flags to use the `counts` endpoint instead of the regular endpoint.

The following cell demonstrates the basic setup that will be referenced throughout your program's session.


```python
import os
import json
from twittersearch import ResultStream, gen_endpoint, gen_rule_payload

# set your environment variables here for enterprise access if you need to
# os.environ["TWITTER_SEARCH_ACCOUNT_NAME"] = ""
# os.environ["TWITTER_SEARCH_PW"] = ""
# os.environ["TWITTER_SEARCH_BEARER_TOKEN"] = ""


username = "agonzales@twitter.com"
search_api = "fullarchive"
endpoint_label = "ogformat.json"
account_kind = "enterprise"

search_endpoint = gen_endpoint(kind="enterprise", 
                               search_api=search_api,
                               account_name=os.environ["TWITTER_SEARCH_ACCOUNT_NAME"],
                               label=endpoint_label,
                               count_endpoint=False)

search_args = {"username": username,
               "password": os.environ["TWITTER_SEARCH_PW"],
               "url": search_endpoint,
               }

print(search_endpoint.replace(os.environ["TWITTER_SEARCH_ACCOUNT_NAME"], '<account_name>'))
```

    https://gnip-api.twitter.com/search/fullarchive/accounts/<account_name>/ogformat.json


There is a function that formats search API rules into valid json queries called `gen_rule_payload`. It has sensible defaults, such as pulling more tweets per call than the default 100, not including dates, and defaulting to hourly counts when using the counts api. Discussing the finer points of generating search rules is out of scope for these examples; I encourage you to see the docs to learn the nuances within, but for now let's see what a rule looks like.


```python
rule = gen_rule_payload("@robotprincessfi")
print(rule)
```

    {"query":"@robotprincessfi","maxResults":500}


This rule will match tweets that mention `@robotprincessfi`.

We'll use the `search_args` variable to power the configuration point for the API. The object also takes a valid PowerTrack rule and has options to cutoff search when hitting limits on both number of tweets and API calls.

Let's create a result stream:


```python
rs = ResultStream(**search_args, rule_payload=rule, max_results=500, max_pages=1, )
```


```python
print(str(rs).replace(os.environ["TWITTER_SEARCH_ACCOUNT_NAME"], '<account_name>'))
```

    ResultStream: 
    	{
        "username":"agonzales@twitter.com",
        "url":"https:\/\/gnip-api.twitter.com\/search\/fullarchive\/accounts\/<account_name>\/ogformat.json",
        "rule_payload":{
            "query":"@robotprincessfi",
            "maxResults":500
        },
        "tweetify":true,
        "max_results":500
    }


There is a function, `.stream`, that seamlessly handles requests and pagination for a given query. It returns a generator, and to grab our 500 tweets that mention `@robotprincessfi` we can do this:


```python
tweets = list(rs.stream())
```

    using username and password for authentication


Tweets are lazily parsed using our Tweet Parser, so tweet data is very easily extractable.


```python
[(tweet.id, tweet.all_text, tweet.hashtags) for tweet in tweets[0:10]]
```




    [('920754829873606657', "@ericmbudd I'm super cute.", []),
     ('920754352716783616', "@RobotPrincessFi that's super cute", []),
     ('920543141614067712', '@RobotPrincessFi https://t.co/z6AioxZkwE', []),
     ('920383435209891841', '@robotprincessfi hi there Fiona', [])]



Let's make a new rule and pass it dates this time. `gen_rule_payload` takes dates of the forms `YYYY-mm-DD` and `YYYYmmDD`.

There is also a convenience function that collects all tweets for a given query and configuration dict, useful in many situations. 


```python
rule = gen_rule_payload("from:jack", from_date="2017-09-01", to_date="2017-10-15")
rule
```




    '{"query":"from:jack","maxResults":500,"toDate":"201710150000","fromDate":"201709010000"}'




```python
from twittersearch import collect_results
```


```python
tweets = collect_results(rule, max_results=500, result_stream_args=search_args)
```

    using username and password for authentication



```python
[(t.created_at_datetime, t.text) for t in tweets[0:10]]
```




    [(datetime.datetime(2017, 10, 14, 22, 57, 23),
      'RT @jenanmoussa: I love to see Palestinians dancing and having fun. Good &amp;positive stories deserve to go viral as well. Watch this: https:/…'),
     (datetime.datetime(2017, 10, 14, 22, 55, 25),
      "RT @chancetherapper: But don't argue with people on twitter about whether policies and laws are racist. Argue with your City Council and… "),
     (datetime.datetime(2017, 10, 14, 21, 30, 26),
      'I saw @solangeknowles perform at Chinati last weekend. It was the most beautiful thing I’ve ever seen. Can’t stop t… https://t.co/WY6SDnr2DU'),
     (datetime.datetime(2017, 10, 14, 19, 17, 33), 'RT @paraga: 1'),
     (datetime.datetime(2017, 10, 14, 17, 30, 1),
      '@monteiro @JohnPaczkowski @cwarzel Never asked for credit Mike'),
     (datetime.datetime(2017, 10, 14, 17, 26),
      '@cwarzel @JohnPaczkowski Will keep everyone updated on the original thread'),
     (datetime.datetime(2017, 10, 14, 17, 3, 38),
      '@davewiner Listened to it all. Doesn’t mean we are going to implement everything! ;)'),
     (datetime.datetime(2017, 10, 14, 17, 0, 56),
      '@davewiner @realDonaldTrump Also not true. It’s a moment in time'),
     (datetime.datetime(2017, 10, 14, 17, 0, 20),
      '@davewiner Come on. This isn’t true. We care. We have to build a business to fund the service'),
     (datetime.datetime(2017, 10, 14, 16, 59, 21),
      '@yaelwrites @JohnPaczkowski @cwarzel @jilliancyork Never said that. We are considering. Need to prioritize.')]


