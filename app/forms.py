from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     TextAreaField, IntegerField)
from wtforms.validators import DataRequired


class AdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PhoneForm(FlaskForm):
    maker = StringField('Maker', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    img_link = StringField('Image Link', validators=[DataRequired()])
    specs = TextAreaField('Specifications')
    memory = IntegerField('Memory', validators=[DataRequired()])
    ram = IntegerField('RAM', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Add Phone')
