
Credential Handling
===================

The premium and enterprise Search APIs use different authentication
methods and we attempt to provide a seamless way to handle
authentication for all customers. We support both YAML-file based
methods and environment variables for access.

A YAML credential file should look like this:

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

Our credential reader will look for this file at
``"~/.twitter_keys.yaml"``, but you can pass the relevant location as
needed. You can also specify a different key in the yaml file, which can
be useful if you have different endpoints, e.g., ``dev``, ``test``,
``prod``, etc. The file might look like this:

.. code:: .yaml


    search_tweets_dev:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      
    search_tweets_prod:
      account_type: premium
      endpoint: <FULL_URL_OF_ENDPOINT>
      bearer_token: <TOKEN>
      

If you want or need to pass credentials via environment variables, you
can set the appropriate variables of the following:

::

    export SEARCHTWEETS_ENDPOINT=
    export SEARCHTWEETS_USERNAME=
    export SEARCHTWEETS_PASSWORD=
    export SEARCHTWEETS_BEARER_TOKEN=
    export SEARCHTWEETS_ACCOUNT_TYPE=

The ``load_credentials`` function will attempt to find these variables
if it cannot load fields from the yaml file, and it will **overwrite any
found credentials from the YAML file** if they have been parsed. This
behavior can be changed by setting the ``load_credentials`` parameter
``env_overwrite`` to ``False``.

The following cells demonstrates credential handling, both in the
command line app and Python library.

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
    os.environ["SEARCHTWEETS_USERNAME"] = "ENV_USERNAME"
    os.environ["SEARCHTWEETS_PASSWORD"] = "ENV_PW"
    os.environ["SEARCHTWEETS_ENDPOINT"] = "https://endpoint"
    
    load_credentials(filename="nothing", yaml_key="no_key_here")


::

    cannot read file nothing
    Error parsing YAML file; searching for valid environment variables




::

    {'endpoint': 'https://endpoint',
     'password': 'ENV_PW',
     'username': 'ENV_USERNAME'}


