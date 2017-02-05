import pytest

from bookscrawler.spiders.url_cache import URLStorageStrategy


@pytest.fixture
def url_strategy():
    return URLStorageStrategy()
