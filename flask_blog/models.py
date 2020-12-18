from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt

from flask import current_app
from flask_blog import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(50), index=True, unique=True)
    email           = db.Column(db.String(100), index=True, unique=True)
    password_hash   = db.Column(db.String(100))
    about_me        = db.Column(db.String(150))
    last_seen       = db.Column(db.DateTime, default=datetime.utcnow)

    posts           = db.relationship('Post', backref='author', lazy='dynamic')

    followed        = db.relationship(
        'User',
        secondary       = followers,
        primaryjoin     = (followers.c.follower_id == id),
        secondaryjoin   = (followers.c.followed_id == id),
        backref         = db.backref('followers', lazy='dynamic'),
        lazy            = 'dynamic'
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>" 
    
    def set_password(self, password):
        self.password_hash  = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('UTF-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?s={size}&d=identicon'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
                
        return followed.union(self.posts).order_by(Post.timestamp.desc())

    def get_password_reset_token(self, expires_in=600):
        return jwt.encode(
            {'user_id': self.id, 'exp':time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('UTF-8')

    @staticmethod
    def verify_password_reset_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256']).get('user_id')
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    body            = db.Column(db.String(200))
    timestamp       = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'
