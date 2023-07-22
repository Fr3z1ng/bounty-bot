from time import sleep
from flask import current_app
from app import db, tg_bot as bot
from app.models import User
from app.bot import messages as msg
from app.bot.handlers.menu import menu


@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)
    if not user:
        referral_id = int(message.text.split()[1]) \
            if len(message.text.split()) > 1 else None
        referral = User.load_user(tg_user_id=referral_id)

        user = User(
            tg_user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            referral=referral)

        db.session.add(user)
        db.session.commit()

    bot.send_message(message.from_user.id, msg.START_MESSAGE.format(
        first_name=message.from_user.first_name,
        bot_name=current_app.config['BOT_NAME']))
    sleep(1)
    menu(message)


@bot.message_handler(commands=['balance'])
def balance(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)
    bot.send_message(
        message.from_user.id,
        msg.BALANCE_MESSAGE.format(amount=user.get_balance()),
        parse_mode='Markdown')
