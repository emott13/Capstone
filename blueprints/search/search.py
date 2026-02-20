from flask import Blueprint, render_template, request
from sqlalchemy import text
from extensions import conn

search_bp = Blueprint('search', __name__, static_folder='static_search', template_folder='templates_search')

@search_bp.route('/search', methods=['GET'])
def search():

    query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    sql = """
        SELECT DISTINCT p.*
        FROM products p
        LEFT JOIN product_category_map pcm
            ON p.product_id = pcm.product_id
        LEFT JOIN product_categories pc
            ON pcm.category_id = pc.category_id
        WHERE 1=1
    """

    params = {}

    # Text search
    if query:
        sql += """
            AND (
                p.product_name ILIKE :query
                OR p.description ILIKE :query
            )
        """
        params["query"] = f"%{query}%"

    # Category filter
    if category:
        sql += " AND pc.category_name ILIKE :category"
        params["category"] = category

    sql += " ORDER BY p.created_at DESC"

    products = conn.execute(text(sql), params).fetchall()

    image_dict = getFirstTwoProductImages(products)

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        query=query,
        selected_category=category
    )

# filter through products and adjust whether they display in the UI
def filterProducts(products, formSearch=None):
    if not formSearch:
        return products

    filtered = []
    for product in products:
        if product.product_id in formSearch:
            filtered.append(product)

    return filtered


# query products from db
def getProducts():
    products = conn.execute(text("SELECT * FROM products")).fetchall()
    return products

# query first two product images for each product
def getFirstTwoProductImages(products):

    if not products:
        return {}

    product_ids = [p.product_id for p in products]

    images = conn.execute(
        text("""
            SELECT *
            FROM (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY product_id
                           ORDER BY image_id
                       ) AS rn
                FROM product_images
                WHERE product_id = ANY(:ids)
            ) ranked
            WHERE rn <= 2
        """),
        {"ids": product_ids}
    ).fetchall()

    image_dict = {}
    for img in images:
        image_dict.setdefault(img.product_id, []).append(img)

    return image_dict