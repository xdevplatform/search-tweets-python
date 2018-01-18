#!/bin/bash

jupyter-nbconvert ./api_example.ipynb --to rst
jupyter-nbconvert ./credential_handling.ipynb --to rst


/usr/local/bin/pandoc -i base_readme.rst --to rst | sed 's/ipython3/python/' | sed 's/.*parsed-literal.*/::/' > ../README.rst
