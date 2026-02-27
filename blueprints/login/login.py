from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import Users, bcrypt
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField, SubmitField, RadioField)
from wtforms.validators import Length, Email, EqualTo, InputRequired, Regexp

login_bp = Blueprint("login", __name__, static_folder="static_login",
                  template_folder="templates")

class LoginForm(FlaskForm):    
    username = StringField('Username Or Email',
        validators=[
            InputRequired(message="A username or email is required"),
            Length(max=255),
        ])
    password = PasswordField('Password',
        validators=[
            InputRequired(),
            Length(min=8, max=255),
        ])
    submit = SubmitField('Login')


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    error = request.args.get("error", None)
    success = request.args.get("success", None)

    # This only happens on POST request
    if login_form.validate_on_submit():
        error = login_post(login_form)
        if not error:
            return redirect(url_for("home.home"))

    return render_template("login.html", error=error, success=success,
                           login_form=login_form,)


def login_post(login_form) -> str:
    """Runs the login post verifications and logic. Returns the error if there is any"""
    email = request.form.get("username")
    password = request.form.get("password")

    if not email or not password:
        return "Invalid input"
    user = Users.query.filter_by(email=email).first()
    user_username = Users.query.filter_by(username=email).first()

    # first checks email, then checks username
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
    elif user_username and bcrypt.check_password_hash(user_username.password, password):
        login_user(user_username)
    else:
        return "Invalid username or password"
    
    return ""
