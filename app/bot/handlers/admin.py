from sqlalchemy import func
import telebot
from urllib.parse import urlparse
from app import db, tg_bot as bot
from app.bot import messages as msg
from app.models import User, Payment, TaskCompletion, Task


@bot.message_handler(commands=['admin'])
def admin_menu(message):
    user = User.load_user(tg_user_id=message.from_user.id)
    if not user or not user.employer:
        return

    try:
        bot.send_chat_action(message.from_user.id, 'typing')
    except Exception as e:
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    button_add_task = telebot.types.InlineKeyboardButton(
        text=msg.ADMIN_MENU_BUTTONS['ADD_TASK'],
        callback_data='ADD_TASK')
    button_find_task = telebot.types.InlineKeyboardButton(
        text=msg.ADMIN_MENU_BUTTONS['FIND_TASK'],
        switch_inline_query_current_chat='')
    keyboard.add(button_add_task, button_find_task)

    bot.send_message(
        message.from_user.id,
        msg.ADMIN_MENU.format(
            users_count=User.query.count(),
            stakes_count=db.session.query(
                func.sum(Payment.amount)
            ).filter(Payment.revoked is False).first()[0]),
        parse_mode='html',
        reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: call.message and call.data == 'ADMIN_MENU')
def admin_menu_callback(call):
    user = User.load_user(tg_user_id=call.from_user.id)
    if not user or not user.employer:
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    button_add_task = telebot.types.InlineKeyboardButton(
        text=msg.ADMIN_MENU_BUTTONS['ADD_TASK'],
        callback_data='ADD_TASK')
    button_find_task = telebot.types.InlineKeyboardButton(
        text=msg.ADMIN_MENU_BUTTONS['FIND_TASK'],
        switch_inline_query_current_chat='')
    keyboard.add(button_add_task, button_find_task)

    try:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=msg.ADMIN_MENU.format(
                users_count=User.query.count(),
                stakes_count=db.session.query(
                    func.sum(Payment.amount)
                ).filter(Payment.revoked is False).first()[0]),
            reply_markup=keyboard,
            parse_mode='html',
            disable_web_page_preview=True)
    except Exception as e:
        pass


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def empty_query(query):
    user = User.load_user(tg_user_id=query.from_user.id)
    if not user or not user.employer:
        return

    keyboard = telebot.types.InlineKeyboardMarkup()

    arcticles = []
    task_id = 0
    task_url = query.query
    print()

    url = urlparse(task_url)
    if url.scheme and url.netloc:
        if 'twitter.com' in url.netloc:
            url_path = url.path.split('/')
            if len(url_path) > 0:
                task_id = url_path[-1]

        tasks = Task.query.filter_by(post_id=task_id).all()

        for index, task in enumerate(tasks):
            button_edit = telebot.types.InlineKeyboardButton(
                text=msg.ADMIN_EDIT_TASK,
                callback_data=f'ADMIN_EDIT_TASK:{task.id}')
            keyboard.add(button_edit)

            arcticles.append(telebot.types.InlineQueryResultArticle(
                id=index, title='Task',
                description=f'{task.action.social_network.name} - '
                + msg.TASK_NAME[task.action.name]['NAME'],
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=msg.ADMIN_TASK.format(
                        type=f'{task.action.social_network.name} - '
                        + msg.TASK_NAME[task.action.name]["NAME"],
                        reward=task.reward,
                        start_timestamp=task.start_timestamp.strftime(
                            '%d.%m.%Y %H:%M:%S')
                        if task.start_timestamp else 'None',
                        end_timestamp=task.end_timestamp.strftime(
                            '%d.%m.%Y %H:%M:%S')
                        if task.end_timestamp else 'None',
                        complete_times=task.complete_times
                        if task.complete_times > 0 else 'Unlimited'
                        if task.complete_times == 0 else 'Disabled',
                        completed_count=TaskCompletion.query.filter_by(
                            task=task).count(),
                        users_count=TaskCompletion.query.filter_by(task=task).
                        group_by(TaskCompletion.user_id).count(),
                        stakes_issued=0),
                    parse_mode='Markdown'),
                reply_markup=keyboard))

    if len(arcticles) == 0:
        button_find = telebot.types.InlineKeyboardButton(
            text=msg.ADMIN_MENU_BUTTONS['FIND_TASK'],
            switch_inline_query_current_chat='')
        keyboard.add(button_find)

        arcticles.append(telebot.types.InlineQueryResultArticle(
            id='1', title='Nothing is found',
            input_message_content=telebot.types.InputTextMessageContent(
                message_text=f'On query `{query.query}` '
                'nothing is found.',
                parse_mode='Markdown'),
            reply_markup=keyboard))

    bot.answer_inline_query(query.id, arcticles)
