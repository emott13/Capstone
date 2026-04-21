# search/routes.py
from flask import Blueprint, render_template, request, redirect, url_for
from services.SearchService import search_products, get_filter_data

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
