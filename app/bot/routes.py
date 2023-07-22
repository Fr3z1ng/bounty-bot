from flask import request, abort, redirect, current_app
from datetime import datetime, timedelta
import oauth2
import urllib.parse
import telebot
import facebook
import twitter
from app import db, tg_bot as bot
from app.bot import bp, messages as msg
from app.models import User, TwitterConnection, FacebookConnection


@bp.route('/')
def index():
    return 'hey!'


@bp.route('/twitter', methods=['GET'])
def twitter_auth():
    parameters = request.args
    user_oauth_token = parameters.get('oauth_token')
    user_oauth_verifier = parameters.get('oauth_verifier')

    if not user_oauth_token or not user_oauth_verifier:
        abort(404)

    tw = TwitterConnection.query.filter_by(
        oauth_token=user_oauth_token).first()

    if not tw:
        return msg.TWITTER_OAUTH_NOT_FOUND

    user = tw.user

    token = oauth2.Token(
        tw.oauth_token,
        tw.oauth_secret_token)

    oauth_consumer = oauth2.Consumer(
        key=current_app.config['TWITTER_CONSUMER_KEY'],
        secret=current_app.config['TWITTER_CONSUMER_SECRET'])
    client = oauth2.Client(oauth_consumer, token)

    try:
        res, content = client.request(
            'https://api.twitter.com/oauth/access_token?%s'
            % urllib.parse.urlencode({
                'oauth_verifier': user_oauth_verifier
            }),
            method='POST')
    except Exception as e:
        bot.send_message(
            tw.user.tg_user_id,
            msg.TWITTER_OAUTH_NOT_SUCCESS)

        return redirect(msg.BOUNTY_BOT_URL.format(
            bot_tag=current_app.config['LINK_TAG'].get('BOT')))

    if res['status'] != '200':
        bot.send_message(
            tw.user.tg_user_id,
            msg.TWITTER_OAUTH_NOT_SUCCESS)

        return redirect(msg.BOUNTY_BOT_URL.format(
            bot_tag=current_app.config['LINK_TAG'].get('BOT')))

    access_token = dict(urllib.parse.parse_qsl(content.decode('utf-8')))

    twapi = twitter.Api(
        consumer_key=current_app.config['TWITTER_CONSUMER_KEY'],
        consumer_secret=current_app.config['TWITTER_CONSUMER_SECRET'],
        access_token_key=access_token['oauth_token'],
        access_token_secret=access_token['oauth_token_secret'])

    try:
        tw_user = twapi.VerifyCredentials(skip_status=True)
    except Exception as e:
        bot.send_message(
            tw.user.tg_user_id,
            msg.TWITTER_OAUTH_NOT_SUCCESS)

        return redirect(msg.BOUNTY_BOT_URL.format(
            bot_tag=current_app.config['LINK_TAG'].get('BOT')))

    if not TwitterConnection.find_user(tw_user.id_str):
        user = tw.user
        tw.oauth_token = access_token['oauth_token']
        tw.oauth_secret_token = access_token['oauth_token_secret']
        tw.authorized = True
        tw.authorized_timestamp = datetime.utcnow()
        tw.twitter_user_id = tw_user.id_str
        db.session.commit()

        bot.send_message(
            user.tg_user_id,
            msg.TWITTER_CONNECTED.format(name=tw_user.name))
    else:
        bot.send_message(
            tw.user.tg_user_id,
            msg.TWITTER_DUPLICATE_USER)

    return redirect(msg.BOUNTY_BOT_URL.format(
        bot_tag=current_app.config['LINK_TAG'].get('BOT')))


@bp.route('/facebook', methods=['GET'])
def facebook_auth():
    parameters = request.args
    user_id = parameters.get('state')
    code = parameters.get('code')

    if not user_id or not code:
        abort(404)
        return

    try:
        user_id = int(user_id)
    except Exception as e:
        abort(404)
        return

    user = User.load_user(user_id=user_id)
    if not user:
        return msg.FACEBOOK_USER_NOT_FOUND

    try:
        fb_api = facebook.GraphAPI(
            access_token=current_app.config['FACEBOOK_APP_SECRET'],
            version='2.7')
        result = fb_api.get_object(
            id='oauth/access_token',
            client_id=current_app.config['FACEBOOK_APP_ID'],
            client_secret=current_app.config['FACEBOOK_APP_SECRET'],
            redirect_uri=current_app.config['WEBHOOK_URL_BASE']
            + current_app.config['FACEBOOK_URL_PRIFIX'],
            code=code)
    except Exception as e:
        print(e)
        user.send_message(
            user.tg_user_id,
            msg.FACEBOOK_OAUTH_NOT_SUCCESS)

    access_token = result.get('access_token')
    token_type = result.get('token_type')
    expires_in = result.get('expires_in')

    if not access_token or not token_type or not expires_in:
        bot.send_message(
            user.tg_user_id,
            msg.FACEBOOK_OAUTH_NOT_SUCCESS)
    else:
        fb_api = facebook.GraphAPI(
            access_token=access_token,
            version='2.7')

        try:
            fb_name = fb_api.get_object(id='me', fields='name')
        except Exception as e:
            print(e)
            bot.send_message(
                user.tg_user_id,
                msg.FACEBOOK_OAUTH_ERROR)
            return

        if not FacebookConnection.find_user(fb_name['id']):
            user.facebook.oauth_token = access_token
            user.facebook.token_type = token_type
            user.facebook.expires_in = datetime.utcnow() \
                + timedelta(0, expires_in)

            user.facebook.authorized = True
            user.facebook.authorized_timestamp = datetime.utcnow()
            user.facebook.facebook_user_id = fb_name['id']
            db.session.commit()

            bot.send_message(
                user.tg_user_id,
                msg.FACEBOOK_CONNECTED.format(name=fb_name['name']))
        else:
            bot.send_message(
                user.tg_user_id,
                msg.FACEBOOK_DUPLICATE_USER)

    return redirect(msg.BOUNTY_BOT_URL.format(
        bot_tag=current_app.config['LINK_TAG'].get('BOT')))


@bp.route('/bot/<webhook_path>', methods=['POST'])
def webhook(webhook_path):
    if webhook_path != current_app.config['WEBHOOK_ROUTE_PATH']:
        abort(404)

    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)
