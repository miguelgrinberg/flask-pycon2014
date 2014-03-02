from flask import render_template, flash, redirect, url_for, abort
from flask.ext.login import login_required, current_user
from .. import db
from ..models import User, Talk, Comment
from . import talks
from .forms import ProfileForm, TalkForm, CommentForm, PresenterCommentForm


@talks.route('/')
def index():
    talk_list = Talk.query.order_by(Talk.date.desc()).all()
    return render_template('talks/index.html', talks=talk_list)


@talks.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    talk_list = user.talks.order_by(Talk.date.desc()).all()
    return render_template('talks/user.html', user=user, talks=talk_list)


@talks.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('talks.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('talks/profile.html', form=form)


@talks.route('/new', methods=['GET', 'POST'])
@login_required
def new_talk():
    form = TalkForm()
    if form.validate_on_submit():
        talk = Talk(author=current_user)
        form.to_model(talk)
        db.session.add(talk)
        db.session.commit()
        flash('The talk was added successfully.')
        return redirect(url_for('.index'))
    return render_template('talks/edit_talk.html', form=form)


@talks.route('/talk/<int:id>', methods=['GET', 'POST'])
def talk(id):
    talk = Talk.query.get_or_404(id)
    comment = None
    if current_user.is_authenticated():
        form = PresenterCommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              talk=talk,
                              author=current_user,
                              notify=False, approved=True)
    else:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              talk=talk,
                              author_name=form.name.data,
                              author_email=form.email.data,
                              notify=form.notify.data, approved=False)
    if comment:
        db.session.add(comment)
        db.session.commit()
        if comment.approved:
            flash('Your comment has been published.')
        else:
            flash('Your comment will be published after it is reviewed by '
                  'the presenter.')
        return redirect(url_for('.talk', id=talk.id) + '#top')
    if talk.author == current_user or \
            (current_user.is_authenticated() and current_user.is_admin):
        comments_query = talk.comments
    else:
        comments_query = talk.approved_comments()
    comments = comments_query.order_by(Comment.timestamp.asc()).all()
    headers = {}
    if current_user.is_authenticated():
        headers['X-XSS-Protection'] = '0'
    return render_template('talks/talk.html', talk=talk, form=form,
                           comments=comments), 200, headers


@talks.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_talk(id):
    talk = Talk.query.get_or_404(id)
    if not current_user.is_admin and talk.author != current_user:
        abort(403)
    form = TalkForm()
    if form.validate_on_submit():
        form.to_model(talk)
        db.session.add(talk)
        db.session.commit()
        flash('The talk was updated successfully.')
        return redirect(url_for('.talk', id=talk.id))
    form.from_model(talk)
    return render_template('talks/edit_talk.html', form=form)


@talks.route('/moderate')
@login_required
def moderate():
    comments = current_user.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('talks/moderate.html', comments=comments)


@talks.route('/moderate-admin')
@login_required
def moderate_admin():
    if not current_user.is_admin:
        abort(403)
    comments = Comment.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('talks/moderate.html', comments=comments)
