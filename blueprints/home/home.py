from flask import Blueprint, render_template, jsonify
from extensions import conn
from sqlalchemy import text
from extensions import db
from models import Products, ProductCategories

from ml.inference.popular import get_popular_products
home_bp = Blueprint("home", __name__, static_folder="static_home",
                  template_folder="templates_home")

@home_bp.route("/home", methods=["GET"])
def home():
    # Get categories
    categories = ProductCategories.query.all()

    # Get product IDs from recommender
    product_ids = get_popular_products(limit=10)

    # Get products
    products = (
        db.session.query(Products)
        .filter(Products.product_id.in_(product_ids))
        .all()
    )

    # Preserve order of popularity
    products_map = {p.product_id: p for p in products}
    ordered_products = [products_map[pid] for pid in product_ids if pid in products_map]
    print('ORDERED PRODUCTS', ordered_products)


    return render_template(
        "home.html",
        categories=categories,
        products=ordered_products
    )
