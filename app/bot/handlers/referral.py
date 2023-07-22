from flask import current_app
from app import tg_bot as bot
from app.models import User
from app.bot import messages as msg


@bot.message_handler(commands=['referral'])
def refer_link(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)

    bot.send_message(
        message.from_user.id,
        msg.REFERRAL_SHARE.format(referred_count=len(user.referred)),
        parse_mode='Markdown')

    bot.send_message(
        message.from_user.id,
        msg.REFERRAL_SHARE_URL.format(
            bot_tag=current_app.config['LINK_TAG'].get('BOT'),
            user_id=message.from_user.id),
        disable_web_page_preview=True)
