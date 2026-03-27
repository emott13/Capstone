from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import text
from extensions import conn
from extensions import db


search_bp = Blueprint('search', __name__, static_folder='static_search', template_folder='templates_search')

@search_bp.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        query = request.form.get('search', '').strip()
        category = request.form.get('category', '').strip()
        color = request.form.get('color', '').strip()
        min_price = request.form.get("min_price", "").strip()
        max_price = request.form.get("max_price", "").strip()
        
        params = {}
        if query:
            params['search'] = query
        if category:
            params['category'] = category
        if color:
            params['color'] = color
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        
        return redirect(url_for('search.search', **params))
    
    query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    color = request.args.get('color', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # Search filtering queries
    filter_categories = conn.execute(text(""" 
        SELECT category_name FROM product_categories;
    """)).fetchall()
    
    filter_colors = conn.execute(text("""
        SELECT hex_code FROM product_colors;
    """)).fetchall()
    

    sql = """
        SELECT DISTINCT p.*, v.store_name
        FROM products p
        LEFT JOIN product_category_map pcm
            ON p.product_id = pcm.product_id
        LEFT JOIN product_categories pc
            ON pcm.category_id = pc.category_id
        LEFT JOIN vendors v
            ON p.vendor_id = v.vendor_id
        WHERE 1=1
    """

    params = {}

    # Text search
    if query:
        sql += """
            AND (
                p.product_name ILIKE :query
                OR p.description ILIKE :query
                OR v.store_name ILIKE :query
            )
        """
        params["query"] = f"%{query}%"

    # Category filter
    if category:
        sql += " AND pc.category_name ILIKE :category"
        params["category"] = category

    # Color filter
    if color:
        sql += " AND EXISTS (SELECT 1 FROM product_colors pc2 WHERE pc2.product_id = p.product_id AND pc2.hex_code ILIKE :color)"
        params["color"] = color

    # Price filter
    if min_price:
        sql += " AND p.price >= :min_price"
        params["min_price"] = min_price

    if max_price:
        sql += " AND p.price <= :max_price"
        params["max_price"] = max_price

    sql += " ORDER BY p.created_at DESC"

    products = conn.execute(text(sql), params).fetchall()

    image_dict = getFirstTwoProductImages(products)

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        query=query,
        selected_category=category,
        selected_color=color,

        filter_categories=filter_categories,
        filter_colors=filter_colors,
        selected_min_price=min_price,
        selected_max_price=max_price
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