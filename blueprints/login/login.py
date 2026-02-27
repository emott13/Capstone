from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import Users, bcrypt
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField, SubmitField, RadioField)
from wtforms.validators import DataRequired, Length, Email, EqualTo

login_bp = Blueprint("login", __name__, static_folder="static_login",
                  template_folder="templates")

class LoginForm(FlaskForm):    
    username = StringField('Username Or Email',
        validators=[
            DataRequired(),
            Length(max=255),
        ])
    password = PasswordField('Password',
        validators=[
            DataRequired(),
            Length(min=8, max=255),
        ])
    submit = SubmitField('Login')


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    error = request.args.get("error", None)
    success = request.args.get("success", None)
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Invalid input")

        user = Users.query.filter_by(email=email).first()
        user_username = Users.query.filter_by(username=email).first()

        # first checks email, then checks username
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home.home"))
        elif user_username and bcrypt.check_password_hash(user_username.password, password):
            login_user(user_username)
            return redirect(url_for("home.home"))
        
        else:
            return render_template("login.html", error="Invalid username or password",
                                   login_form=login_form)

    return render_template("login.html", error=error, success=success,
                           login_form=login_form,)
