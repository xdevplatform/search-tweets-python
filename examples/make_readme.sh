#!/bin/bash
/usr/local/bin/pandoc -i base_readme.rst --to rst | sed 's/ipython3/python/' > ../README.rst
