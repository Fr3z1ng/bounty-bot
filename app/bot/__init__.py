from flask import Blueprint

bp = Blueprint('bot', __name__)

from app.bot import routes, messages
from app.bot.handlers import main, menu, settings, referral, task, admin
