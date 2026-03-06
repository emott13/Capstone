from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import current_user
from extensions import db
from sqlalchemy import text
from datetime import datetime
order_bp = Blueprint("order", __name__, static_folder="static_order",
                  template_folder="templates_order")

@order_bp.route("/order", methods=["GET", "POST"])
def order():

    # handle including promotions in order total calculation
    # 1. fetch active promotions
    # 2. check time validity
    # 3. check conditions
    # 4. check usage limits
    # 5. calculate discount
    # 6. insert into order_discounts and promotion_redemptions tables
    # 7. reduce order total
    # 8. commit

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

            # # get cart totals
            # cart_sql = """
            #     SELECT 
            #         ci.product_id,
            #         ci.quantity,
            #         p.price,
            #         p.vendor_id
            #     FROM cart_items ci
            #     JOIN products p ON ci.product_id = p.product_id
            #     WHERE ci.cart_id = :cart_id
            # """

            # cart_items = db.session.execute(
            #     text(cart_sql),
            #     {"cart_id": cart_id}
            # ).fetchall()

            # if not cart_items:
            #     return redirect(url_for("cart.cart"))

            # cart_subtotal = sum(item.quantity * item.price for item in cart_items)

            # # cart_total = cart_total_result[0] if cart_total_result[0] is not None else 0

            # order_result = db.session.execute(text(create_order_sql), {
            #     "customer_id": customer_id,
            #     "order_subtotal": cart_subtotal,
            #     "order_tax": cart_tax,
            #     "order_total": cart_total
            # }).fetchone()
            
            # if not order_result:
            #     db.session.rollback()
            #     return redirect(url_for('cart.cart'))
            
            # order_id = order_result[0]

            # # insert order items from cart items
            # insert_items_sql = """
            #     INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase)
            #     SELECT :order_id, ci.product_id, ci.quantity, p.price
            #     FROM cart_items ci
            #     JOIN products p ON ci.product_id = p.product_id
            #     WHERE ci.cart_id = :cart_id
            # """

            # print("cart items", insert_items_sql) # debug print to check SQL query

            # db.session.execute(text(insert_items_sql), {
            #     "order_id": order_id,
            #     "cart_id": cart_id,
            # })

            # # clear cart items
            # clear_cart_sql = """
            #     DELETE FROM cart_items
            #     WHERE cart_id = :cart_id
            # """

            # db.session.execute(text(clear_cart_sql), {"cart_id": cart_id})
            # db.session.commit() # save changes to db
            cart_sql = """
                SELECT 
                    ci.product_id,
                    ci.quantity,
                    p.price,
                    p.vendor_id
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.product_id
                WHERE ci.cart_id = :cart_id
            """

            cart_items = db.session.execute(
                text(cart_sql),
                {"cart_id": cart_id}
            ).fetchall()

            if not cart_items:
                return redirect(url_for("cart.cart"))

            cart_subtotal = sum(item.quantity * item.price for item in cart_items)

            # fetch active promotions 
            promo_sql = """
                SELECT *
                FROM promotions
                WHERE is_active = true
                AND (starts_at IS NULL OR starts_at <= NOW())
                AND (ends_at IS NULL OR ends_at >= NOW())
            """

            active_promotions = db.session.execute(text(promo_sql)).fetchall()

            # validate promo code if entered
            entered_code = request.form.get("promo_code")
            applied_promotion = None

            if entered_code:
                for promo in active_promotions:
                    if promo.code and promo.code.lower() == entered_code.lower():
                        applied_promotion = promo
                        break

            # check usage limits
            if applied_promotion:

                usage_count_sql = """
                SELECT COUNT(*)
                FROM promotion_redemptions
                WHERE promotion_id = :promotion_id
                """

                total_uses = db.session.execute(
                    text(usage_count_sql),
                    {"promotion_id": applied_promotion.promotion_id}
                ).scalar()

                if applied_promotion.usage_limit and total_uses >= applied_promotion.usage_limit:
                    applied_promotion = None

            # calculate discount
            discount_amount = 0

            if applied_promotion:
                if applied_promotion.discount_type == "percentage":
                    discount_amount = int(cart_subtotal * (applied_promotion.discount_value / 100))

                elif applied_promotion.discount_type == "fixed_amount":
                    discount_amount = applied_promotion.discount_value

                discount_amount = min(discount_amount, cart_subtotal)

            # final totals
            tax_rate = 0.07
            cart_tax = int((cart_subtotal - discount_amount) * tax_rate)
            order_total = cart_subtotal - discount_amount + cart_tax

            # create order from cart items (default pending order status)
            create_order_sql = """
                INSERT INTO orders (customer_id, order_date, order_subtotal, order_tax, order_total, order_status)
                VALUES (:customer_id, NOW(), :order_subtotal, :order_tax, :order_total, 'pending')
                RETURNING order_id
            """

            order_result = db.session.execute(text(create_order_sql), {
                "customer_id": customer_id,
                "order_subtotal": cart_subtotal,
                "order_tax": cart_tax,
                "order_total": order_total
            }).fetchone()

            order_id = order_result[0]

            # handle promotions
            if applied_promotion:

                insert_discount_sql = """
                    INSERT INTO order_discounts (
                        order_id,
                        promotion_id,
                        code_used,
                        discount_amount_applied
                    )
                    VALUES (:order_id, :promotion_id, :code_used, :amount)
                """

                db.session.execute(text(insert_discount_sql), {
                    "order_id": order_id,
                    "promotion_id": applied_promotion.promotion_id,
                    "code_used": applied_promotion.code,
                    "amount": discount_amount
                })

                insert_redemption_sql = """
                    INSERT INTO promotion_redemptions (
                        promotion_id,
                        customer_id,
                        order_id
                    )
                    VALUES (:promotion_id, :customer_id, :order_id)
                """

                db.session.execute(text(insert_redemption_sql), {
                    "promotion_id": applied_promotion.promotion_id,
                    "customer_id": customer_id,
                    "order_id": order_id
                })

                db.session.commit() # save to db
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
                            'discount_amount', od.discount_amount_applied
                        )
                    ) FILTER (WHERE oi.order_id IS NOT NULL),
                    '[]'
                ) AS items

            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN order_discounts od ON o.order_id = od.order_id
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