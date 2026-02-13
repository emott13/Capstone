import time
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import Users, Roles, bcrypt, db
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField, SubmitField, RadioField)
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegisterForm(FlaskForm):    
    username = StringField('Username',
        validators=[
            DataRequired(),
            Length(min=2, max=30),
        ])
    email = StringField('Email',
        validators=[
            DataRequired(), 
            Email(),
            
        ])
    password = PasswordField('Password',
        validators=[
            DataRequired(),
            Length(min=8, max=255),
        ])
    confirm_password = PasswordField('Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password'),
        ])
    first_name = StringField('First Name',
        validators=[
            DataRequired(), 
        ])
    last_name = StringField('Last Name',
        validators=[
            DataRequired(), 
        ])
    dob = DateField('Date Of Birth',
        validators=[
            DataRequired(),
        ])
    submit = SubmitField('Sign Up')

register_bp = Blueprint("register", __name__, static_folder="static",
                  template_folder="templates")


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    error = request.args.get("error", None)
    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
        user = Users(username=register_form.username.data,
                     email=register_form.email.data,
                     password=hashed_password,
                     last_name=register_form.last_name.data,
                     first_name=register_form.first_name.data,
                     dob=register_form.dob.data,
        )
        db.session.add(user)
        db.session.commit()
        
        return "Success"

    roles = Roles.query.order_by(Roles.role_id.desc())

    return render_template("register.html", error=error,
                           roles=roles, register_form=register_form
    )
