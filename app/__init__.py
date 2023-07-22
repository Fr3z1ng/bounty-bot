from raven.contrib.flask import Sentry
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import telebot
import logging
from time import sleep
from config import Config


db = SQLAlchemy()
migrate = Migrate()
tg_bot = telebot.TeleBot.__new__(telebot.TeleBot)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
sentry = Sentry()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    sentry.init_app(app)

    tg_bot.__init__(app.config['TELEGRAM_TOKEN'], threaded=False)

    from app.bot import bp as bot_bp
    app.register_blueprint(bot_bp)

    if app.config['DEBUG']:
        tg_bot.remove_webhook()
        sleep(1)
        # Set webhook

        if app.config['WEBHOOK_SLL_SELF_SIGNED']:
            tg_bot.set_webhook(
                url=app.config['WEBHOOK_URL_BASE']
                + '/bot/' + app.config['WEBHOOK_ROUTE_PATH'],
                certificate=open(app.config['WEBHOOK_SSL_CERT'], 'r'))
        else:
            tg_bot.set_webhook(
                url=app.config['WEBHOOK_URL_BASE']
                + '/bot/' + app.config['WEBHOOK_ROUTE_PATH'])

    return app


from app import models
