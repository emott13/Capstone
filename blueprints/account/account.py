from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo
from extensions import bcrypt, db
from services.UserService import UserService
from models import Users

account_bp = Blueprint("account", __name__, template_folder="templates_account")

class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Current Password',
        validators=[
            InputRequired(),
            Length(min=8, max=255)
        ])

    new_password = PasswordField('New Password',
        validators=[
            InputRequired(),
            Length(min=8, max=255)
        ])

    confirm_password = PasswordField('Confirm New Password',
        validators=[
            InputRequired(),
            EqualTo('new_password', message="Passwords must match")
        ])

    submit = SubmitField('Reset Password')

@account_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    customer_id = current_user.get_id()

    # get user information
    user = Users.query.get(customer_id)

    for phone in user.phone_numbers:
        print("phone!   ", phone.phone_number)

    form = ResetPasswordForm()
    error = None
    success = None

    if form.validate_on_submit():
        error = reset_password_post(form)
        if not error:
            success = "Password updated successfully"

    return render_template(
        "account.html",
        user=user,
        form=form,  
        error=error,
        success=success
    )

@account_bp.route("/account/phone", methods=["POST"])
def add_phone_number():
    # Implementation for adding phone number
    number = request.form.get("phone_number")
    if not number:
        return redirect(url_for("account.account"))

    user_service = UserService.add_phone_number(current_user.get_id(), number)

    return redirect(url_for("account.account"))
    

def reset_password_post(form) -> str:
    old_password = form.old_password.data
    new_password = form.new_password.data

    # Verify old password
    if not bcrypt.check_password_hash(current_user.password, old_password):
        return "Current password is incorrect"

    # Optional: prevent reusing same password
    if bcrypt.check_password_hash(current_user.password, new_password):
        return "New password cannot be the same as the old password"

    # Hash new password
    hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    # Update user
    current_user.password = hashed_password
    db.session.commit()

    return ""