from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField


# WTForm
class CreateNewSection(FlaskForm):
    section_title = StringField("New Section Title", validators=[DataRequired()])
    section_description = CKEditorField("Section Description")
    section_body = CKEditorField("Section Body", validators=[DataRequired()])
    submit = SubmitField("Add section")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log Me In!")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")