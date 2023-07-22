from app import tg_bot as bot
from app.models import User
from app.bot import messages as msg


@bot.message_handler(commands=['menu'])
def menu(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    bot.send_message(
        message.from_user.id, msg.MENU, parse_mode='html')

    user = User.load_user(tg_user_id=message.from_user.id)
    if user and user.employer:
        bot.send_message(
            message.from_user.id, msg.EMPLOYER_MENU)
