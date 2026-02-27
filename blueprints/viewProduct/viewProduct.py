from flask import Blueprint, render_template, request, url_for, redirect
from extensions import conn, Products
from sqlalchemy import text
view_product_bp = Blueprint("viewProduct", __name__, static_folder="static", template_folder="templates")

@view_product_bp.route("/view/product", methods = ["GET", "POST"])
def viewProduct():
    error = request.args.get("error", None)
    product_id = request.args.get("id")
    product = None
    vendor = None
    images = []

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
                
        except Exception as e:
            error = "Error loading product."
    
    return render_template("viewProduct.html", product=product, vendor=vendor, images=images, error=error)