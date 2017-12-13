from setuptools import setup, find_packages

setup(name='twittersearch',
      description="Wrapper for Twitter's Premium and Enterprise search APIs",
      url='https://github.com/twitterdev/twitter_search_api',
      author='Fiona Pigott, Jeff Kolb, Josh Montague, Aaron Gonzales',
      long_description=open('README.rst', 'r').read(),
      author_email='agonzales@twitter.com',
      license='MIT',
      version='0.1.2',
      install_requires=["requests", "tweet_parser", "yaml"],
      packages=find_packages(),
      scripts=["tools/twitter_search.py"],
      )
