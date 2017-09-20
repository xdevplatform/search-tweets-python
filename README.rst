Python Twitter Search API
=========================


This library serves as a python interface to the Twitter/GNIP Search API. It allows use both from a command-line utility and from with a python program. It comes with tools for assisting in dynamic generation of search rules and for parsing tweets.




Command line examples
=====================

Stream json results to stdout without saving:
:: 
  python twitter_search_api.py \
  --user-name <USERNAME> \
  --account-name <ACCOUNT> \
  --password <PW> \
  --stream-endpoint ogformat.json \
  --search-api fullarchive \
  --max-tweets 1000 \
  --filter-rule "beyonce has:geo" \
  --print-stream
::

Stream json results to stdout and save to a file:
:: 
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
::

Save to file without output:
:: 
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
::




