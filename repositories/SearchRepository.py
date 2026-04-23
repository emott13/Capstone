# search/repository.py
from sqlalchemy import text
from extensions import conn


def fetch_products(filters):
    sql = """
        SELECT DISTINCT p.*, v.store_name,
            (SELECT COALESCE(AVG(rating), 0)
             FROM reviews WHERE product_id = p.product_id) as average_rating,
            (SELECT COUNT(*)
             FROM reviews WHERE product_id = p.product_id) as review_count
        FROM products p
        LEFT JOIN product_category_map pcm ON p.product_id = pcm.product_id
        LEFT JOIN product_categories pc ON pcm.category_id = pc.category_id
        LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
        WHERE 1=1
    """

    params = {}

    query = filters.get("search", [""])[0]
    if query:
        sql += """
            AND (
                p.product_name ILIKE :query
                OR p.description ILIKE :query
                OR v.store_name ILIKE :query
            )
        """
        params["query"] = f"%{query}%"

    # Categories
    categories = filters.get("categories", [])
    if categories:
        placeholders = ','.join([f':cat{i}' for i in range(len(categories))])
        sql += f" AND pc.category_name IN ({placeholders})"
        for i, cat in enumerate(categories):
            params[f"cat{i}"] = cat

    # Colors
    colors = filters.get("colors", [])
    if colors:
        placeholders = ','.join([f':col{i}' for i in range(len(colors))])
        sql += f"""
            AND EXISTS (
                SELECT 1 FROM product_colors pc2
                WHERE pc2.product_id = p.product_id
                AND pc2.hex_code IN ({placeholders})
            )
        """
        for i, col in enumerate(colors):
            params[f"col{i}"] = col

    # Vendors
    vendors = filters.get("vendors", [])
    if vendors:
        placeholders = ','.join([f':ven{i}' for i in range(len(vendors))])
        sql += f" AND v.store_name IN ({placeholders})"
        for i, ven in enumerate(vendors):
            params[f"ven{i}"] = ven

    # Price
    if filters.get("min_price"):
        sql += " AND p.price >= :min_price"
        params["min_price"] = filters["min_price"][0]

    if filters.get("max_price"):
        sql += " AND p.price <= :max_price"
        params["max_price"] = filters["max_price"][0]

    # Sorting
    sort_map = {
        "a-z": "p.product_name ASC",
        "z-a": "p.product_name DESC",
        "price-low-high": "p.price ASC",
        "price-high-low": "p.price DESC",
        "rating-low-high": "average_rating ASC, review_count ASC",
        "rating-high-low": "average_rating DESC, review_count DESC"
    }

    sortby = filters.get("sortby", [""])[0]
    order_by = sort_map.get(sortby, "p.created_at DESC")

    sql += f" ORDER BY {order_by}"

    return conn.execute(text(sql), params).fetchall()

def fetch_products_by_ids(product_ids):
    if not product_ids:
        return []

    placeholders = ','.join([f':id{i}' for i in range(len(product_ids))])
    
    sql = f"""
        SELECT DISTINCT p.*, v.store_name,
            (SELECT COALESCE(AVG(rating), 0)
             FROM reviews WHERE product_id = p.product_id) as average_rating,
            (SELECT COUNT(*)
             FROM reviews WHERE product_id = p.product_id) as review_count
        FROM products p
        LEFT JOIN product_category_map pcm ON p.product_id = pcm.product_id
        LEFT JOIN product_categories pc ON pcm.category_id = pc.category_id
        LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
        WHERE p.product_id IN ({placeholders})
    """

    params = {f"id{i}": pid for i, pid in enumerate(product_ids)}

    return conn.execute(text(sql), params).fetchall()

def fetch_categories():
    return conn.execute(text("SELECT category_name FROM product_categories")).fetchall()

def fetch_colors():
    return conn.execute(text("SELECT hex_code FROM product_colors")).fetchall()

def fetch_vendors():
    return conn.execute(text("SELECT DISTINCT store_name FROM vendors")).fetchall()

def fetch_first_two_images(products):
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

    return images
