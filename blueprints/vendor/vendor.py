from flask import Blueprint, render_template
from extensions import conn
from sqlalchemy import text
from extensions import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, RadioField, DecimalField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError

vendor_bp = Blueprint("vendor", __name__, static_folder="static_vendor",
                  template_folder="templates_vendor")

class CreateProductForm(FlaskForm):    
    name = StringField('Product Name',
        validators=[
            InputRequired(), 
            Length(max=100),
        ])
    description = StringField('Description',
        validators=[
            InputRequired(), 
            Length(max=1024),
        ])
    price = DecimalField('Price',
        validators=[
            InputRequired(), 
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

@vendor_bp.route("/vendor", methods=["GET"])
def vendor():
    return render_template(
        "vendor.html",
    )
