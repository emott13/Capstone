from repositories.SearchRepository import (
    fetch_products,
    fetch_categories,
    fetch_colors,
    fetch_vendors,
    fetch_first_two_images
)

def search_products(filters):
    # normalize price filters
    min_price = filters.get("min_price", [""])[0]
    max_price = filters.get("max_price", [""])[0]

    min_price = int(float(min_price) * 100) if min_price else 0
    max_price = int(float(max_price) * 100) if max_price else 100000

    filters["min_price"] = [min_price]
    filters["max_price"] = [max_price]

    products = fetch_products(filters)
    image_dict = get_first_two_product_images(products)

    return products, image_dict


def get_filter_data():
    categories = fetch_categories()
    colors = fetch_colors()
    vendors = fetch_vendors()

    return {
        "filter_categories": categories,
        "filter_colors": colors,
        "filter_vendors": vendors,
    }

def get_first_two_product_images(products):

    if not products:
        return {}

    images = fetch_first_two_images(products)

    image_dict = {}
    for img in images:
        image_dict.setdefault(img.product_id, []).append(img)

    return image_dict