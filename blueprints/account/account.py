from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from sqlalchemy import text
from wtforms import PasswordField, SubmitField, StringField
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

class VendorStoreNameForm(FlaskForm):
    store_name = StringField('New Store Name',
        # default=db.session.execute(
        #     text("SELECT store_name FROM vendors where vendor_id = :vendor_id"),
        #          {"vendor_id": current_user.get_id()}),
        validators=[
            InputRequired(),
            Length(max=100)
        ])

    submit = SubmitField('Set Store Name')

@account_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    customer_id = current_user.get_id()

    # get user information
    user = Users.query.get(customer_id)

    for phone in user.phone_numbers:
        print("phone!   ", phone.phone_number)

    redirect = None
    form = ResetPasswordForm()
    vendor_store_form = VendorStoreNameForm()
    current_store_name = ""
    if current_user.has_role("vendor"):
        current_store_name = db.session.execute(
            text("SELECT store_name FROM vendors WHERE vendor_id = :vendor_id"),
                 {"vendor_id": current_user.get_id()}).one()[0]

    error = None
    success = None

    if form.validate_on_submit():
        error = reset_password_post(form)
        if not error:
            success = "Password updated successfully"
    elif vendor_store_form and vendor_store_form.validate_on_submit():
        redirect = vendor_store_post(vendor_store_form)

    if redirect:
        return redirect

    return render_template(
        "account.html",
        user=user,
        form=form,  
        error=error,
        success=success,
        vendor_store_form=vendor_store_form,
        current_store_name=current_store_name,
    )

@account_bp.route("/account/phone", methods=["POST"])
def add_phone_number():
    # Implementation for adding phone number
    number = request.form.get("phone_number")
    if not number:
        return redirect(url_for("account.account"))

    user_service = UserService.add_phone_number(current_user.get_id(), number)

    return redirect(url_for("account.account"))
    

def reset_password_post(form: ResetPasswordForm) -> str:
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

def vendor_store_post(store_form: VendorStoreNameForm) -> str:
    # new store name
    store_name = store_form.store_name.data

    # Update store name
    db.session.execute(
        text("UPDATE vendors SET store_name = :store_name WHERE vendor_id = :vendor_id"),
             {"store_name": store_name, "vendor_id": current_user.get_id()})
    db.session.commit()

    return redirect(url_for("account.account"))