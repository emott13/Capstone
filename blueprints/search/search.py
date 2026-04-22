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
        clean_params = {
            "search": request.form.get("search", "").strip(),
            "categories": request.form.getlist("categories"),
            "colors": request.form.getlist("colors"),
            "vendors": request.form.getlist("vendors"),
            "min_price": request.form.get("min_price"),
            "max_price": request.form.get("max_price"),
            "min_rating": request.form.get("min_rating"),
            "max_rating": request.form.get("max_rating"),
            "sortby": request.form.get("sortby")
        }

        return redirect(url_for('search.search', **clean_params))

    filters = request.args.to_dict(flat=False)

    products, image_dict = search_products(filters)
    filter_data = get_filter_data()\
    

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        **filter_data,
        **filters
    )

@search_bp.route('/best-selling', methods=['GET', 'POST'])
def best_selling():
    
    filters = request.args.to_dict(flat=False)

    product_ids = get_best_selling_products()
    products = fetch_products_by_ids(product_ids)
    image_dict = get_first_two_product_images(products)
    filter_data = get_filter_data()\
    

    return render_template(
        "search.html",
        products=products,
        image_dict=image_dict,
        **filter_data,
        **filters
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
        **filter_data,
        **filters
    )