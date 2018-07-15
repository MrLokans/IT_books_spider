Description
-----------

Web crawler of baraholka.onliner.by bulletins website.
What it does is searching for specific text piece encounters
and reporting bulletin urls to you via email or telegram bot.

Running
-------
```bash
# Install libcairo to render PDF apropriately (ubuntu/debian)
sudo apt-get update
sudo apt-get install libpangocairo-1.0-0

# Create virtualenv with virtualenvwrapper
mkvirtualenv onliner_scrapper
# Install requirements
pip install -r requirements.txt

# Set environment variables to get reports
export SCRAPY_MAIL_USER= # emails are sent FROM the given user, gmail only supported for now
export SCRAPY_MAIL_PASS=  # email password
export SCRAPY_SEND_MAIL_TO=  # emails are sent TO the specified user
export TELEGRAM_BOT_TOKEN=  # Telegram Access token
export TELEGRAM_BOT_CHAT_ID=  # identifier of chat to send reports to

# Update list of workds you're looking for in bookscrawler/settings.py:SEARCHED_KEYWORDS list

# launch the spider
scrapy runspider bookscrawler/spiders/onliner_spider.py
```

Deployment
----------
Spider is deployed to the remote linux server via [Fabric](http://www.fabfile.org/), only prerequisites are Python 3.6 and SSH client installed.

In order to deploy the spider you should update config.ini e-mail settings, include your host address in env.hosts variable inside fabfile.py script and launch ```fab deploy```. This will download the repository, install the vurtual environment and launch cron jobs.