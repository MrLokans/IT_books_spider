#!/bin/bash

export SCRAPY_MAIL_PASS={{password}}
export SCRAPY_MAIL_USER={{username}}
export SCRAPY_SEND_MAIL_TO={{recipient}}
export TELEGRAM_BOT_TOKEN={{telegram_bot_token}}
export TELEGRAM_BOT_CHAT_ID={{telegram_bot_chat_id}}
source {{venv_activate}}
cd {{spider_dir}} && scrapy runspider bookscrawler/spiders/onliner_spider.py >> {{ logs_dir }}/bookscrawler.log
