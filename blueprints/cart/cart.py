from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user
from extensions import db
from sqlalchemy import text
cart_bp = Blueprint("cart", __name__, static_folder="static_cart",
                  template_folder="templates_cart")

@cart_bp.route("/cart", methods=["GET", "POST"])
def cart():
    if not current_user.is_authenticated:
        return redirect(url_for("login.login"))
    if current_user.has_role("customer"):
        # --- POST --- #

        if request.method == "POST":
            # get customer id
            customer_id = current_user.get_id()
            # get cart_id for this customer
            cart_sql = """
                SELECT cart_id
                FROM carts
                WHERE customer_id = :customer_id
                """

            cart_result = db.session.execute(text(cart_sql), {"customer_id": customer_id}).fetchone()

            if not cart_result:
                return redirect(url_for('cart.cart'))
        
            cart_id = cart_result[0]

            # loop through form items
            for product_id, quantity in request.form.items():
                update_sql = """
                    UPDATE cart_items
                    SET quantity = :quantity
                    WHERE cart_id = :cart_id
                    AND product_id = :product_id
                    """
                
                db.session.execute(text(update_sql), {
                    "quantity": int(quantity),
                    "cart_id": cart_id,
                    "product_id": int(product_id)

                })

            db.session.commit() # save changes to db

            return redirect(url_for('cart.cart'))

        # --- GET --- #
            
        # get customer id
        customer_id = current_user.get_id()
        # for debugging
        print("the customer_id: ", customer_id)

        params = {}
        # selecting product name, quantity, and price to display in UI
        sql = '''
            SELECT p.product_name, ci.quantity, p.price, p.product_id
            FROM carts c
            INNER JOIN cart_items ci ON c.cart_id = ci.cart_id
            INNER JOIN products p ON ci.product_id = p.product_id
            WHERE c.customer_id = :customer_id
            '''
        # where customer_id matches
        params["customer_id"] = customer_id
        # execute
        cartItems = db.session.execute(text(sql), params).fetchall()
        # for debugging
        print("cart items: ", cartItems)

        # change price from cents to dollars and map items
        cartItemsMap = []
        prices = []
        for item in cartItems:
            name = item[0]
            quantity = int(item[1])
            
            price = int(item[2] * item[1]) # multiply price x quantity
            prices.append(price) # append total

            id = item[3]

                # map
            cartItemsMap.append({
                'name': name,
                'quantity': quantity,
                'price': price,
                'id': id
            })

        # get totals
        subtotal = 0
        tax = 0
        total = 0
            
        # subtotal is sum of all elements in prices
        for price in prices:
            subtotal += price

            # assumed 6% sales tax rate
        tax = round(float(subtotal * 0.06))
        total = tax + subtotal

        totals = [subtotal, tax, total]
                
        return render_template("cart.html", cartItems = cartItemsMap, totals = totals) 
    else:
        return render_template('login.html')
    