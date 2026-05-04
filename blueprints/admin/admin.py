from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from extensions import conn, db, required_roles
from sqlalchemy import text
from models import Vendors
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

# url_prefix makes /admin the root of this blueprint
admin_bp = Blueprint("admin", __name__, static_folder="static_admin",
                template_folder="templates_admin", 
                url_prefix="/admin")

required_roles_list = ["admin"]


def enabled_categories():
    return Vendors.query.all()


@admin_bp.route("/", methods=["GET"])
@login_required
def home():
    vendors = Vendors.query.order_by("store_name").all()

    return render_template("admin.html", vendors=vendors)