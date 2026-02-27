from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from sqlalchemy import text
from extensions import bcrypt, db
from models import Users, UserRoles, Roles
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField, SubmitField, RadioField)
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError

class RegisterForm(FlaskForm):    
    username = StringField('Username',
        validators=[
            InputRequired(),
            Length(min=2, max=30),
        ])
    email = StringField('Email',
        validators=[
            InputRequired(), 
            Email(),
            
        ])
    password = PasswordField('Password',
        validators=[
            InputRequired(),
            Length(min=8, max=255),
            Regexp(regex="^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*])", message="Password must contain at least 1 capital, 1 lowercase, 1 number, and a special character."),
        ])
    confirm_password = PasswordField('Confirm Password',
        validators=[
            InputRequired(),
            EqualTo('password', message="Passwords must match."),
        ])
    first_name = StringField('First Name',
        validators=[
            InputRequired(), 
            Length(max=50),
        ])
    last_name = StringField('Last Name',
        validators=[
            InputRequired(), 
            Length(max=50),
        ])
    dob = DateField('Date Of Birth',
        validators=[
            InputRequired(),
            
        ])
    submit = SubmitField('Sign Up')

    def validate_dob(form, field):
        if field.data < datetime(1900, 1, 1).date():
            raise ValidationError("Date of birth must be greater than the year 1900")
        elif field.data > datetime.today().date():
            raise ValidationError("Date of birth can not be in the future")

register_bp = Blueprint("register", __name__, static_folder="register_static",
                  template_folder="templates")


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    error = request.args.get("error", None)
    if register_form.validate_on_submit():
        error = register_post(register_form)
        if not error:
            return redirect(url_for('login.login', success="Account created! Login here"))

    roles = Roles.query.where(text('role_name != \'admin\'')).order_by(Roles.role_id.desc())

    return render_template("register.html", error=error,
                           roles=roles, register_form=register_form,
    )


def register_post(register_form) -> str:
    """Runs the register post verifications and logic. Returns the error if there is any"""
    role_ids = request.form.getlist('role_id')

    if role_ids == []:
        return "Need to select an account type"
        
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

    roles = []
    for role_id in role_ids:
        roles.append(UserRoles(user_id=user.user_id, role_id=role_id))
    db.session.add_all(roles)
    db.session.commit()
    
    return ""
