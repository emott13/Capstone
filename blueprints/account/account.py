from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo
from extensions import bcrypt, db
from services.UserService import UserService

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
    user = UserService.get_user_by_id(customer_id)

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