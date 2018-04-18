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

How to build the documentation:

Building the documentation requires a few Sphinx packages to build the webpages:

.. code:: bash
 
  pip install sphinx
  pip install sphinx_bootstrap_theme
  pip install sphinxcontrib-napoleon

Then (once your changes are committed to master) you should be able to run the documentation-generating bash script and follow the instructions:

.. code:: bash
  
  bash build_sphinx_docs.sh master searchtweets

Note that this README is also generated, and so after any README changes you'll need to re-build the README (you need pandoc version 2.1+ for this) and commit the result:

.. code:: bash 
  
  bash make_readme.sh

