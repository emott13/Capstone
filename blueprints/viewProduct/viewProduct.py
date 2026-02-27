from flask import Blueprint, render_template, request, url_for, redirect
view_product_bp = Blueprint("viewProduct", __name__, static_folder="viewProduct_static", template_folder="templates")

@view_product_bp.route("/view/product", methods = ["GET", "POST"])
def viewProduct():
    error = request.args.get("error", None)
    return render_template("viewProduct.html", error=error)