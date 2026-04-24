from flask import Blueprint, redirect, render_template, url_for
from extensions import conn
from sqlalchemy import text
from extensions import db
from models import ProductCategories
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, RadioField, DecimalField, SelectMultipleField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

# url_prefix makes /vendor the root of this blueprint
vendor_bp = Blueprint("vendor", __name__, static_folder="static_vendor",
                template_folder="templates_vendor", 
                url_prefix="/vendor")

def enabled_categories():
    return ProductCategories.query.all()

class CreateProductForm(FlaskForm):    
    name = StringField('Product Name',
        validators=[
            InputRequired(), 
            Length(max=100),
        ])
    desc = TextAreaField('Description',
        validators=[
            InputRequired(), 
            Length(max=1024),
        ])
    price = DecimalField('Price',
        validators=[
            InputRequired(), 
            Regexp(regex="^[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?$")
        ])
    categories = QuerySelectMultipleField('Categories',
        query_factory=enabled_categories,
        get_label="category_name",
        validators=[

        ])
    specs = StringField('Specifications',
        validators=[
            Length(max=255),
        ])
    colors = StringField('Colors',
        validators=[
            Length(min=6, max=7),
        ])
    images = StringField('Images',
        validators=[
            Length(max=255),
        ])
    submit = SubmitField('Sign Up')

"""
Products Database Format
products:              product_id   vendor_id      product_name 
                       description  price
product_categories:    category_id  category_name  category_image
product_cagegory_map:  product_id   category_id
product_specs:         spec_id      product_id     specification
product_colors:        color_id     product_id     hex_code
product_images:        image_id     product_id     image_url
"""

@vendor_bp.route("/", methods=["GET", "POST"])
def vendor():
    create_form = CreateProductForm()

    if create_form.validate_on_submit():
        error = create_post(create_form)

    return render_template("vendor.html", create_form=create_form,
    )

def create_post(create_form: CreateProductForm) -> str:
    return redirect(url_for("vendor.vendor"))