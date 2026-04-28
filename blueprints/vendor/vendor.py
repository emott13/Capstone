from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from extensions import conn
from sqlalchemy import text
from extensions import db
from models import ProductCategories, ProductColors, ProductImages, ProductSpecs, Products
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

# url_prefix makes /vendor the root of this blueprint
vendor_bp = Blueprint("vendor", __name__, static_folder="static_vendor",
                template_folder="templates_vendor", 
                url_prefix="/vendor")

required_roles_list = ["vendor"]


def enabled_categories():
    return ProductCategories.query.all()

def required_roles(roles: list[str]) -> bool:
    for role in roles:
        if current_user.has_role(role):
            return True
    # user doesn't not have the role
    return False

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
    price = StringField('Price',
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
            Length(min=0, max=7),
        ])
    images = URLField('Images',
        validators=[
            Length(max=512),
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

@vendor_bp.route("/create-product", methods=["GET", "POST"])
@login_required
def create_product():
    if required_roles(required_roles_list) == False:
        return redirect(url_for("login.login"))

    error = None
    success = None
    form = CreateProductForm()

    if form.validate_on_submit():
        error = create_post(form)

        if not error:
            success = "Product now created!"

    return render_template("createProduct.html", 
        form=form, success=success, error=error
    )

def create_post(form: CreateProductForm) -> str:
    # create_form attributes
    # name   desc    price   categoies
    # specs  colors  images

    if form.validate_on_submit():
        price = form.price.data
        price = int(float(price)*100)
        product = Products(
            vendor_id=current_user.user_id, 
            product_name=form.name.data,
            description=form.desc.data,
            price=price
        )
        # loops though the list of strings and converts it into a list of models
        productSpecs = []
        for spec in request.form.getlist('specs'):
            if len(spec) > 0:
                productSpecs.append(ProductSpecs(specification=spec))
        # productSpecs = list(map(lambda spec: ProductSpecs(specification=spec), 
        #                         request.form.getlist('specs')))
        productColors = []
        for hex_code in request.form.getlist('colors'):
            if len(hex_code) == 6:
                productColors.append(ProductColors(hex_code="#" + hex_code))
            elif len(hex_code) == 7:
                productColors.append(ProductColors(hex_code=hex_code))
        productImages = []
        for url in request.form.getlist('images'):
            if len(url) > 0:
                ProductImages(image_url=url)

        # print(list(map(lambda c: c.image_url, productImages)))
        # print(list(map(lambda c: c.category_name, form.categories.data)))

        product.categories = list(form.categories.data)
        product.specs = productSpecs
        product.colors = productColors
        product.images = productImages
        try:
            db.session.add(product)
            db.session.commit()
        except Exception as exc:
            print(f"{__name__} had exception: {exc}")
            return "Unknown error"


    return ""