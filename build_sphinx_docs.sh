#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Error: Please provide a branch name and repo name from which documentation will be built";
  exit 1
fi

BRANCH_NAME=$1
REPO_NAME=$2

echo "Building documentation from $BRANCH_NAME"
echo "checking out gh-pages"
if ! git checkout gh-pages
then
  echo >&2 "checkout of gh-pages branch failed; please ensure you have local changes commited prior to running this script "
  echo "exiting"
  exit 1
fi

pwd
echo "removing current files"
rm -rf ./*.egg-info
git pull origin gh-pages
rm -r ./*.html ./*.js ./_modules ./_sources ./_static
touch .nojekyll
git checkout $BRANCH_NAME docs $REPO_NAME README.rst
# need to do this step because the readme will be overwritten
cp README.rst docs/source/README.rst
mv docs/* .
make html
mv -fv build/html/* ./
rm -r $REPO_NAME docs build Makefile source README.md __pycache__/ dist/
echo "--------------------------------------------------------------------"
echo " docs built; please review these changes and then run the following:"
echo "--------------------------------------------------------------------"
echo git add -A
echo git commit -m \"Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit | grep commit`\"
echo git push origin gh-pages
echo git checkout $BRANCH_NAME
