from flask import Blueprint, render_template, request, redirect, url_for
from services.SearchService import search_products, get_filter_data, get_first_two_product_images
from repositories.SearchRepository import fetch_products_by_ids
from ml.inference.best_selling import get_best_selling_products
from ml.inference.sale_products import get_sale_products

search_bp = Blueprint(
    'search',
    __name__,
    static_folder='static_search',
    template_folder='templates_search'
)

@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':

        # normalize lists + single values
        clean_params = {}

        def add_if_valid (k, v):
            if isinstance(v, list):
                if v:
                    clean_params[k] = v
        
        add_if_valid("search", request.form.get("search", "").strip())
        add_if_valid("categories", request.form.getlist("categories"))
        add_if_valid("colors", request.form.getlist("colors"))
        add_if_valid("vendors", request.form.getlist("vendors"))
        add_if_valid("min_price", request.form.getlist("min_price"))
        add_if_valid("max_price", request.form.getlist("max_price"))
        add_if_valid("min_rating", request.form.getlist("min_rating"))
        add_if_valid("max_rating", request.form.getlist("max_rating"))
        add_if_valid("sortby", request.form.getlist("sortby"))

        return redirect(url_for('search.search', **clean_params))

    filters = request.args.to_dict(flat=False)

    products, image_dict = search_products(filters)
    filter_data = get_filter_data()
    

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        selected_categories=filters.get("categories", []),
        selected_colors=filters.get("colors", []),
        selected_vendors=filters.get("vendors", []),
        selected_min_price=filters.get("min_price", [""])[0],
        selected_max_price=filters.get("max_price", [""])[0],
        selected_min_rating=filters.get("min_rating", [""])[0],
        selected_max_rating=filters.get("max_rating", [""])[0],
        sortby=filters.get("sortby", [""])[0],
        **filter_data
    )

@search_bp.route('/best-selling', methods=['GET', 'POST'])
def best_selling():
    
    filters = request.args.to_dict(flat=False)

    product_ids = get_best_selling_products()
    products = fetch_products_by_ids(product_ids)
    image_dict = get_first_two_product_images(products)
    filter_data = get_filter_data()
    

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        selected_categories=filters.get("categories", []),
        selected_colors=filters.get("colors", []),
        selected_vendors=filters.get("vendors", []),
        selected_min_price=filters.get("min_price", [""])[0],
        selected_max_price=filters.get("max_price", [""])[0],
        selected_min_rating=filters.get("min_rating", [""])[0],
        selected_max_rating=filters.get("max_rating", [""])[0],
        sortby=filters.get("sortby", [""])[0],
        **filter_data
    )

@search_bp.route('/sale', methods=['GET', 'POST'])
def sale():

    product_ids = get_sale_products()
    products = fetch_products_by_ids(product_ids)
    print('SALE products: ', products)
    image_dict = get_first_two_product_images(products)
    filter_data = get_filter_data()
    filters = request.args.to_dict(flat=False)

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        selected_categories=filters.get("categories", []),
        selected_colors=filters.get("colors", []),
        selected_vendors=filters.get("vendors", []),
        selected_min_price=filters.get("min_price", [""])[0],
        selected_max_price=filters.get("max_price", [""])[0],
        selected_min_rating=filters.get("min_rating", [""])[0],
        selected_max_rating=filters.get("max_rating", [""])[0],
        sortby=filters.get("sortby", [""])[0],
        **filter_data
    )