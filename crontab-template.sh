#!/bin/sh

export SCRAPY_MAIL_PASS={{password}}
export SCRAPY_MAIL_USER={{username}}
export SCRAPY_SEND_MAIL_TO={{recipient}}
source {{venv_activate}}
cd {{spider_dir}} && scrapy runspider bookscrawler/spiders/onliner_spider.py