from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class CustomerRegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    username = StringField("Username", validators=[Optional(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=180)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class CustomerLoginForm(FlaskForm):
    identifier = StringField("Username or email", validators=[DataRequired(), Length(max=180)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class CustomerForgotPasswordForm(FlaskForm):
    identifier = StringField("Username or email", validators=[DataRequired(), Length(max=180)])
    submit = SubmitField("Create reset link")


class CustomerResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset password")
