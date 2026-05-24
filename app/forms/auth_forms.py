from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    identifier = StringField("Username or email", validators=[DataRequired(), Length(max=180)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    identifier = StringField("Username or email", validators=[DataRequired(), Length(max=180)])
    submit = SubmitField("Create reset link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset password")
