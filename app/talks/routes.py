from flask import render_template
from . import talks


@talks.route('/')
def index():
    return render_template('talks/index.html')


@talks.route('/user/<username>')
def user(username):
    return render_template('talks/user.html', username=username)

