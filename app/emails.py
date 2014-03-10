from threading import Thread
import time
from datetime import datetime
from flask import current_app, render_template, url_for
from flask.ext.mail import Message
from . import db
from .models import PendingEmail
from . import mail

_email_thread = None


def get_notification_email(name, email, subject, body_text, body_html):
    msg = Message(subject, recipients=['{0} <{1}>'.format(name, email)])
    msg.body = body_text
    msg.html = body_html
    return msg


def flush_pending(app):
    while True:
        time.sleep(app.config['MAIL_FLUSH_INTERVAL'])
        now = datetime.utcnow()
        with app.app_context():
            emails = PendingEmail.query.filter(PendingEmail.timestamp < now)
            if emails.count() > 0:
                with mail.connect() as conn:
                    for email in emails.all():
                        conn.send(
                            get_notification_email(email.name, email.email,
                                                   email.subject,
                                                   email.body_text,
                                                   email.body_html))
                        db.session.delete(email)
            db.session.commit()


def start_email_thread():
    if not current_app.config['TESTING']:
        global _email_thread
        if _email_thread is None:
            print("Starting email thread...")
            _email_thread = Thread(target=flush_pending,
                                   args=[current_app._get_current_object()])
            _email_thread.start()


def send_author_notification(talk):
    if not PendingEmail.already_in_queue(talk.author.email, talk):
        pending_email = PendingEmail(
            name=talk.author.username,
            email=talk.author.email,
            subject='[talks] New comment',
            body_text=render_template('email/notify.txt',
                                      name=talk.author.username,
                                      email=talk.author.email, talk=talk),
            body_html=render_template('email/notify.html',
                                      name=talk.author.username,
                                      email=talk.author.email, talk=talk),
            talk=talk)
        db.session.add(pending_email)
        db.session.commit()


def send_comment_notification(comment):
    talk = comment.talk
    for email, name in comment.notification_list():
        if not PendingEmail.already_in_queue(email, talk):
            unsubscribe = url_for('talks.unsubscribe',
                            token=talk.get_unsubscribe_token(email),
                            _external=True)
            pending_email = PendingEmail(
                name=name, email=email, subject='[talks] New comment',
                body_text=render_template('email/notify.txt',
                                          name=name, email=email, talk=talk,
                                          unsubscribe=unsubscribe),
                body_html=render_template('email/notify.html',
                                          name=name, email=email, talk=talk,
                                          unsubscribe=unsubscribe),
                talk=talk)
            db.session.add(pending_email)
            db.session.flush()
    db.session.commit()
