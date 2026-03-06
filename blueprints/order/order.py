from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user
from extensions import db
from sqlalchemy import text
order_bp = Blueprint("order", __name__, static_folder="static_order",
                  template_folder="templates_order")

@order_bp.route("/order", methods=["GET", "POST"])
def order():
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

            # create order from cart items (default pending order status)
            create_order_sql = """
                INSERT INTO orders (customer_id, order_date, order_subtotal, order_tax, order_total, order_status)
                VALUES (:customer_id, NOW(), :order_subtotal, :order_tax, :order_total, 'pending')
                RETURNING order_id
            """

            # get cart total
            # cart_total_sql = """
            #     SELECT SUM(ci.quantity * p.price) AS total
            #     FROM cart_items ci
            #     JOIN products p ON ci.product_id = p.product_id
            #     WHERE ci.cart_id = :cart_id
            # """

            # cart_total_result = db.session.execute(
            #     text(cart_total_sql),
            #     {"cart_id": cart_id}
            # ).fetchone()

            # get cart totals
            cart_subtotal = request.form.get("subtotal")
            cart_tax = request.form.get("tax")
            cart_total = request.form.get("total")

            # cart_total = cart_total_result[0] if cart_total_result[0] is not None else 0

            order_result = db.session.execute(text(create_order_sql), {
                "customer_id": customer_id,
                "order_subtotal": cart_subtotal,
                "order_tax": cart_tax,
                "order_total": cart_total
            }).fetchone()
            
            if not order_result:
                db.session.rollback()
                return redirect(url_for('cart.cart'))
            
            order_id = order_result[0]

            # insert order items from cart items
            insert_items_sql = """
                INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
                SELECT :order_id, ci.product_id, ci.quantity, p.price
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = :cart_id
            """

            print("cart items", insert_items_sql) # debug print to check SQL query

            db.session.execute(text(insert_items_sql), {
                "order_id": order_id,
                "cart_id": cart_id,
            })

            # clear cart items
            clear_cart_sql = """
                DELETE FROM cart_items
                WHERE cart_id = :cart_id
            """

            db.session.execute(text(clear_cart_sql), {"cart_id": cart_id})
            db.session.commit() # save changes to db

            return redirect(url_for("order.order"))

        # --- GET --- #

        # get customer id
        customer_id = current_user.get_id()

        orders_sql = """
            SELECT 
                o.order_id,
                o.order_date,
                o.order_subtotal,
                o.order_tax,
                o.order_total,
                o.order_status,

                COALESCE(
                    json_agg(
                        json_build_object(
                            'product_name', p.product_name,
                            'quantity', oi.quantity,
                            'price_at_purchase', oi.price_at_purchase
                        )
                    ) FILTER (WHERE oi.order_id IS NOT NULL),
                    '[]'
                ) AS items

            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.customer_id = :customer_id
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
            """

        orders_result = db.session.execute(
            text(orders_sql),
            {"customer_id": customer_id}
        ).fetchall()

        print("orders result", orders_result) # debug print to check orders result

        return render_template('order.html', orders=orders_result)

    else:
        return redirect(url_for("home.home"))