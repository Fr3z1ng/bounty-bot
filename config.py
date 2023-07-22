import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    TWITTER_URL_PREFIX = os.environ.get('TWITTER_URL_PREFIX')
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    FACEBOOK_URL_PRIFIX = os.environ.get('FACEBOOK_URL_PRIFIX')

    WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
    WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT')
    WEBHOOK_URL_BASE = 'https://{WEBHOOK_HOST}:{WEBHOOK_PORT}'.format(
        WEBHOOK_HOST=WEBHOOK_HOST,
        WEBHOOK_PORT=WEBHOOK_PORT)
    WEBHOOK_ROUTE_PATH = os.environ.get('WEBHOOK_ROUTE_PATH')
    WEBHOOK_SLL_SELF_SIGNED = os.environ.get('WEBHOOK_SLL_SELF_SIGNED') in \
        ['true', 'yes', '1']
    WEBHOOK_SSL_CERT = os.environ.get('WEBHOOK_SSL_CERT') or 'cert.pem'
    WEBHOOK_SSL_PRIV = os.environ.get('WEBHOOK_SSL_PRIV') or 'private.key'

    BOT_NAME = os.environ.get('BOT_NAME')
    LINK_TAG = {
        'BOT': os.environ.get('LINK_TAG_BOT'),
        'CHAT_EN': os.environ.get('LINK_TAG_CHAT_EN'),
        'CHAT_BOUNTY': os.environ.get('LINK_TAG_CHAT_BOUNTY'),
        'TWITTER': os.environ.get('LINK_TAG_TWITTER'),
        'FACEBOOK': os.environ.get('LINK_TAG_FACEBOOK')
    }

    REFERRER_DONE_TASKS_COUNT = 1
