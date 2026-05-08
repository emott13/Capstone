from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length
from extensions import conn, db
from models import Products, Reviews, ProductCategories, Promotion, PromotionTarget
from sqlalchemy import text
from repositories.ReviewRepository import ReviewRepository
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, RadioField)
from wtforms.validators import InputRequired, Length
from flask_login import current_user, login_required
from ml.inference.also_bought import get_also_bought
from ml.inference.recommend import recommend_for_user
from services.WishlistService import WishlistService
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime
from sqlalchemy import or_, and_



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
def viewProduct(error=None, product_id=None, success=None):
    if error == None:
        error = request.args.get("error", None)
    if success == None:
        success = request.args.get("success", None)
    if product_id is None:
        product_id = request.args.get("id")

    # check if product exists
    if not Products.query.filter(
        Products.product_id == product_id).first():
        return redirect(url_for("home.home"))

    # second arg is default value
    review_sort = request.args.get("review-sort", "positive") 
    review_filter = request.args.get("review-filter", "all")
    product = None
    vendor = None
    images = []
    colors = []
    specs = []
    # contains an array of Reviews objects with the correct product_id
    # and other data
    reviews = ReviewRepository(product_id)
    reviews_filtered = ReviewRepository(product_id, sort=review_sort, filter=review_filter)
    create_review_form = CreateReviewForm()
    review_exists = bool(
        Reviews.query.filter(Reviews.customer_id == current_user.get_id())
            .filter(Reviews.product_id == product_id).first())

    if product_id:
        try:
            product = (
                db.session.query(Products)
                .options(
                    selectinload(Products.specs),
                    selectinload(Products.colors),
                    selectinload(Products.images),
                    selectinload(Products.categories),
                    selectinload(Products.vendor)
                )
                .filter(
                    Products.product_id == product_id
                )
                .first()
            )
                
        except Exception as error:
            error = "Error loading product."

    print("PRODUCT TESTING: ", product.vendor.store_name)
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

    # Step 2: get category IDs for this product
    category_ids = [c.category_id for c in product.categories]

    # Step 3: find other products with ANY of those categories
    related_products = (
        db.session.query(Products)
        .join(Products.categories)  # join through relationship
        .filter(ProductCategories.category_id.in_(category_ids))
        .filter(Products.product_id != product_id)  # exclude itself
        .distinct()
        .all()
    )

    # --- Product Promotions --- #

    now = datetime.utcnow()

    promotions = (
        db.session.query(Promotion)
        .join(Promotion.targets)  # joins PromotionTarget
        .filter(
            # Active promotions
            Promotion.is_active.is_(True),
            or_(Promotion.starts_at == None, Promotion.starts_at <= now),
            or_(Promotion.ends_at == None, Promotion.ends_at >= now),

            # Match ANY target type
            or_(
                PromotionTarget.product_id == product.product_id,
                PromotionTarget.vendor_id == product.vendor_id,
                PromotionTarget.category_id.in_(category_ids) if category_ids else False
            )
        )
        .options(joinedload(Promotion.targets))
        .distinct()
        .all()
    )

    create_review_form = CreateReviewForm()
    user_products = None

    if current_user.is_authenticated and category_ids:
        user_id = current_user.get_id()
        user_products_ids = recommend_for_user(user_id, 8)
        user_products = (
            db.session.query(Products)
            .filter(Products.product_id.in_(user_products_ids))
            .all()
        )

    return render_template("viewProduct.html", product=product,
        product_id=product_id, success=success, reviews=reviews, promotions=promotions,
        reviews_filtered=reviews_filtered, review_sort=review_sort,
        review_filter=review_filter, 
        also_bought=also_bought_products, 
        related_products=related_products,
        create_review_form=create_review_form,
        review_exists=review_exists, 
        user_products=user_products,
    )

@login_required
@view_product_bp.route("/create/review/<int:product_id>", methods=["POST"])
def createReview(product_id):
    rating = request.form['rating']
    title = request.form['title']
    desc = request.form['desc']

    # error checks
    error = ""
    # unique check
    duplicate = (Reviews.query
        .filter(Reviews.customer_id == current_user.get_id())
        .filter(Reviews.product_id == product_id).first())
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
    query = (Reviews.query
        .filter(Reviews.customer_id == current_user.get_id())
        .filter(Reviews.product_id == product_id).first())

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

@login_required
@view_product_bp.route("/add_to_wishlist/<int:product_id>", methods=["POST"])
def add_to_wishlist(product_id):
    try:
        quantity = int(request.form.get("quantity", 1))
        if quantity <= 0:
            quantity = 1
        
        WishlistService.add_item(customer_id=current_user.get_id(), product_id=product_id, quantity=quantity)
        return redirect(url_for('viewProduct.viewProduct', id=product_id, success="Product added to wishlist!"))
    except Exception as exc:
        return redirect(url_for('viewProduct.viewProduct', id=product_id, error="Failed to add product to wishlist."))
