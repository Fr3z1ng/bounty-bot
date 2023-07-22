from flask import current_app
import telebot
import twitter
import facebook
from app import db, tg_bot as bot
from app.models import User, Task
from app.bot import messages as msg


def set_keyboard(callback_text=None, callback_data=None, check_data=None):
    keyboard = telebot.types.InlineKeyboardMarkup()

    if callback_data and not check_data:
        callback_button = telebot.types.InlineKeyboardButton(
            text=callback_text,
            callback_data=callback_data)
        keyboard.add(callback_button)

    elif check_data and not callback_data:
        check_execution = telebot.types.InlineKeyboardButton(
            text=msg.TASK_ELEMENT_BUTTON_CHECK,
            callback_data=check_data)

    elif callback_data and check_data:
        callback_button = telebot.types.InlineKeyboardButton(
            text=callback_text,
            callback_data=callback_data)

        check_execution = telebot.types.InlineKeyboardButton(
            text=msg.TASK_ELEMENT_BUTTON_CHECK,
            callback_data=check_data)

        keyboard.add(callback_button, check_execution)

    return keyboard


def load_task(task_id):
    try:
        task_id = int(task_id)
    except Exception as e:
        print(task_id, e)
        return None

    task = Task.query.filter_by(id=task_id).first()
    return task


def create_message_header(user, task, mode):
    if task.action.name == 'REFERRAL':
        message_text = msg.TASK_NAME[task.action.name]['LESS']
    else:
        message_text = msg.TASK_NAME[
            task.action.name][task.action.social_network.name]['LESS']

    if mode == 'MORE':
        message_text += '\n\n'

        instructions = []
        if task.action.name == 'SUBSCRIPTION':
            if task.action.social_network.name == 'TWITTER':
                tw = user.twitter

                if not tw or not tw.authorized:
                    instructions.append(msg.TWITTER_NOT_EXISTS)

                instructions.append(
                    msg.TASK_NAME[
                        task.action.name][
                        task.action.social_network.name]['MORE'].format(
                            tag=current_app.config['LINK_TAG']
                            .get(task.action.social_network.name)))
        elif task.action.name == 'REFERRAL':
            instructions = [
                msg.TASK_NAME['REFERRAL']['MORE'].format(
                    tasks_count=current_app.config['REFERRER_DONE_TASKS_COUNT']
                )]
        elif task.action.name == 'SHARE':
            if task.action.social_network.name == 'TWITTER':
                tw = user.twitter

                if not tw or not tw.authorized:
                    instructions.append(msg.TWITTER_NOT_EXISTS)

            if task.action.social_network.name == 'FACEBOOK':
                fb = user.facebook

                if not fb or not fb.authorized:
                    instructions.append(msg.FACEBOOK_NOT_EXISTS)

            instructions.append(
                msg.TASK_NAME[
                    task.action.name][
                    task.action.social_network.name]['MORE'].format(
                        post_id=task.post_id))

        elif task.action.name == 'LIKE':
            if task.action.social_network.name == 'TWITTER':
                tw = user.twitter

                if not tw or not tw.authorized:
                    instructions.append(msg.TWITTER_NOT_EXISTS)

            instructions.append(
                msg.TASK_NAME[
                    task.action.name][
                    task.action.social_network.name]['MORE'].format(
                        post_id=task.post_id))

        message_instructions = ''
        for i in range(0, len(instructions)):
            message_instructions += f'{i + 1}. ' + instructions[i] + '\n'
        message_text += message_instructions

    message_header = msg.TASK_ELEMENT.format(
        action=message_text,
        reward=task.reward)
    return message_header


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and call.data.split(':')[0] == 'TASK_LIST')
def callback_task_list(call):
    user = User.load_user(tg_user_id=call.from_user.id)
    if not user:
        return

    offset = int(call.data.split(':')[1]) \
        if len(call.data.split(':')[0]) > 1 \
        else 1
    tasks = user.get_list(offset)
    task_list = tasks.items

    if len(task_list) == 0:
        bot.send_message(
            call.from_user.id,
            msg.TASK_NO_ELEMENTS)
        return

    bot.send_message(
        call.from_user.id,
        msg.TASK_LIST)

    for task in task_list:
        keyboard = telebot.types.InlineKeyboardMarkup()
        buttons = []
        buttons.append(telebot.types.InlineKeyboardButton(
            text=msg.TASK_ELEMENT_BUTTON_MORE_INFO,
            callback_data=f'TASK:{task.id}:MORE_INFO'))

        if task.action.name != 'REFERRAL':
            buttons.append(telebot.types.InlineKeyboardButton(
                text=msg.TASK_ELEMENT_BUTTON_CHECK,
                callback_data=f'{task.action.name}:{task.id}:CHECK'))

        keyboard.add(*buttons)

        message_response = create_message_header(user, task, 'LESS')

        bot.send_message(
            call.from_user.id,
            message_response,
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=keyboard)

    keyboard = telebot.types.InlineKeyboardMarkup()
    buttons = []
    if tasks.has_next:
        buttons.append(telebot.types.InlineKeyboardButton(
            text='Next',
            callback_data=f'TASK_LIST:{tasks.next_num}'))

    if len(buttons) > 0:
        keyboard.add(*buttons)

        bot.send_message(
            call.from_user.id,
            f'Current page: {offset}',
            reply_markup=keyboard)


@bot.message_handler(commands=['tasks'])
def tasks(message):
    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    user = User.load_user(tg_user_id=message.from_user.id)
    offset = 1
    tasks = user.get_list(offset)
    task_list = tasks.items
    print(tasks.items)
    print(tasks)

    if len(task_list) == 0:
        bot.send_message(
            message.from_user.id,
            msg.TASK_NO_ELEMENTS)
        return

    bot.send_message(
        message.from_user.id,
        msg.TASK_LIST)

    for task in task_list:
        keyboard = telebot.types.InlineKeyboardMarkup()
        buttons = []
        buttons.append(telebot.types.InlineKeyboardButton(
            text=msg.TASK_ELEMENT_BUTTON_MORE_INFO,
            callback_data=f'TASK:{task.id}:MORE_INFO'))

        if task.action.name != 'REFERRAL':
            buttons.append(telebot.types.InlineKeyboardButton(
                text=msg.TASK_ELEMENT_BUTTON_CHECK,
                callback_data=f'{task.action.name}:{task.id}:CHECK'))

        keyboard.add(*buttons)

        message_response = create_message_header(user, task, 'LESS')

        bot.send_message(
            message.from_user.id,
            message_response,
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=keyboard)

    keyboard = telebot.types.InlineKeyboardMarkup()
    buttons = []
    if tasks.has_next:
        buttons.append(telebot.types.InlineKeyboardButton(
            text='Next',
            callback_data=f'TASK_LIST:{tasks.next_num}'))

    if len(buttons) > 0:
        keyboard.add(*buttons)

        bot.send_message(
            message.from_user.id,
            f'Current page: {offset}',
            reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and len(call.data.split(':')) == 3
        and call.data.split(':')[0] == 'TASK'
        and call.data.split(':')[2] == 'LESS_INFO')
def callback_less_info(call):
    task = load_task(call.data.split(':')[1])
    if not task:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=msg.TASK_CANNOT_LOAD)
        return

    message_header = create_message_header(None, task, 'LESS')

    keyboard = set_keyboard(
        callback_text=msg.TASK_ELEMENT_BUTTON_MORE_INFO,
        callback_data=f'TASK:{task.id}:MORE_INFO',

        check_data=f'{task.action.name}:{task.id}:CHECK'
        if task.action.name != 'REFERRAL' else None)

    try:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=message_header,
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=keyboard)
    except Exception as e:
        pass

    return


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and len(call.data.split(':')) == 3
        and call.data.split(':')[0] == 'TASK'
        and call.data.split(':')[2] == 'MORE_INFO')
def callback_more_info(call):
    user = User.load_user(tg_user_id=call.from_user.id)

    task = load_task(call.data.split(':')[1])
    if not task:
        bot.answer_callback_query(
            callback_query_id=call.id,
            show_alert=False,
            text=msg.TASK_CANNOT_LOAD)
        return

    message_response = create_message_header(user, task, 'MORE')

    keyboard = set_keyboard(
        callback_text=msg.TASK_ELEMENT_BUTTON_LESS_INFO,
        callback_data=f'TASK:{task.id}:LESS_INFO',

        check_data=f'{task.action.name}:{task.id}:CHECK'
        if task.action.name != 'REFERRAL' else None)

    try:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=message_response,
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=keyboard)
    except Exception as e:
        pass

    return


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and call.data.split(':')[0] == 'SUBSCRIPTION'
        and call.data.split(':')[2] == 'CHECK')
def subscription_check(call):
    user = User.load_user(tg_user_id=call.from_user.id)

    try:
        task_id = int(call.data.split(':')[1])
    except Exception as e:
        print(e)
        return

    try:
        task = Task.query.filter_by(id=task_id).first()
    except Exception as e:
        print(e)
        return

    if not user.can_complete_task(task):
        try:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text=msg.TASK_ELEMENT_DONE,
                disable_web_page_preview=True)
        except Exception as e:
            pass

        return

    if task.action.social_network.name == 'TWITTER':
        tw = user.twitter

        if not tw or not tw.authorized:
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_NOT_EXISTS)
            return

        twapi = twitter.Api(
            consumer_key=current_app.config['TWITTER_CONSUMER_KEY'],
            consumer_secret=current_app.config['TWITTER_CONSUMER_SECRET'],
            access_token_key=tw.oauth_token,
            access_token_secret=tw.oauth_secret_token)

        try:
            tw_user = twapi.GetUser(
                screen_name=current_app.config['LINK_TAG'].get('TWITTER'))
        except Exception as e:
            print(e)
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_OAUTH_NOT_SUCCESS)
            return

        if tw_user.following:
            user.complete_task(task)
            db.session.commit()

            try:
                bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=msg.TASK_ELEMENT_DONE,
                    disable_web_page_preview=True)

                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=True,
                    text=msg.PAYMENT_GOT_NEW.format(
                        username=user.first_name,
                        amount=task.reward))

            except Exception as e:
                pass

        else:
            try:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=False,
                    text=msg.TASK_NAME['SUBSCRIPTION']['TWITTER']['NOT_FOUND'])
            except Exception as e:
                return


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and call.data.split(':')[0] == 'SHARE'
        and call.data.split(':')[2] == 'CHECK')
def share_check(call):
    user = User.load_user(tg_user_id=call.from_user.id)

    try:
        task_id = int(call.data.split(':')[1])
    except Exception as e:
        print(e)
        return

    try:
        task = Task.query.filter_by(id=task_id).first()
    except Exception as e:
        print(e)
        return

    if not user.can_complete_task(task):
        try:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                text=msg.TASK_ELEMENT_DONE,
                disable_web_page_preview=True)
        except Exception as e:
            pass

        return

    if task.action.social_network.name == 'TWITTER':
        tw = user.twitter

        if not tw or not tw.authorized:
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_NOT_EXISTS)
            return

        twapi = twitter.Api(
            consumer_key=current_app.config['TWITTER_CONSUMER_KEY'],
            consumer_secret=current_app.config['TWITTER_CONSUMER_SECRET'],
            access_token_key=tw.oauth_token,
            access_token_secret=tw.oauth_secret_token)

        try:
            tw_user = twapi.GetStatus(
                status_id=task.post_id,
                include_my_retweet=True,
                include_entities=False)
        except Exception as e:
            print(e)
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_OAUTH_NOT_SUCCESS)
            return

        if tw_user.current_user_retweet:
            user.complete_task(task)
            db.session.commit()

            try:
                bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=msg.TASK_ELEMENT_DONE,
                    disable_web_page_preview=True)

                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=True,
                    text=msg.PAYMENT_GOT_NEW.format(
                        username=user.first_name,
                        amount=task.reward))

            except Exception as e:
                pass

        else:
            try:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=False,
                    text=msg.TASK_NAME['SHARE']['TWITTER']['NOT_FOUND'])
            except Exception as e:
                return

    elif task.action.social_network.name == 'FACEBOOK':
        fb = user.facebook

        if not fb or not fb.authorized:
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.FACEBOOK_NOT_EXISTS)
            return

        try:
            fb_api = facebook.GraphAPI(
                access_token=fb.oauth_token,
                version='2.7')
            fb_page_id = fb_api.get_object(
                id=current_app.config['LINK_TAG']['FACEBOOK']).get('id')
        except Exception as e:
            print(e)
            bot.send_message(
                user.tg_user_id,
                msg.FACEBOOK_OAUTH_NOT_SUCCESS)
            return

        try:
            fb_repost = fb_api.get_object(
                id=fb_page_id + '_' + task.post_id,
                fields='sharedposts{created_time}')
        except Exception as e:
            print(e)
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_OAUTH_NOT_SUCCESS)
            return

        if fb_repost.get('sharedposts') \
                and len(fb_repost['sharedposts']['data']) > 0:
            user.complete_task(task)
            db.session.commit()

            try:
                bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=msg.TASK_ELEMENT_DONE,
                    disable_web_page_preview=True)

                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=True,
                    text=msg.PAYMENT_GOT_NEW.format(
                        username=user.first_name,
                        amount=task.reward))

            except Exception as e:
                pass

        else:
            try:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=False,
                    text=msg.TASK_NAME['SHARE']['FACEBOOK']['NOT_FOUND'])
            except Exception as e:
                return


@bot.callback_query_handler(
    func=lambda call:
        call.message
        and call.data.split(':')[0] == 'LIKE'
        and call.data.split(':')[2] == 'CHECK')
def like_check(call):
    user = User.load_user(tg_user_id=call.from_user.id)

    try:
        task_id = int(call.data.split(':')[1])
    except Exception as e:
        print(e)
        return

    try:
        task = Task.query.filter_by(id=task_id).first()
    except Exception as e:
        print(e)
        return

    if task.action.social_network.name == 'TWITTER':
        tw = user.twitter

        if not tw or not tw.authorized:
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_NOT_EXISTS)
            return

        twapi = twitter.Api(
            consumer_key=current_app.config['TWITTER_CONSUMER_KEY'],
            consumer_secret=current_app.config['TWITTER_CONSUMER_SECRET'],
            access_token_key=tw.oauth_token,
            access_token_secret=tw.oauth_secret_token)

        try:
            tw_user = twapi.GetStatus(
                status_id=task.post_id,
                include_my_retweet=True,
                include_entities=False)
        except Exception as e:
            print(e)
            bot.answer_callback_query(
                callback_query_id=call.id,
                show_alert=False,
                text=msg.TWITTER_OAUTH_NOT_SUCCESS)
            return

        if tw_user.favorited:
            user.complete_task(task)
            db.session.commit()

            try:
                bot.edit_message_text(
                    chat_id=call.from_user.id,
                    message_id=call.message.message_id,
                    text=msg.TASK_ELEMENT_DONE,
                    disable_web_page_preview=True)

                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=True,
                    text=msg.PAYMENT_GOT_NEW.format(
                        username=user.first_name,
                        amount=task.reward))

            except Exception as e:
                pass

        else:
            try:
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    show_alert=False,
                    text=msg.TASK_NAME['LIKE']['TWITTER']['NOT_FOUND'])
            except Exception as e:
                return
