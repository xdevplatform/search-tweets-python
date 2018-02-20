
Credential Handling
===================

The premium and enterprise Search APIs use different authentication
methods and we attempt to provide a seamless way to handle
authentication for all customers. We know credentials can be tricking or
annoying - please read this in its entirety.

Premium clients will require the ``bearer_token`` and ``endpoint``
fields; Enterprise clients require ``username``, ``password``, and
``endpoint``. If you do not specify the ``account_type``, we attempt to
discern the account type and declare a warning about this behavior.

For premium search products, we are using app-only authentication and
the bearer tokens are not delivered with an expiration time. You can
provide either: - your application key and secret (the library will
handle bearer-token authentication) - a bearer token that you get
yourself

Many developers might find providing your application key and secret
more straightforward and letting this library manage your bearer token
generation for you. Please see
`here <https://developer.twitter.com/en/docs/basics/authentication/overview/application-only>`__
for an overview of the premium authentication method.

We support both YAML-file based methods and environment variables for
storing credentials, and provide flexible handling with sensible
defaults.

YAML method
-----------

For premium customers, the simplest credential file should look like
this:

.. code:: yaml


    search_tweets_api:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      consumer_key: <CONSUMER_KEY>
      consumer_secret: <CONSUMER_SECRET>

For enterprise customers, the simplest credential file should look like
this:

.. code:: yaml


    search_tweets_api:
      account_type: enterprise
      endpoint: <FULL_URL_OF_ENDPOINT>
      username: <USERNAME>
      password: <PW>

By default, this library expects this file at
``"~/.twitter_keys.yaml"``, but you can pass the relevant location as
needed, either with the ``--credential-file`` flag for the command-line
app or as demonstrated below in a Python program.

Both above examples require no special command-line arguments or
in-program arguments. The credential parsing methods, unless otherwise
specified, will look for a YAML key called ``search_tweets_api``.

For developers who have multiple endpoints and/or search products, you
can keep all credentials in the same file and specify specific keys to
use. ``--credential-file-key`` specifies this behavior in the command
line app. An example:

.. code:: yaml


    search_tweets_30_day_dev:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      consumer_key: <KEY>
      consumer_secret: <SECRET>
      (optional) bearer_token: <TOKEN>
      
      
    search_tweets_30_day_prod:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      
    search_tweets_fullarchive_dev:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>

    search_tweets_fullarchive_prod:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      

Environment Variables
---------------------

If you want or need to pass credentials via environment variables, you
can set the appropriate variables for your product of the following:

::

    export SEARCHTWEETS_ENDPOINT=
    export SEARCHTWEETS_USERNAME=
    export SEARCHTWEETS_PASSWORD=
    export SEARCHTWEETS_BEARER_TOKEN=
    export SEARCHTWEETS_ACCOUNT_TYPE=
    export SEARCHTWEETS_CONSUMER_KEY=
    export SEARCHTWEETS_CONSUMER_SECRET=

The ``load_credentials`` function will attempt to find these variables
if it cannot load fields from the YAML file, and it will **overwrite any
credentials from the YAML file that are present as environment
variables** if they have been parsed. This behavior can be changed by
setting the ``load_credentials`` parameter ``env_overwrite`` to
``False``.

The following cells demonstrates credential handling in the Python
library.

.. code:: ipython3

    from searchtweets import load_credentials

.. code:: ipython3

    load_credentials(filename="./search_tweets_creds_example.yaml",
                     yaml_key="search_tweets_ent_example",
                     env_overwrite=False)




::

    {'endpoint': '<MY_ENDPOINT>',
     'password': '<MY_PASSWORD>',
     'username': '<MY_USERNAME>'}



.. code:: ipython3

    load_credentials(filename="./search_tweets_creds_example.yaml",
                     yaml_key="search_tweets_premium_example",
                     env_overwrite=False)




::

    {'bearer_token': '<A_VERY_LONG_MAGIC_STRING>',
     'endpoint': 'https://api.twitter.com/1.1/tweets/search/30day/dev.json'}



Environment Variable Overrides
------------------------------

If we set our environment variables, the program will look for them
regardless of a YAML file's validity or existence.

.. code:: ipython3

    import os
    os.environ["SEARCHTWEETS_USERNAME"] = "<ENV_USERNAME>"
    os.environ["SEARCHTWEETS_PASSWORD"] = "<ENV_PW>"
    os.environ["SEARCHTWEETS_ENDPOINT"] = "<https://endpoint>"
    
    load_credentials(filename="nothing_here.yaml", yaml_key="no_key_here")


::

    cannot read file nothing_here.yaml
    Error parsing YAML file; searching for valid environment variables




::

    {'endpoint': '<https://endpoint>',
     'password': '<ENV_PW>',
     'username': '<ENV_USERNAME>'}



Command-line app
----------------

the flags:

-  ``--credential-file <FILENAME>``
-  ``--credential-file-key <KEY>``
-  ``--env-overwrite``

are used to control credential behavior from the command-line app.
