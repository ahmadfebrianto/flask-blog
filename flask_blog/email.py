from threading import Thread
from flask import render_template
from flask_mail import Message
from flask_blog import current_app, mail


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)

    
def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_mail, args=(current_app, msg)).start()


def send_password_reset_mail(user):
    token = user.get_password_reset_token()
    send_mail(
        '[Microblog]Reset Your Password',
        sender = current_app.config['ADMINS'][0],
        recipients = [user.email],
        text_body = render_template('email/password_reset.txt', user=user, token=token),
        html_body = render_template('email/password_reset.html', user=user, token=token) 
    )