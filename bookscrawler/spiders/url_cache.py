"""
Here we implement caching class for our parsed URLs.
We can not use middleware because we yield requests
in our spider and the request is not processed by
middleware level
"""


class URLFileCache(object):
    def __init__(self, storage_file: str):
        self.storage_file = storage_file

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
