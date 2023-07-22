import facebook
from app import db, tg_bot as bot
from app.bot import messages as msg
from app.models import User, TwitterConnection, FacebookConnection


@bot.message_handler(commands=['settings'])
def settings(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    bot.send_message(
        message.from_user.id, msg.SETTINGS)


@bot.message_handler(commands=['settings_twitter'])
def set_twitter(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)
    twitter = user.twitter

    if twitter and twitter.authorized:
        bot.send_message(message.from_user.id, msg.TWITTER_EXISTS)
        return

    if not twitter:
        user.twitter = TwitterConnection()

    try:
        user.twitter.setup_oauth()
    except Exception as e:
        print(e)
        bot.send_message(message.from_user.id, msg.TWITTER_OAUTH_ERROR)
        return

    db.session.commit()

    bot.send_message(
        message.from_user.id,
        msg.TWITTER_SETUP.format(link=user.twitter.get_oauth_url()),
        parse_mode='Markdown')


@bot.message_handler(commands=['settings_facebook'])
def set_facebook(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)
    fb = user.facebook

    if fb and fb.authorized:
        fb_api = facebook.GraphAPI(access_token=fb.oauth_token, version='2.7')
        fb_response = fb_api.get_object(id='me', fields='name')

        if fb_response.get('error'):
            if fb_response.type == 'OAuthException':

                bot.send_message(
                    message.from_user.id,
                    msg.FACEBOOK_TOKEN_EXPIRED)
        else:
            bot.send_message(
                message.from_user.id,
                msg.FACEBOOK_EXISTS.format(name=fb_response.get('name')))
            return

    if not user.facebook:
        user.facebook = FacebookConnection()
        db.session.commit()

    bot.send_message(
        message.from_user.id,
        msg.FACEBOOK_SETUP.format(
            link=FacebookConnection.get_oauth_url(user.id)),
        parse_mode='Markdown')
