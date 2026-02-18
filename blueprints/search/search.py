from flask import Blueprint, render_template
from sqlalchemy import text
from extensions import conn

search_bp = Blueprint('search', __name__, static_folder='static_search', template_folder='templates_search')

@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    # get first two images for each product
    products = conn.execute(text("SELECT * FROM products")).fetchall()

    images = conn.execute(text("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY image_id) as rn
            FROM product_images
        ) ranked
        WHERE rn <= 2
    """)).fetchall()

    # organize images by product_id
    image_dict = {}
    for img in images:
        image_dict.setdefault(img.product_id, []).append(img)

    return render_template('search.html', products=products, image_dict=image_dict)