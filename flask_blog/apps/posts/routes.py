from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g, current_app
from flask_login import login_required, current_user
from flask_blog.models import Post
from flask_blog import db
from flask_blog import translator
from flask_babel import _, get_locale
from datetime import datetime


posts = Blueprint('posts', __name__)


@posts.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.locale = str(get_locale())


def page_number():
    return request.args.get('page', 1, type=int)


@posts.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page_number(), current_app.config['POSTS_PER_PAGE'], False)
    prev_url = url_for('posts.explore', page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('posts.explore', page=posts.next_num) if posts.has_next else None
    return render_template(
        'index.html', title='Explore', posts=posts.items,
        prev_url=prev_url, next_url=next_url)


@posts.route('/post/<post_id>/edit', methods=['POST'])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=int(post_id)).first()
    post.body = request.form.get('new_post')
    db.session.commit()
    return jsonify({'new_post': post.body})


@posts.route('/post/<post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash(_('Your post has been deleted!'))
    return redirect(url_for('main.index'))


@posts.route('/detect-language', methods=['POST'])
@login_required
def detect_lang():
    post_items = request.form.get('post_items')
    if post_items != None:
        post_items = list(map(lambda x: x.strip(),post_items.split(',')))
        results = []
        if len(post_items) > 2:
            post_items = [post_items[i:i+2] for i in range(0, len(post_items), 2)]
            for post in post_items:
                post_id, post_text = post
                post_lang = translator.detect_language(post_text)
                if post_lang.lang == 'msid':
                    post_lang.lang = post_lang.lang[2:]
                results.append([post_id, post_lang.lang])
            return jsonify({'results': results})

        else:
            post_id, post_text = post_items
            post_lang = translator.detect_language(post_text)
            if post_lang.lang == 'msid':
                post_lang.lang = post_lang.lang[2:]
            results = [post_id, post_lang.lang]
            return jsonify({'results': results})


@posts.route('/post/<post_id>/translate', methods=['POST'])
@login_required
def translate(post_id):
    text = request.form.get('origin_text')
    dest = request.form.get('dest_lang')
    result = translator.translate_language(text, dest=dest)
    return jsonify({'result': result.text})
