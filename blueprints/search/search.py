from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import text
from extensions import conn
from extensions import db


search_bp = Blueprint('search', __name__, static_folder='static_search', template_folder='templates_search')

@search_bp.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':
        query = request.form.get('search', '').strip()
        sortby = request.args.get('sortby')
        categories = request.form.getlist('categories')
        colors = request.form.getlist('colors')
        min_price = request.form.get("min_price", "").strip()
        max_price = request.form.get("max_price", "").strip()
        min_rating = request.form.get("min_rating", "").strip()
        max_rating = request.form.get("max_rating", "").strip()
        vendors = request.form.getlist('vendors')
        price = request.form.getlist('price')
        
        params = {}
        if query:
            params['search'] = query
        if categories:
            params['categories'] = ','.join(categories)
        if colors:
            params['colors'] = ','.join(colors)
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        if min_rating:
            params['min_rating'] = min_rating
        if max_rating:
            params['max_rating'] = max_rating
        if vendors:
            params['vendors'] = ','.join(vendors)
        if price:
            params['price'] = ','.join(price)
        if sortby:
            params['sortby'] = sortby
        
        return redirect(url_for('search.search', **params))
    
    query = request.args.get('search', '').strip()
    categories_str = request.args.get('categories', '').strip()
    colors_str = request.args.get('colors', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_rating = request.args.get('min_rating')
    max_rating = request.args.get('max_rating')
    sortby = request.args.get('sortby')
    selected_categories = categories_str.split(',') if categories_str else []
    selected_colors = colors_str.split(',') if colors_str else []
    selected_vendors_str = request.args.get('vendors', '').strip()
    selected_vendors = selected_vendors_str.split(',') if selected_vendors_str else []

    # Search filtering queries
    filter_categories = conn.execute(text(""" 
        SELECT category_name FROM product_categories;
    """)).fetchall()
    
    filter_colors = conn.execute(text("""
        SELECT hex_code FROM product_colors;
    """)).fetchall()
    
    filter_vendors = conn.execute(text("""
        SELECT DISTINCT store_name FROM vendors;
    """)).fetchall()
    

    sql = """ 
        SELECT DISTINCT p.*, v.store_name, (SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = p.product_id) as average_rating, (SELECT COUNT(*) FROM reviews WHERE product_id = p.product_id) as review_count
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
    if selected_categories:
        placeholders = ','.join([f':cat{i}' for i in range(len(selected_categories))])
        sql += f" AND pc.category_name IN ({placeholders})"
        for i, cat in enumerate(selected_categories):
            params[f"cat{i}"] = cat

    # Color filter
    if selected_colors:
        placeholders = ','.join([f':col{i}' for i in range(len(selected_colors))])
        sql += f" AND EXISTS (SELECT 1 FROM product_colors pc2 WHERE pc2.product_id = p.product_id AND pc2.hex_code IN ({placeholders}))"
        for i, col in enumerate(selected_colors):
            params[f"col{i}"] = col

    # Vendor filter
    if selected_vendors:
        placeholders = ','.join([f':ven{i}' for i in range(len(selected_vendors))])
        sql += f" AND v.store_name IN ({placeholders})"
        for i, ven in enumerate(selected_vendors):
            params[f"ven{i}"] = ven

    # Price filter
    if min_price:
        sql += " AND p.price >= :min_price"
        params["min_price"] = min_price

    if max_price:
        sql += " AND p.price <= :max_price"
        params["max_price"] = max_price

    # Rating filter
    if min_rating:
        sql += " AND (SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = p.product_id) >= :min_rating"
        params["min_rating"] = min_rating

    if max_rating:
        sql += " AND (SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE product_id = p.product_id) <= :max_rating"
        params["max_rating"] = max_rating

    # Order by
    if sortby == "a-z":
        order_by = "p.product_name ASC"
    elif sortby == "z-a":
        order_by = "p.product_name DESC"
    elif sortby == "low-to-high":
        order_by = "p.price ASC"
    elif sortby == "high-to-low":
        order_by = "p.price DESC"
    else:
        order_by = "p.created_at DESC"
    sql += f" ORDER BY {order_by}"

    products = conn.execute(text(sql), params).fetchall()

    image_dict = getFirstTwoProductImages(products)

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        query=query,
        selected_categories=selected_categories,
        selected_colors=selected_colors,
        selected_vendors=selected_vendors,

        filter_categories=filter_categories,
        filter_colors=filter_colors,
        filter_vendors=filter_vendors,
        selected_min_price=min_price,
        selected_max_price=max_price,
        selected_min_rating=min_rating,
        selected_max_rating=max_rating,
        sortby=sortby
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