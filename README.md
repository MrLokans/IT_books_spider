Description
-----------

Web crawler of books bulletins in baraholka.onliner.by website.

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

Deployment
----------
Spider is deployed to the remote linux server via [Fabric](http://www.fabfile.org/), only prerequisites are Python 3.5 and SSH client installed.

In order to deploy the spider you should update config.ini e-mail settings, include your host address in env.hosts variable inside fabfile.py script and launch ```fab deploy```. This will download the repository, install the vurtual environment and launch cron jobs.