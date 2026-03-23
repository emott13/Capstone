from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from services.OrderService import OrderService
from repositories.OrderRepository import OrderRepository

order_bp = Blueprint(
    "order",
    __name__,
    static_folder="static_order",
    template_folder="templates_order"
)

@order_bp.route("/order", methods=["GET", "POST"])
@login_required
def order():

    if not current_user.has_role("customer"):
        return redirect(url_for("home.home"))

    customer_id = current_user.get_id()

    # --- CREATE ORDER ---
    if request.method == "POST":

        promo_code = request.form.get("promo_code")

        result = OrderService.checkout_cart(
            customer_id=customer_id,
            promo_code=promo_code
        )
        print("Checkout result:", result)

        return redirect(url_for("order.order"))

    # --- VIEW ORDERS ---
    orders = OrderRepository.get_customer_orders(customer_id)

    return render_template("order.html", orders=orders)