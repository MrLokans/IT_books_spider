from typing import List, Mapping

import requests


class StaticConfig:
    # ID-s of forums we want to parse
    FORUM_IDS = [
        191,  # PS3 games
        203,  # Books
        237,  # Musical instruments
    ]
    PROGRAMMING_KEYWORDS = [
        'python', 'data intensive',
        'алгоритм', 'algorithm',
        'distributed systems',
        'программировани[еюя]',
        'программист', 'нейронные сети', 'разработка',
        'program', 'programming',
        'искусственный интеллект',
        'artificial intelligence',
        'машинное обучение', 'data science',
        'neural networks', 'machine learning',
    ]
    BOOKS_KEYWORDS = [
        'devops', 'комикс',
    ]
    GAME_KEYWORDS = [
        'ps4', 'playstation 4', 'playstation4',
    ]
    MUSIC_KEYWORDS = [
        'fender', 'squier', 'ltd', 'ibanez',
        'gibson', 'telecaster', 'stratocaster',
        'драм-машина', 'драм машина',
        'бас-гитара', 'бас гитара',
    ]
    SEARCHED_KEYWORDS = (
            PROGRAMMING_KEYWORDS +
            BOOKS_KEYWORDS +
            GAME_KEYWORDS +
            MUSIC_KEYWORDS
    )

    def can_use(self) -> bool:
        return True

    def get_config(self) -> Mapping[int, List[str]]:
        return {
            forum_id: self.SEARCHED_KEYWORDS
            for forum_id in self.FORUM_IDS
        }


class WebSiteBased:
    url_endpoint = 'https://mrlokans.com/api/v1/parse-items/'
    connection_timeout = 2  # seconds

    def can_use(self) -> bool:
        try:
            requests.get(self.url_endpoint, timeout=self.connection_timeout)
            return True
        except Exception:
            return False

    def get_config(self):
        return {

        }