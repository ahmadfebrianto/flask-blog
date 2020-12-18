from flask import render_template, url_for, flash, redirect, request, g, current_app
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from datetime import datetime
from flask_babel import _, get_locale

from flask_blog import db
from flask_blog.apps.posts.forms import PostForm
from flask_blog.models import Post


main = Blueprint('main', __name__)


@main.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.locale = str(get_locale())

def page_number():
    return request.args.get('page', 1, type=int)

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post has been updated!'))
        return redirect(url_for('main.index'))
    posts = current_user.followed_posts().paginate(
        page_number(), current_app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    return render_template(
        'index.html', posts=posts.items, title='Home', form=form,
        prev_url=prev_url, next_url=next_url)


