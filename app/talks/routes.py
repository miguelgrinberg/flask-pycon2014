from flask import render_template
from ..models import User
from . import talks


@talks.route('/')
def index():
    return render_template('talks/index.html')


@talks.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('talks/user.html', user=user)

