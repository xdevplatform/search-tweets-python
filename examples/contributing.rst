Any contributions should follow the following pattern:

1. Make a feature or bugfix branch, e.g., ``git checkout -b my_new_feature``
2. Make your changes in that branch
3. Ensure you bump the version number in ``searchtweets/_version.py`` to reflect your changes. We use `Semantic Versioning <https://semver.org>`_, so non-breaking enhancements should increment the minor version, e.g., ``1.5.0 -> 1.6.0``, and bugfixes will increment the last version, ``1.6.0 -> 1.6.1``.
4. Create a pull request

After the pull request process is accepted, package maintainers will handle building documentation and distribution to Pypi. 


For reference, distributing to Pypi is accomplished by the following commands, ran from the root directory in the repo:

.. code:: bash

  python setup.py bdist_wheel
  python setup.py sdist
  twine upload dist/*

