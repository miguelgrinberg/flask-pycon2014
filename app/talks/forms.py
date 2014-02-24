from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, Required, URL


class ProfileForm(Form):
    name = StringField('Name', validators=[Optional(), Length(1, 64)])
    location = StringField('Location', validators=[Optional(), Length(1, 64)])
    bio = TextAreaField('Bio')
    submit = SubmitField('Submit')


class TalkForm(Form):
    title = StringField('Title', validators=[Required(), Length(1, 128)])
    description = TextAreaField('Description')
    slides = StringField('Slides Embed Code (450 pixels wide)')
    video = StringField('Video Embed Code (450 pixels wide)')
    venue = StringField('Venue',
                        validators=[Required(), Length(1, 128)])
    venue_url = StringField('Venue URL',
                            validators=[Optional(), Length(1, 128), URL()])
    date = DateField('Date')
    submit = SubmitField('Submit')
