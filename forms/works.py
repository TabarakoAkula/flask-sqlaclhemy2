from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class WorksLogForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    team_leader = StringField("Team Leader id")
    user = StringField("Team Leader id")
    work_size = IntegerField('Work Size')
    collaborators = StringField('Collaborators')
    is_finished = BooleanField("Is job finished?")
    submit = SubmitField('Submit')


