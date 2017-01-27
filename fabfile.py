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
VIRTUALENV_PYTHON = os.path.join(VIRTUALENV_DIR, 'bin/python3')
VIRTUALENV_PIP = os.path.join(VIRTUALENV_DIR, 'bin/pip')
REQUIREMENTS_PATH = os.path.join(PROJECT_DIR, 'requirements.txt')
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
    sudo('python3 -m virtualenv {path}'
         .format(path=VIRTUALENV_DIR))


def install_dependencies():
    logger.info("Installing depenencies")
    sudo('{pip} install -r {deps_file}'
        .format(pip=VIRTUALENV_PIP,
                deps_file=REQUIREMENTS_PATH))


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
    # add_crontab_entry()
