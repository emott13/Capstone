from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user
from extensions import conn, db
from models import Products, Reviews, ProductCategories
from sqlalchemy import text
from repositories.ReviewRepository import ReviewRepository
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, RadioField)
from wtforms.validators import InputRequired, Length
from flask_login import current_user, login_required
from ml.inference.also_bought import get_also_bought
from ml.inference.recommend import recommend_for_user

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
def viewProduct(error=None):
    if error == None:
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
    review_exists = bool(
        Reviews.query.filter(Reviews.customer_id == current_user.get_id()).first())

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


    # --- Customers Also Bought These Products --- #

    also_bought_ids = get_also_bought(product_id)

    also_bought_products = (
        db.session.query(Products)
        .filter(Products.product_id.in_(also_bought_ids))
        .all()
    )

    # --- Related Products --- #
    
    # Step 1: get the product
    product = db.session.get(Products, product_id)

    if not product:
        return []

    # Step 2: get category IDs for this product
    category_ids = [c.category_id for c in product.categories]

    if not category_ids:
        return []

    # Step 3: find other products with ANY of those categories
    related_products = (
        db.session.query(Products)
        .join(Products.categories)  # join through relationship
        .filter(ProductCategories.category_id.in_(category_ids))
        .filter(Products.product_id != product_id)  # exclude itself
        .distinct()
        .all()
    )

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        user_products_ids = recommend_for_user(user_id, 8)
        user_products = (
            db.session.query(Products)
            .filter(Products.product_id.in_(user_products_ids))
            .all()
        )

        return render_template("viewProduct.html", product=product, vendor=vendor, 
                           images=images, color=color, spec=spec, error=error, 
                           reviews=reviews, reviews_filtered=reviews_filtered,
                           review_sort=review_sort, review_filter=review_filter,
                           also_bought=also_bought_products, related_products=related_products,
                           user_products=user_products)
    
    return render_template("viewProduct.html", product=product, product_id=product_id,
                           vendor=vendor, images=images, color=color, spec=spec,
                           error=error, reviews=reviews,
                           reviews_filtered=reviews_filtered,
                           review_sort=review_sort, review_filter=review_filter,
                           create_review_form=create_review_form,
                           review_exists=review_exists,
                           also_bought=also_bought_products,
                           related_products=related_products,)

@login_required
@view_product_bp.route("/create/review/<int:product_id>", methods=["POST"])
def createReview(product_id):
    rating = request.form['rating']
    title = request.form['title']
    desc = request.form['desc']

    # error checks
    error = ""
    # unique check
    duplicate = Reviews.query.filter(Reviews.customer_id == current_user.get_id()).first()
    if duplicate:
        error = "Review already exists" 
    
    if not error:
        # add review to database
        review = Reviews(product_id=product_id, customer_id=current_user.get_id(),
                         rating=rating, title=title, description=desc)
        try:
            db.session.add(review)         
            db.session.commit()
        except Exception as exc:
            print(f"Error: {exc}")
            error = "Unknown error"

    print(error)
    return redirect(url_for('viewProduct.viewProduct', id=product_id, error=error) + '#reviews')

@login_required
@view_product_bp.route("/delete/review/<int:product_id>", methods=["POST"])
def deleteReview(product_id):
    query = Reviews.query.filter(Reviews.customer_id == current_user.get_id())

    # error checks
    error = ""
    # unique check
    duplicate = query.first()
    if not duplicate:
        error = "Review does not exist" 
    
    if not error:
        # delete customer review
        try:
            query.delete()
            db.session.commit()
        except Exception as exc:
            print(f"Error: {exc}")
            error = "Unknown error"

    print(error)
    return redirect(url_for('viewProduct.viewProduct', id=product_id, error=error) + '#reviews')
