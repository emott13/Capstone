from flask import render_template, url_for, redirect
# from sqlalchemy import create_engine, text, insert, Table, MetaData, update
from flask_login import logout_user, login_required, current_user
from extensions import *
from login.login import login_bp
from register.register import register_bp
from product.product import product_bp
from search.search import search_bp
from home.home import home_bp
from product_manage.product_manage import product_manage_bp
from cart.cart import cart_bp
from order.order import order_bp
from account.account import account_bp
from complaint.complaint import complaint_bp
from chat.chat import chat_bp

defaultDBPassword() # Hashes the default user's password as 'password'

# -- LOGIN PAGE -- #
app.register_blueprint(login_bp)

# -- SIGNUP PAGE -- #
app.register_blueprint(register_bp)

# -- ACCOUNT PAGE -- #
app.register_blueprint(account_bp)

# -- HOME PAGE -- #
app.register_blueprint(home_bp)

# -- SEARCH PAGE -- #
app.register_blueprint(search_bp)

# -- PRODUCT PAGE -- #
app.register_blueprint(product_bp)

# -- PRODUCT MANAGE PAGE -- #
app.register_blueprint(product_manage_bp)

# -- COMPLAINT PAGE -- #
app.register_blueprint(complaint_bp)

# -- CHAT PAGE -- #
app.register_blueprint(chat_bp)

# -- TEST PAGE -- #
# Shows current_user data (whoever is logged in)
@app.route("/test")
@login_required
def test():
    return render_template("test.html", current_user=current_user)

# -- LOGOUT PAGE -- #
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login.login"))

# -- CART PAGE -- #
app.register_blueprint(cart_bp)


# -- ORDER PAGE -- #
app.register_blueprint(order_bp)


if __name__ == '__main__':
    app.run(debug=True)