from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import conn
from sqlalchemy import text
home_bp = Blueprint("home", __name__, static_folder="static_home",
                  template_folder="templates_home")

@home_bp.route("/home", methods=["GET", "POST"])
def home():
    # get products categories to display on home page
    productsCategories = conn.execute(text("SELECT category_name FROM product_categories;")).fetchall()
    return render_template("home.html", productsCategories=productsCategories)