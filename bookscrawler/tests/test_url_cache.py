import pytest

from bookscrawler.spiders.url_cache import URLStorageStrategy
from bookscrawler.spiders.exceptions import IncorrectURL


def test_basic_url_strategy_compacts_url(url_strategy):
    expected = '19314820'
    bulletin_url = 'http://baraholka.onliner.by/viewtopic.php?t={}'\
        .format(expected)
    assert url_strategy.from_internal_format(bulletin_url)


def test_basic_url_strategy_raises_error_with_incorrect_url(url_strategy):
    incorrect_url = 'http://vk.com'
    with pytest.raises(IncorrectURL):
        url_strategy.to_internal_format(incorrect_url)


def test_basic_url_strategy_builds_full_url_correctly(url_strategy):
    url_piece = '1111000'
    expected_url = 'http://baraholka.onliner.by/viewtopic.php?t={}'\
        .format(url_piece)
    assert url_strategy.from_internal_format(url_piece) == expected_url
