from flask import Blueprint, render_template, request, url_for, redirect
from extensions import conn
from models import Products
from sqlalchemy import text
from repositories.ReviewRepository import ReviewRepository
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, RadioField)
from wtforms.validators import InputRequired, Length

view_product_bp = Blueprint("viewProduct", __name__, static_folder="viewProduct_static", template_folder="templates")

class CreateReviewForm(FlaskForm):    
    title = StringField('Title',
        validators=[
            Length(max=100),
        ])
    desc = TextAreaField('Description',
        validators=[
            Length(max=1024),
        ])
    rating = RadioField('Rating',
        choices=[
            ('1'), ('2'), ('3'), ('4'), ('5'),
        ],
        validators=[
            InputRequired(),
        ])
    submit = SubmitField('Create')

@view_product_bp.route("/view/product", methods = ["GET", "POST"])
def viewProduct():
    error = request.args.get("error", None)
    product_id = request.args.get("id")
    # second arg is default value
    review_sort = request.args.get("review-sort", "positive") 
    review_filter = request.args.get("review-filter", "all")
    product = None
    vendor = None
    images = []
    color = None
    spec = None
    # contains an array of Reviews objects with the correct product_id
    # and other data
    reviews = ReviewRepository(product_id)
    reviews_filtered = ReviewRepository(product_id, sort=review_sort, filter=review_filter)
    create_review_form = CreateReviewForm()

    if product_id:
        try:
            product = Products.query.get(product_id)
            if product:
                vendor_res = conn.execute(text("""
                    SELECT first_name, last_name, store_name
                    FROM users u JOIN vendors v
                    ON u.user_id = v.vendor_id
                    WHERE v.vendor_id = :vendor_id
                """), {"vendor_id": product.vendor_id}).fetchone()
                
                if vendor_res:
                    vendor = vendor_res

                images = conn.execute(text("""
                    SELECT image_url FROM product_images
                    WHERE product_id = :product_id
                    ORDER BY image_id
                """), {"product_id": product_id}).fetchall()

                color = conn.execute(text("""
                    SELECT hex_code FROM product_colors
                    WHERE product_id = :product_id
                    ORDER BY color_id
                """), {"product_id": product_id}).fetchone()

                spec = conn.execute(text("""
                    SELECT specification FROM product_specs
                    WHERE product_id = :product_id
                    ORDER BY spec_id
                """), {"product_id": product_id}).fetchone()
                
        except Exception as error:
            error = "Error loading product."
    
    return render_template("viewProduct.html", product=product, vendor=vendor, 
                           images=images, color=color, spec=spec, error=error, 
                           reviews=reviews, reviews_filtered=reviews_filtered,
                           review_sort=review_sort, review_filter=review_filter,
                           create_review_form=create_review_form)
