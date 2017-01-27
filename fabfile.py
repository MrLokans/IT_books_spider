import os
import logging
import ConfigParser

from fabric.api import (
    abort,
    cd,
    local,
    lcd,
    put,
    run,
    settings,
    sudo
)
from fabric.state import env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = ConfigParser.ConfigParser()

REPOSITORY_URL = 'https://github.com/MrLokans/IT_books_spider'
PROJECT_DIR = '/opt/IT_books_spider'
VIRTUALENV_DIR = '/opt/it_books_venv'
CONFIG_FILE = os.path.abspath('config.ini')


env.hosts = []


def create_directories():
    sudo('mkdir -p {}'.format(PROJECT_DIR))
    sudo('chown -R {user}:{user} {dir}'.format(user=env.user,
                                               dir=PROJECT_DIR))


def checkout_repository():
    with cd(PROJECT_DIR):
        with settings(warn_only=True):
            result = run('git clone {url} {path}'.format(url=REPOSITORY_URL,
                                                         path=PROJECT_DIR))
            if result.failed:
                logger.info("Repository is already cloned. "
                            "Checkout will be attempted "
                            "together with pulling.")
                run('git reset --hard HEAD')
                run('git pull')


def create_virtualenv():
    logger.info("Creating virtual environemnt.")


def install_dependencies():
    logger.info("Installing depenencies")


def add_crontab_entry():
    config.read(CONFIG_FILE)
    username = config.get('credentials', 'email_username')
    password = config.get('credentials', 'email_password')
    recipient = config.get('credentials', 'recipient')
    logger.info("Creating crontab entry")


def deploy():
    create_directories()
    checkout_repository()
    create_virtualenv()
    install_dependencies()
    add_crontab_entry()
