from flask import Blueprint, render_template, request, url_for, redirect
from extensions import db
from sqlalchemy import text
cart_bp = Blueprint("cart", __name__, static_folder="static_cart",
                  template_folder="templates_cart")

@cart_bp.route("/cart", methods=["GET"])
def cart():
    # where cart id matches
    params = {}
    sql = '''
        SELECT p.product_name, ci.quantity, p.price, p.product_id
        FROM carts c
        INNER JOIN cart_items ci ON c.cart_id = ci.cart_id
        INNER JOIN products p ON ci.product_id = p.product_id
        WHERE c.cart_id = 1
        '''
    params["cart_id"] = 1
    cartItems = db.session.execute(text(sql), params).fetchall()
    print("cart items: ", cartItems)

    # map items
    cartItemsMap = []
    prices = []
    for item in cartItems:
        name = item[0]
        quantity = int(item[1])
        
        priceTotal = int(item[2] * item[1]) # multiply price x quantity
        prices.append(priceTotal) # append total
        price = centsToDollar(priceTotal) # convert from cents to dollars

        id = item[3]

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
    
    for price in prices:
        subtotal += price

    tax = round(float(subtotal * 0.06))
    total = tax + subtotal

    subtotal = centsToDollar(subtotal)
    tax = centsToDollar(tax)
    total = centsToDollar(total)

    totals = [subtotal, tax, total]
        
    return render_template("cart.html", cartItems = cartItemsMap, totals = totals)

def centsToDollar(num, html=False, thousand=False):
    try:
        numDollar = num / 100
    except:
        return num
    match html, thousand:
        case False, True:
            return f'${numDollar:,.2f}'
        case False, False:
            return f'${numDollar:.2f}'
        case True, True:
            return f'{numDollar:,.2f}'
        case True, False:
            return f'${numDollar:.2f}'
        case _:
            return f'${numDollar:.2f}'