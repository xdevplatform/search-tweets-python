"""
Utility functions that are used in various parts of the program.
"""

from functools import reduce
import itertools as it
import types
import codecs
import datetime
import logging
import configparser
try:
    import ujson as json
except ImportError:
    import json


logger = logging.getLogger(__name__)

__all__ = ["take", "partition", "merge_dicts", "write_result_stream",
           "read_configfile"]


def take(n, iterable):
    """Return first n items of the iterable as a list
    
    Args:
        n (int): number of items to return
        iterable (iterable): the object to select
    """
    return it.islice(iterable, n)


def partition(iterable, chunk_size, pad_none=False):
    """adapted from Toolz. Breaks an iterable into n iterables up to the
    certain chunk size, padding with Nones if availble.

    Example:
        >>> from searchtweets.utils import partition
        >>> iter_ = range(10)
        >>> list(partition(iter_, 3))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
        >>> list(partition(iter_, 3, pad_none=True))
        [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, None, None)]
    """
    args = [iter(iterable)] * chunk_size
    if not pad_none:
        return zip(*args)
    else:
        return it.zip_longest(*args)


def merge_dicts(*dicts):
    """
    Helpful function to merge / combine dictionaries and return a new
    dictionary.

    Args:
        dicts (list or Iterable): iterable set of dictionarys for merging.

    Returns:
        dict: dict with all keys from the passed list. Later dictionaries in
        the sequence will override duplicate keys from previous dictionaries.

    Example:
        >>> from searchtweets.utils import merge_dicts
        >>> d1 = {"rule": "something has:geo"}
        >>> d2 = {"maxResults": 1000}
        >>> merge_dicts(*[d1, d2])
        {"maxResults": 1000, "rule": "something has:geo"}
    """
    def _merge_dicts(dict1, dict2):
        return {**dict1, **dict2}

    return reduce(_merge_dicts, dicts)


def write_ndjson(filename, data_iterable, append=False, **kwargs):
    """
    Generator that writes newline-delimited json to a file and returns items
    from an iterable.
    """
    write_mode = "ab" if append else "wb"
    logger.info("writing to file {}".format(filename))
    with codecs.open(filename, write_mode, "utf-8") as outfile:
        for item in data_iterable:
            outfile.write(json.dumps(item) + "\n")
            yield item


def write_result_stream(result_stream, filename_prefix=None,
                        results_per_file=None, **kwargs):
    """
    Wraps a resultstream object to save it to a file. This function will still
    return all data from the result stream as a generator that wraps the
    `write_ndjson` method.

    Args:
        result_stream (ResultStream): the unstarted ResultStream object
        filename_prefix (str or None): the base name for file writing
        results_per_file (int or None): the maximum number of tweets to write
        per file. Defaults to having no max, which means one file. Multiple
        files will be named by datetime, according to
        "<prefix>_YYY-mm-ddTHH_MM_SS.json".

    """
    if isinstance(result_stream, types.GeneratorType):
        stream = result_stream
    else:
        stream = result_stream.stream()

    file_time_formatter = "%Y-%m-%dT%H_%M_%S"
    if filename_prefix is None:
        filename_prefix = "twitter_search_results"

    if results_per_file:
        logger.info("chunking result stream to files with {} tweets per file"
                    .format(results_per_file))
        chunked_stream = partition(stream, results_per_file, pad_none=True)
        for chunk in chunked_stream:
            chunk = filter(lambda x: x is not None, chunk)
            curr_datetime = (datetime.datetime.utcnow()
                             .strftime(file_time_formatter))
            _filename = "{}_{}.json".format(filename_prefix, curr_datetime)
            yield from write_ndjson(_filename, chunk)

    else:
        curr_datetime = (datetime.datetime.utcnow()
                         .strftime(file_time_formatter))
        _filename = "{}.json".format(filename_prefix)
        yield from write_ndjson(_filename, stream)


def read_configfile(filename):
    """
    reads and flattens a configuration file into a single
    dictionary for ease of use.
    """
    config = configparser.ConfigParser()

    with open(filename) as f:
        config.read_file(f)

    config_dict = merge_dicts(*[dict(config[s]) for s in config.sections()])
    return config_dict
