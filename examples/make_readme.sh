#!/bin/bash

jupyter-nbconvert ./api_example.ipynb --to rst
jupyter-nbconvert ./credential_handling.ipynb --to rst

sed 's/.*parsed-literal.*/::/' api_example.rst > _api_example.rst
sed 's/.*parsed-literal.*/::/' credential_handling.rst > _credential_handling.rst

mv _api_example.rst api_example.rst
mv _credential_handling.rst credential_handling.rst

$(brew --prefix)/bin/pandoc -i base_readme.rst --to rst | sed 's/ipython3/python/' > ../README.rst
#| sed 's/.*parsed-literal.*/::/' 
