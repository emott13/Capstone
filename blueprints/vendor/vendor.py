from flask import Blueprint, redirect, render_template, request, url_for, abort
from flask_login import login_required, current_user
from extensions import conn, db, required_roles
from sqlalchemy import text
from models import ProductCategories, ProductColors, ProductImages, ProductSpecs, Products, Vendors
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

# url_prefix makes /vendor the root of this blueprint
vendor_bp = Blueprint("vendor", __name__, static_folder="static_vendor",
                template_folder="templates_vendor", 
                url_prefix="/vendor")

required_roles_list = ["vendor", "admin"]


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

@vendor_bp.route("/", methods=["GET"])
@login_required
def home():
    if required_roles(required_roles_list) == False:
        return redirect(url_for("login.login"))

    success = request.args.get("success", None)
    # to pass args (vendor_id) to the CRUD pages if 
    # the arg is already specified
    url_args = dict()

    vendor: Vendors = get_vendor(url_args, request.args.get('vendor_id'))
    
    # if the user is only admin and there is no vendor_id in the URL
    # or something else goes wrong, then 404
    if vendor == None:
        abort(404)
    
    products: list[Products] = vendor.products

    return render_template("vendor.html", 
                           products=products, url_args=url_args,
                           success=success)

@vendor_bp.route("/create-product", methods=["GET", "POST"])
@login_required
def create_product():
    if required_roles(required_roles_list) == False:
        return redirect(url_for("login.login"))

    url_args = dict()
    error = None
    success = None

    vendor: Vendors = get_vendor(url_args, request.args.get('vendor_id'))

    if not vendor:
        abort(404)

    form = CreateProductForm()

    if form.validate_on_submit():
        error = create_post(form, vendor)

        if not error:
            success = "Product now created!"

    return render_template("createProduct.html", 
        form=form, success=success, error=error, url_args=url_args,
    )

@vendor_bp.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id: int = None):
    if required_roles(required_roles_list) == False:
        return redirect(url_for("login.login"))

    return render_template("editProduct.html",
                           product_id=product_id)

@vendor_bp.route("/delete-product/<int:product_id>", methods=["GET", "POST"])
@login_required
def delete_product(product_id: int = None):
    if required_roles(required_roles_list) == False:
        return redirect(url_for("login.login"))

    product: Products = Products.query.where(
        text(f"product_id = {product_id}")).one_or_none()

    url_args: dict = {}
    vendor: Vendors = get_vendor(url_args, request.args.get("vendor_id"))    

    if  (not product or 
         not current_user.has_role("admin") and
         vendor.vendor_id != product.vendor_id
        ):
        abort(404)

    if request.method == "POST":
        db.session.delete(product)
        db.session.commit()

        return redirect(url_for('vendor.home', 
            success="Product deleted successfully",
            **url_args))

    print(f"url_args = {url_args}")
    return render_template("deleteProduct.html",
        product_id=product_id, product=product, url_args=url_args)

def get_vendor(url_args: dict, request_vendor_id: None) -> Vendors:
    """
    Returns the vendor. If the user is an admin then it returns
    the vendor with the correct request vendor_id
    Returns None if a vendor could not be found
    Also adds to url_args if the arg exists and the user is an admin
    """
    vendor: Vendors = None
    if current_user.has_role("admin") and request_vendor_id:
        vendor_id = request_vendor_id
        vendor = Vendors.query.filter(text(
            f"vendor_id = {vendor_id}")).one_or_404()
        
        url_args['vendor_id'] = vendor_id

    if current_user.has_role("vendor") and vendor == None:
        vendor = current_user.get_vendor()
    
    return vendor

def create_post(form: CreateProductForm, vendor: Vendors) -> str:
    # create_form attributes
    # name   desc    price   categoies
    # specs  colors  images

    if form.validate_on_submit():
        vendor_id = vendor.vendor_id

        # if current_user.has_role("admin") and request.args.get("vendor_id"):
        #     print("admin vendor_id")
        #     vendor_id = request.args.get("vendor_id")
        # # check if vendor_id exists in vendor DB
        # if not Vendors.query.filter(Vendors.vendor_id == vendor_id).first():
        #     return "Vendor does not exist"

        price = form.price.data
        price = int(float(price)*100)
        product = Products(
            vendor_id=vendor_id,
            product_name=form.name.data,
            description=form.desc.data,
            price=price
        )
        # loops though the list of strings and converts it into a list of models
        productSpecs = []
        for spec in request.form.getlist('specs'):
            if len(spec) > 0:
                productSpecs.append(ProductSpecs(specification=spec))
        productColors = []
        for hex_code in request.form.getlist('colors'):
            if len(hex_code) == 6:
                productColors.append(ProductColors(hex_code="#" + hex_code))
            elif len(hex_code) == 7:
                productColors.append(ProductColors(hex_code=hex_code))
        productImages = []
        for url in request.form.getlist('images'):
            if len(url) > 0:
                productImages.append(ProductImages(image_url=url))

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
