from flask import current_app
from sqlalchemy import func
from datetime import datetime
import oauth2
import urllib.parse
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    tg_user_id = db.Column(db.Integer, index=True, nullable=False, unique=True)
    username = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    employer = db.Column(db.Boolean, default=False, nullable=False)
    referral_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    referral = db.relationship(
        'User', backref='referred', remote_side=[id])
    twitter = db.relationship(
        'TwitterConnection', uselist=False)
    facebook = db.relationship(
        'FacebookConnection', uselist=False)
    linkedin = db.relationship(
        'LinkedInConnection', uselist=False)
    completed_task_list = db.relationship(
        'TaskCompletion', lazy='dynamic', backref='user')
    payments = db.relationship(
        'Payment', backref='user')

    # Methods
    """def __repr__(self):
        return f'<User id={self.id}, tg_user_id={self.tg_user_id}>'"""

    @staticmethod
    def load_user(user_id=None, tg_user_id=None):

        if user_id:
            try:
                user_id = int(user_id)
            except Exception as e:
                return None

            return User.query.filter_by(id=user_id).first()

        if tg_user_id:
            try:
                tg_user_id = int(tg_user_id)
            except Exception as e:
                return None

            return User.query.filter_by(tg_user_id=tg_user_id).first()

    def find_completed_task(self, task):
        return TaskCompletion.query.filter_by(user=self, task=task).all()

    def can_complete_task(self, task):
        if (TaskCompletion.query.filter_by(
                user=self, task=task).count() < task.complete_times
                or task.complete_times == 0) \
                and (
                    task.start_timestamp is None
                    or task.start_timestamp < datetime.utcnow()
                ) \
                and (
                    task.end_timestamp is None
                    or task.end_timestamp > datetime.utcnow()
                ):
            return True

        return False

    def complete_task(self, task):
        completed_task = TaskCompletion(task=task)
        db.session.add(completed_task)

        payment = Payment(
            user=self,
            task=completed_task,
            amount=task.reward)
        db.session.add(payment)

        self.completed_task_list.append(completed_task)

        if self.referral \
                and self.completed_task_list.count() == \
                current_app.config['REFERRER_DONE_TASKS_COUNT']:
            ref_task = Task.query.filter_by(
                action=TaskAction.query.filter_by(name='REFERRAL').first()
            ).first()

            if ref_task and self.referral:
                self.referral.complete_task(ref_task)

    def get_balance(self):
        balance = db.session.query(
                func.sum(Payment.amount)
            ).filter(
                Payment.user == self
            ).first()[0]

        return balance if balance else 0

    def get_list(self, offset=1):
        tasks = Task.query.filter(
            ~Task.id.in_(
                [
                    completed_task.task.id
                    for completed_task in self.completed_task_list.all()
                ]),
            Task.complete_times > -1
        ).paginate(offset, 5, False)

        return tasks


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ctask_id = db.Column(db.Integer, db.ForeignKey('task_completions.id'))
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(300), default=None)
    revoked = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    task = db.relationship('TaskCompletion', uselist=False, backref='payment')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.Integer, db.ForeignKey('task_actions.id'))
    post_id = db.Column(db.String(256), default=None)
    reward = db.Column(db.Integer, default=0, nullable=False)
    complete_times = db.Column(db.Integer, default=1, nullable=False)
    start_timestamp = db.Column(db.DateTime, default=None)
    end_timestamp = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    action = db.relationship('TaskAction', backref='tasks')
    completed_list = db.relationship('TaskCompletion', backref='task')


class TaskCompletion(db.Model):
    __tablename__ = 'task_completions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class TaskAction(db.Model):
    __tablename__ = 'task_actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    social_network_id = db.Column(
        db.Integer, db.ForeignKey('social_networks.id'))

    # Relationships
    social_network = db.relationship(
        'SocialNetwork', uselist=False, backref='task_actions')


class SocialNetwork(db.Model):
    __tablename__ = 'social_networks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))


class TwitterConnection(db.Model):
    __tablename__ = 'connections_twitter'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    oauth_token = db.Column(db.String(256), default=None, index=True)
    oauth_secret_token = db.Column(db.String(256), default=None)
    requested_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    authorized = db.Column(db.Boolean, default=False, nullable=False)
    authorized_timestamp = db.Column(db.DateTime, default=None)
    twitter_user_id = db.Column(db.String(64), default=None)
    user = db.relationship('User')

    def __repr__(self):
        return f'<TwitterConnection id={self.id}, ' + \
            f'authorized={self.authorized}, ' + \
            f'timestamp={self.timestamp}>'

    @staticmethod
    def find_user(twitter_id):
        return TwitterConnection.query.filter_by(
            twitter_user_id=str(twitter_id)).first()

    def setup_oauth(self):
        oauth_consumer = oauth2.Consumer(
            key=current_app.config['TWITTER_CONSUMER_KEY'],
            secret=current_app.config['TWITTER_CONSUMER_SECRET'])
        oauth_client = oauth2.Client(oauth_consumer)

        oauth_twitter_url = 'https://api.twitter.com/oauth/request_token?%s' \
            % urllib.parse.urlencode({
                'oauth_callback': current_app.config['WEBHOOK_URL_BASE']
                + current_app.config['TWITTER_URL_PREFIX']
            })

        res, content = oauth_client.request(oauth_twitter_url, 'POST')

        if int(res['status']) != 200:
            raise Exception(
                'Invalid response code {status}\nResponse: {content}'
                .format(
                    status=res['status'],
                    content=content))

        content = dict(urllib.parse.parse_qsl(content.decode('utf-8')))

        self.oauth_token = content['oauth_token']
        self.oauth_secret_token = content['oauth_token_secret']

    def get_oauth_url(self):
        return 'https://api.twitter.com/oauth/authenticate?%s' \
            % urllib.parse.urlencode({
                'oauth_token': self.oauth_token
            })


class FacebookConnection(db.Model):
    __tablename__ = 'connections_facebook'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    oauth_token = db.Column(db.String(256), default=None, index=True)
    expires_in = db.Column(db.DateTime, default=None)
    token_type = db.Column(db.String(16), default=None)
    authorized = db.Column(db.Boolean, default=False, nullable=False)
    authorized_timestamp = db.Column(db.DateTime, default=None)
    facebook_user_id = db.Column(db.String(64), default=None)
    user = db.relationship('User')

    def __repr__(self):
        return f'<FacebookConnection id={self.id}, ' + \
            f'authorized={self.authorized}, ' + \
            f'timestamp={self.timestamp}>'

    @staticmethod
    def find_user(facebook_id):
        return FacebookConnection.query.filter_by(
            facebook_user_id=str(facebook_id)).first()

    @staticmethod
    def get_oauth_url(user_id):
        return 'https://www.facebook.com/v3.0/dialog/oauth?%s' \
            % urllib.parse.urlencode({
                'client_id': current_app.config['FACEBOOK_APP_ID'],
                'response_type': 'code',
                'scope': 'manage_pages,user_posts,user_status',
                'redirect_uri': current_app.config['WEBHOOK_URL_BASE']
                + current_app.config['FACEBOOK_URL_PRIFIX'],
                'state': user_id
            })


class LinkedInConnection(db.Model):
    __tablename__ = 'connections_linkedin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    authorized = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship('User')

    def __repr__(self):
        return f'<LinkedInConnection id={self.id}, ' + \
            f'authorized={self.authorized}, ' + \
            f'timestamp={self.timestamp}>'
