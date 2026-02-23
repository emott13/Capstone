import time
from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from sqlalchemy import text
from extensions import Users, UserRoles, Roles, bcrypt, db
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

register_bp = Blueprint("register", __name__, static_folder="register_static",
                  template_folder="templates")


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    error = request.args.get("error", None)
    if register_form.validate_on_submit():
        print(request.form.getlist('role_id'))
        role_ids = request.form.getlist('role_id')

        if role_ids == []:
            error = "Need to select an account type"
        else:
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
            
            return redirect(url_for('login.login', success="Account created! Login here"))

    roles = Roles.query.where(text('role_name != \'admin\'')).order_by(Roles.role_id.desc())

    return render_template("register.html", error=error,
                           roles=roles, register_form=register_form,
    )
