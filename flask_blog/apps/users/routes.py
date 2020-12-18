from flask import Blueprint, render_template, redirect, url_for, request, flash, g, current_app
from flask_login import login_required, login_user, logout_user, current_user
from flask_blog.models import User, Post
from flask_blog import db 
from .forms import *
from werkzeug.urls import url_parse
from flask_blog.email import send_password_reset_mail
from flask_babel import _, get_locale
from datetime import datetime


users = Blueprint('users', __name__)

@users.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.locale = str(get_locale())


def page_number():
    return request.args.get('page', 1, type=int)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        flash(_('Registration for %(username)s is successful. Log in now!', username=new_user.username))
        return redirect(url_for('users.login'))
    
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password!'))
            return redirect(url_for('users.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page is None or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash(_('Welcome %(username)s', username=form.username.data))
        return redirect(next_page)
    return render_template('login.html', form=form, title='Login')


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have just logout!'))
    return redirect(url_for('users.login'))


@users.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(
        Post.timestamp.desc()).paginate(
            page_number(), current_app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('users.profile', username=user.username, page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('users.profile', username=user.username, page=posts.next_num) if posts.has_next else None

    form = EmptyForm()
    return render_template(
        'profile.html', posts=posts.items, form=form, user=user, title="Profile",
        prev_url=prev_url, next_url=next_url)
    

@users.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your profile has been updated!'))
        return redirect(url_for('users.edit_profile', username=current_user.username))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form, user=user, title='Edit Profile')


@users.route('/profile/<username>/change-password', methods=['GET', 'POST'])
def change_password(username):
    user = User.query.filter_by(username=username).first()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(_('Your password has been updated!'))
        return redirect(url_for('users.profile', username=username))
    return render_template('change_password.html', title='Change Password', form=form, user=user)


@users.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user: 
        flash(_('User %(username)s is not found!', username=username))
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash(_('You can\'t follow yourself!'))
        return redirect(url_for('users.profile', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(_('You\'re now following %(username)s!', username=username))
    return redirect(url_for('users.profile', username=username))


@users.route('/unfollow/<username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(_('User %(username)s is not found!', username=username))
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash(_('You can\'t unfollow yourself!'))
        return redirect(url_for('users.profile', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_('You\'re not following %(username)s anymore.', username=username))
    return redirect(url_for('users.profile', username=username))


@users.route('/request-password-reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
            flash(_('An email has been sent to your email to reset your password!'))
            return redirect(url_for('users.login'))
    return render_template(
        'request_password_reset.html', 
        title="Request Password Reset", 
        form=form)


@users.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_password_reset_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(_('Your password has been reset!'))
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)