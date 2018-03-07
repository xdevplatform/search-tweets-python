from setuptools import setup, find_packages

setup(name='searchtweets',
      description="Wrapper for Twitter's Premium and Enterprise search APIs",
      url='https://github.com/twitterdev/search-tweets-python',
      author='Fiona Pigott, Jeff Kolb, Josh Montague, Aaron Gonzales',
      long_description=open('README.rst', 'r', encoding="utf-8").read(),
      author_email='agonzales@twitter.com',
      license='MIT',
      version='1.3.1',
      python_requires='>=3.3',
      install_requires=["requests", "tweet_parser", "pyyaml"],
      packages=find_packages(),
      scripts=["tools/search_tweets.py"],
     )
