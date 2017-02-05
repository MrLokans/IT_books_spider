"""
Here we implement caching class for our parsed URLs.
We can not use middleware because we yield requests
in our spider and the request is not processed by
middleware level
"""


class URLStorageStrategy(object):
    """
    In order to optimize storage space we remove
    redundant URL parts
    """

    def to_internal_format(self, url: str) -> str:
        """
        Transform the given URL into compact internal representation
        """

    def from_internal_format(self, shorten_url: str) -> str:
        """
        Reconstruct full URL from internal representation
        """


class URLFileCache(object):
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self.__url_set = set()

    def load_cache(self) -> None:
        """
        Attempts to read cache data from the file
        """

    def has_url(self, url: str) -> bool:
        """
        Checks whether we have already visited the specified URL
        """

    def add_url(self, url: str) -> None:
        """
        Add specified URL to cache
        """
