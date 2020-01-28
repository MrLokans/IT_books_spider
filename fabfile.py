import configparser
import logging
import os

from fabric import task, Connection
from bookscrawler.settings import LOGGING_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()

REPOSITORY_URL = 'https://github.com/MrLokans/IT_books_spider'
PROJECT_DIR = '/opt/IT_books_spider'
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')
CONFIG_FILE = os.path.abspath('config.ini')
CRONTAB_TEMPLATE = """\
#!/bin/bash

export SCRAPY_MAIL_PASS={password}
export SCRAPY_MAIL_USER={username}
export SCRAPY_SEND_MAIL_TO={recipient}
export TELEGRAM_BOT_TOKEN={telegram_bot_token}
export TELEGRAM_BOT_CHAT_ID={telegram_bot_chat_id}
cd {spider_dir} && poetry run scrapy runspider bookscrawler/spiders/onliner_spider.py >> {logs_dir}/bookscrawler.log

"""
CRONTAB_FILE = os.path.join('/etc/cron.daily', 'it-spider')


@task
def create_directories(conn):
    logger.info('Creating required dirs')
    conn.sudo(f'mkdir -p {PROJECT_DIR}')
    conn.sudo(f'chown -R {conn.user}:{conn.user} {PROJECT_DIR}')
    # Logging directory
    conn.sudo(f'mkdir -p {LOGGING_DIR}')
    conn.sudo(f'chown -R {conn.user}:{conn.user} {LOGGING_DIR}')
    # Logging directory
    conn.sudo(f'mkdir -p {LOGS_DIR}')
    conn.sudo(f'chown -R {conn.user}:{conn.user} {LOGS_DIR}')


@task
def checkout_repository(conn):
    with conn.cd(PROJECT_DIR):
        result = conn.run(
            f'git clone {REPOSITORY_URL} {PROJECT_DIR}', warn=True
        )
        if result.failed:
            logger.info("Repository is already cloned. "
                        "Checkout will be attempted "
                        "together with pulling.")
            conn.run('git reset --hard HEAD')
            conn.run('git pull')


@task
def install_dependencies(conn):
    logger.info("Installing depenencies")
    with conn.cd(PROJECT_DIR):
        conn.run(f'poetry run pip install -U pip setuptools')
        conn.run(f'poetry check')
        conn.run(f'poetry install')


@task
def add_crontab_entry(conn):
    logger.info("Reading config")
    config.read(CONFIG_FILE)
    username = config.get('credentials', 'email_username')
    password = config.get('credentials', 'email_password')
    recipient = config.get('credentials', 'recipient')
    telegram_bot_token = config.get('credentials', 'telegram_bot_token')
    telegram_bot_chat_id = config.get('credentials', 'telegram_bot_chat_id')

    if not all([username, password, recipient, telegram_bot_token, telegram_bot_chat_id]):
        logger.error("Some of the settings is not set.")
        raise ValueError("Some of the settings is not set.")

    logger.info("Creating crontab entry")
    context = {
        'password': password,
        'username': username,
        'recipient': recipient,
        'telegram_bot_token': telegram_bot_token,
        'telegram_bot_chat_id': telegram_bot_chat_id,
        'spider_dir': PROJECT_DIR,
        'logs_dir': LOGS_DIR,
    }
    crontab_contents = CRONTAB_TEMPLATE.format(**context)
    with open('/tmp/fab-crontab', 'w') as temp_f:
        temp_f.write(crontab_contents)
    conn.put('/tmp/fab-crontab', CRONTAB_FILE)
    conn.run(f'cat {CRONTAB_FILE}')
    conn.sudo(f'chmod +x {CRONTAB_FILE}')


@task
def run_spider_manually(conn):
    with conn.cd(PROJECT_DIR):
        conn.run('poetry run scrapy runspider bookscrawler/spiders/onliner_spider.py')


@task
def setup_python_alias(conn):
    try:
        conn.sudo('ln -s /usr/bin/python3 /usr/bin/python')
    except Exception:
        pass


@task
def install_poetry(conn):
    poetry_url = 'https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py'
    python_binary = 'python3'
    conn.sudo('apt-get install -y python3-venv')
    conn.run(
        f'curl -sSL {poetry_url} | {python_binary}'
    )
    # Manually modify /etc/environment to include absolute path to poetry
    conn.run('poetry -V')



@task
def deploy(conn):
    setup_python_alias(conn)
    create_directories(conn)
    checkout_repository(conn)
    install_poetry(conn)
    install_dependencies(conn)
    add_crontab_entry(conn)