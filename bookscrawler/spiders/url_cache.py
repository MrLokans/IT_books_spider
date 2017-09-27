"""
Here we implement caching class for our parsed URLs.
We can not use middleware because we yield requests
in our spider and the request is not processed by
middleware level
"""
import logging
import os
import pickle
import re


from bookscrawler.spiders.exceptions import IncorrectURL


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class URLStorageStrategy(object):
    """
    In order to optimize storage space we remove
    redundant URL parts
    """

    TOPIC_URL = 'https://baraholka.onliner.by/viewtopic.php\?t={}'

    URL_REGEX = re.compile(
        r'(http|https)://baraholka\.onliner\.by/viewtopic\.php\?t=(?P<topic_id>\d+)'
    )

    def to_internal_format(self, url: str) -> str:
        """
        Transform the given URL into compact internal representation
        """
        match = self.URL_REGEX.match(url)
        if not match:
            raise IncorrectURL('Incorrect URL: {}'.format(url))
        return match.groupdict()['topic_id']

    def from_internal_format(self, topic_id: str) -> str:
        """
        Reconstruct full URL from internal representation
        """
        return self.TOPIC_URL + topic_id


class URLFileCache(object):
    def __init__(self, storage_file: str, storage_strategy):
        self.storage_file = storage_file
        self.storage_strategy = storage_strategy
        self.__url_set = set()

    def load_cache(self) -> None:
        """
        Attempts to read cache data from the file
        """
        cache_exists = os.path.exists(self.storage_file)
        cache_is_file = os.path.isfile(self.storage_file)
        if not cache_exists or not cache_is_file:
            logger.info("Cache file does not exist.")
            return
        logger.info("Reading cache file.")
        with open(self.storage_file, 'rb') as f:
            self.__url_set = pickle.load(f)

    def persist_cache(self) -> None:
        """
        Dumps internal cache to disk in order to
        persist between calls
        """
        logger.info("Writing URL cache.")
        with open(self.storage_file, 'wb') as f:
            pickle.dump(self.__url_set, f)

    def has_url(self, url: str) -> bool:
        """
        Checks whether we have already visited the specified URL
        """
        url = self.storage_strategy.to_internal_format(url)
        return url in self.__url_set

    def add_url(self, url: str) -> None:
        """
        Add specified URL to cache
        """
        url = self.storage_strategy.to_internal_format(url)
        self.__url_set.add(url)
