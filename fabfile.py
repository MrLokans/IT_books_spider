import configparser
import logging
import os

from fabric.api import (
    cd,
    run,
    settings,
    sudo,
)
from fabric.contrib.files import upload_template
from fabric.state import env

from bookscrawler.settings import LOGGING_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()

REPOSITORY_URL = 'https://github.com/MrLokans/IT_books_spider'
PROJECT_DIR = '/opt/IT_books_spider'
VIRTUALENV_DIR = '/opt/it_books_venv'
VIRTUALENV_PYTHON = os.path.join(VIRTUALENV_DIR, 'bin/python3')
VIRTUALENV_PIP = os.path.join(VIRTUALENV_DIR, 'bin/pip')
VIRTUALENV_ACTIVATE = os.path.join(VIRTUALENV_DIR, 'bin/activate')
REQUIREMENTS_PATH = os.path.join(PROJECT_DIR, 'requirements.txt')
CONFIG_FILE = os.path.abspath('config.ini')
CRONTAB_TEMPLATE_NAME = 'crontab-template.sh'
CRONTAB_FILE = os.path.join('/etc/cron.daily', 'it-spider')


env.hosts = []


def create_directories():
    sudo('mkdir -p {}'.format(PROJECT_DIR))
    sudo('chown -R {user}:{user} {dir}'.format(user=env.user,
                                               dir=PROJECT_DIR))
    # Logging directory
    sudo('mkdir -p {}'.format(LOGGING_DIR))
    sudo('chown -R {user}:{user} {dir}'.format(user=env.user,
                                               dir=LOGGING_DIR))


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
        'venv_activate': VIRTUALENV_ACTIVATE
    }
    upload_template(CRONTAB_TEMPLATE_NAME, CRONTAB_FILE,
                    context=context,
                    use_sudo=True,
                    use_jinja=True,
                    backup=False)
    sudo('chmod +x {file}'.format(file=CRONTAB_FILE))


def deploy():
    create_directories()
    checkout_repository()
    create_virtualenv()
    install_dependencies()
    add_crontab_entry()
