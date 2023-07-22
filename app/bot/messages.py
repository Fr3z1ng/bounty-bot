# -*- coding: utf-8 -*-

START_MESSAGE = 'Hello, {first_name}!👋\nWelcome to {bot_name}!\n\n' \
                'This bot will help you to earn ETokens for social ' \
                'activities and other tasks.\n\n' \
                'Try out /menu command to see what we can do for you 😉'
BALANCE_MESSAGE = 'ℹ️ Your current balance is *{amount}*.\n' \
                  'Complete more /tasks to earn stakes! 🎁'

UNKNOWN_ERROR = 'An unexpected was occured. The developers are notificed.\n' \
                'Try again later.'

PAYMENT_GOT_NEW = 'Hey, {username}! You just earned {amount} stakes!'

MENU = '➡️ Here is our menu:\n\n' \
       '/tasks - Tasks list\n' \
       '/settings - Your settings\n' \
       '/referral - Get your referral link\n' \
       '/balance - Show your balance\n' \
       '/menu - Show this message\n'
EMPLOYER_MENU = '⚔️ Admin menu:\n\n' \
                '/task_add - Add new task\n' \
                '/task_find - Find exists task\n' \
                '/task_edit <id> - Edit task with id <id>\n'
SETTINGS = '⚙️ You can edit your bot settings here.\n\n' \
           '/settings_twitter - View, edit and set up a Twitter ' \
           'connection\n' \
           '/settings_facebook - View, edit and set up a Facebook ' \
           'connection\n'
IN_DEV = '🛠 This module is in the process of development.\n' \
         'Stay tuned to our chat @{bounty_chat} to get updates!'

TASK_LIST = 'Available tasks:'
TASK_NO_ELEMENTS = 'You have completed all tasks.'
TASK_ELEMENT = '{action}\nReward: +<b>{reward}</b> stakes'
TASK_ELEMENT_BUTTON_MORE_INFO = 'More info'
TASK_ELEMENT_BUTTON_LESS_INFO = 'Less info'
TASK_ELEMENT_BUTTON_CHECK = 'Check completion'
TASK_ELEMENT_CLICK_CHECK_BUTTON = 'Finally, click the ' \
                                  '"Check completion" button ' \
                                  'to get reward. '
TASK_ELEMENT_HEADER = ''
TASK_CANNOT_LOAD = 'We are unable to load data, try again later'
TASK_ELEMENT_DONE = 'You have done this task'
TASK_NAME = {
    'SUBSCRIPTION': {
        'NAME': 'Subscription on page',

        'FACEBOOK': {
            'LESS': 'Follow us on Facebook',
            'MORE': 'Follow us on Facebook: '
            'https://fb.me/{tag}'
        },

        'TWITTER': {
            'LESS': 'Follow us on Twitter',
            'MORE': 'Follow us on Twitter: '
            'https://twitter.com/{tag}',
            'NOT_FOUND': 'You are not followed to our Twitter',
            'COMPLETE': 'You have already done this task'
        }
    },

    'SHARE': {
        'NAME': 'Share post',

        'TWITTER': {
            'LESS': 'Share our post on Twitter',
            'MORE': 'Share our post on Twitter '
            'https://twitter.com/gintr1k/status/{post_id}',
            'NOT_FOUND': 'You are not retweeted our post',
            'COMPLETE': 'You have already done this task'
        },

        'FACEBOOK': {
            'LESS': 'Share our post on Facebook',
            'MORE': 'Share our post on Facebook '
            'https://facebook.com/gintr1k/posts/{post_id}',
            'NOT_FOUND': 'You are not shared our post',
            'COMPLETE': 'You have already done this task'
        }
    },

    'LIKE': {
        'TWITTER': {
            'LESS': 'Like post on Twitter',
            'MORE': 'Like our post on Twitter '
            'https://twitter.com/gintr1k/status/{post_id}',
            'NOT_FOUND': 'You are not liked our post',
            'COMPLETE': 'You have already done this task'
        }
    },

    'REFERRAL': {
        'LESS': 'Invite friends to bot',
        'MORE': 'Click on /referral command and share '
        'your referral link with friends\n'
        'Then, your friends must complete at least {tasks_count} tasks '
        'to make us sure, that you and your friends are not bots'
    }
}

REFERRAL_SHARE = '💎 You have *{referred_count}* referrals.\n' \
                 'Invite your *friends* in the app and earn ' \
                 '*stakes*.\n' \
                 'Your referral link is:'
BOUNTY_BOT_URL = 'https://t.me/{bot_tag}'
REFERRAL_SHARE_URL = 'https://t.me/{bot_tag}?start={user_id}'
REFERRAL_NEW = 'Hello, {username}! You just earned *{amount}* stakes ' \
               'for friend invitation!'

TWITTER_EXISTS = '🆗 You have already set up a connection with Twitter.'
TWITTER_NOT_EXISTS = '💡 Сonnect your Twitter account via command ' \
                     '/settings_twitter'
TWITTER_OAUTH_NOT_SUCCESS = 'An unexpected error has occurred with ' \
                            'Twitter.\nPlease, try again 🙏'
TWITTER_OAUTH_ERROR = TWITTER_OAUTH_NOT_FOUND = TWITTER_OAUTH_NOT_SUCCESS
TWITTER_DUPLICATE_USER = 'A user with that Twitter account already exists.'
TWITTER_SETUP = '➡️ To set up a connection with Twitter, ' \
                'follow the [link]({link}).'
TWITTER_CONNECTED = '✅ {name}, have successfully connected Twitter, ' \
                    'congratulations!'

FACEBOOK_EXISTS = '🆗 You have already set up a connection with Facebook ' \
                  '({name}).'
FACEBOOK_NOT_EXISTS = '💡 Connect your Facebook account via command ' \
                      '/settings_facebook'
FACEBOOK_DUPLICATE_USER = 'A user with that Facebook account already exists.'
FACEBOOK_SETUP = '➡️ To set up a connection with Facebook, ' \
                 'follow the [link]({link}).'
FACEBOOK_CONNECTED = '✅ {name}, you have successfully connected Facebook, ' \
                     'congratulations!'
FACEBOOK_TOKEN_EXPIRED = 'ℹ️ Your authorization period has been expired ' \
                         'or you has revoked it. You need to connect ' \
                         'Facebook again.'
FACEBOOK_USER_NOT_FOUND = '⚠️ An unexpected error has occurred with ' \
                          'Facebook.\nPlease, try again 🙏'
FACEBOOK_OAUTH_ERROR = FACEBOOK_OAUTH_NOT_SUCCESS = FACEBOOK_USER_NOT_FOUND

ADMIN_MENU = 'Some statistics:\n\n' \
             'Users count: <b>{users_count}</b>\n' \
             'Stakes issued: <b>{stakes_count}</b>'
ADMIN_MENU_BUTTONS = {
    'ADD_TASK': 'Add a task',
    'FIND_TASK': 'Find a task'
}
ADMIN_BACK_TO_MENU = 'Back to Menu'
ADMIN_FIND_TASK = 'Alright, enter a link to the post.'
ADMIN_INLINE_TITLE = 'Search for tasks'
ADMIN_INLINE_DESC = 'Enter a link to the task\'s post'
ADMIN_INLINE_INPUT_MESSAGE = 'You need to enter a link to the post ' \
                             'to find a task'
ADMIN_EDIT_TASK = 'Edit'
ADMIN_TASK = '{type}\nReward: *{reward}*\n' \
             'Start time: *{start_timestamp}*\n' \
             'End time: *{end_timestamp}*\n' \
             'Can complete *{complete_times}* times\n\n' \
             'Statistics:\n' \
             'Completed *{completed_count}* times by *{users_count}* users;\n'\
             'Stakes issued: *{stakes_issued}*.'
