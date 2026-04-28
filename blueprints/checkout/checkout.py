from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from repositories.CartRepository import CartRepository
from services.OrderPricingService import OrderPricingService
from services.OrderService import OrderService
from services.PaymentService import PaymentService
from services.CartService import CartService


checkout_bp = Blueprint("checkout", __name__, template_folder="templates_checkout")

@checkout_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    if not current_user.is_authenticated or not current_user.has_role("customer"):
        return redirect(url_for("login.login"))
    
    if request.method == "POST":
        
        customer_id = current_user.get_id()

        promo_code = session.get("manual_promo_code")

        cart = CartService.get_cart(customer_id, promo_code)

        if not cart or not cart.get("items"):
            # Either the cart doesn't exist, or it has no items
            flash("Your cart is empty. Please add items before checking out.","error")
            return redirect(url_for("cart.cart"))

        return render_template(
            "checkout.html",
            cartItems=cart["items"],
            subtotal=cart["subtotal"],
            discounts=cart["discounts"],
            tax=cart["tax"],
            total=cart["total"],
            promotions=cart["applied_promotions"]
        )
    
# handles order address
@checkout_bp.route("/address", methods=["GET", "POST"])
def address():
    if not current_user.is_authenticated or not current_user.has_role("customer"):
        return redirect(url_for("login.login"))
    
    user_id = current_user.get_id()

    if request.method == "POST":
        selected_address_id = request.form.get("address_id")

        if selected_address_id:
            CartService.set_cart_address(user_id, selected_address_id)
        else:
            address_data = {
                "add1": request.form.get("add1"),
                "add2": request.form.get("add2"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip"),
                "country": request.form.get("country"),
            }
            CartService.set_cart_address(user_id, address_data=address_data)

        return redirect(url_for("checkout.payment"))
        
    addresses = CartService.get_user_addresses(user_id)
    return render_template("address.html", addresses=addresses)

# handles order payment
@checkout_bp.route("/payment", methods=["POST", "GET"])
def payment():
    if not current_user.is_authenticated:
        return redirect(url_for("login.login"))
    if not current_user.has_role("customer"):
        return redirect(url_for("login.login"))
    
    # regex to handle card number formatting (e.g. "1234 5678 9012 3456" or "1234567890123456")

    # if card number is invalid, flash error and redirect back to checkout
    # if card number is valid, process payment and create order
    if request.method == "POST":

        customer_id = current_user.get_id()
        promo_code = request.form.get("promo_code")
        items=CartRepository.get_cart(customer_id)

        amount = OrderPricingService.calculate_cart(
            items=items, 
            customer_id=customer_id,
            promo_code=promo_code
        )   

        session["order_amount"] = amount

        # result = OrderService.checkout_cart(
        #     customer_id=customer_id,
        #     promo_code=promo_code
        # )
        # print("Checkout result:", result)

        # PaymentService.process_payment(
        #     customer_id=customer_id,
        #     amount=amount,
        #     order_id=result
        # )

        return redirect(url_for("checkout.confirmation"))
    
    return render_template("payment.html")
    
# handles order confirmation
@checkout_bp.route("/confirmation", methods=["GET", "POST"])
def confirmation():
    if not current_user.is_authenticated:
        return redirect(url_for("login.login"))
    
    user_id = current_user.get_id()
    promo_code = session.get("manual_promo_code")
    cartDict = CartService.get_cart(user_id, promo_code)
    cart = CartService.get_cart_by_user_id(user_id)

    if request.method == "POST":
        cart_id = cart.cart_id

        result = OrderService.checkout_cart(
            customer_id=user_id,
            promo_code=promo_code
        )
        print("Checkout result:", result)

        amount = session.get("order_amount")
        PaymentService.process_payment(
            customer_id=user_id,
            amount=amount,
            order_id=result
        )
        return redirect(url_for("order.order"))

    # print("CART", cart)
    return render_template("confirmation.html", 
        subtotal=cartDict["subtotal"],
        discounts=cartDict["discounts"],
        tax=cartDict["tax"],
        total=cartDict["total"],
        promotions=cartDict["applied_promotions"],
        cart=cart
    )
