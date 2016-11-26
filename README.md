Description
-----------

Web crawler of books bulletins in baraholka.onliner.by

Running
-------
```bash
# Create virtualenv with virtualenvwrapper
mkvirtualenv onliner_scrapper
# Install requirements
pip install -r requirements.txt
# Set environment variables to get PDF reports

export SCRAPY_MAIL_USER= # emails are sent FROM the given user, gmail only supported for now
export SCRAPY_MAIL_PASS=  # email password
export export SCRAPY_SEND_MAIL_TO=  # emails are sent TO the specified user

# launch the spider
scrapy runspider bookscrawler/spiders/onliner_spider.py
```