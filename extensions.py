import os
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_login import LoginManager, UserMixin, current_user
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv

# USEFUL flask_login COMMANDS
# @app.route("/foo")
# @login_required # (requires the user to be logged in. Redirects to login if not logged in)
# def foo() ...
# current_user # (has current_user data like current_user.email or current_user.type)
# current_user.is_authenticated
# getCurrentType() # gets the current type. Is None if the user isn't signed in


# Postgresql connection credentials
load_dotenv()
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]

# Initialize Flask app
conn_str = f"postgresql://{db_user}:{db_password}@localhost/{db_name}" 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\xdak\xd2\xf7\x80,8\x0f\xbdG\xb7\x87\xe4h\xcf\xae'

# Initialize database
db = SQLAlchemy()
db.init_app(app)

# Initialize bcrypt
bcrypt = Bcrypt(app)

# Initialize bootstrap
Bootstrap(app)

# Initialize database and login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "blueprints.login.login"

@login_manager.user_loader
def load_user(user_id):
    return Users.get(user_id)

# Initialize DB the way we did the other times
engine = create_engine(conn_str, echo=True)                                             
conn = engine.connect()                                                                 

# Define models here
# Users
class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    roles = db.relationship(
        "Roles",
        secondary="user_roles",
        backref=db.backref("users", lazy="dynamic")
    )
# Roles
class Roles(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())


# UserRoles
class UserRoles(db.Model):
    __tablename__ = "user_roles"
    user_role_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# Admins
class Admins(db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# Vendors
class Vendors(db.Model):
    __tablename__ = "vendors"
    vendor_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# Customers
class Customers(db.Model):
    __tablename__ = "customers"
    customer_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# PhoneNumbers
class PhoneNumbers(db.Model):
    __tablename__ = "phone_numbers"
    phone_id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(22), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# UserPhoneNumbers
class UserPhoneNumbers(db.Model):
    __tablename__ = "user_phone_numbers"
    user_phone_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    phone_id = db.Column(db.Integer, db.ForeignKey("phone_numbers.phone_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# addresses
class Addresses(db.Model):
    __tablename__ = "addresses"
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    address1 = db.Column(db.String(100), nullable=False)
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# products
class Products(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.BigInteger, db.ForeignKey("vendors.vendor_id"), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # Store price in cents to avoid float issues
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# product specs
class ProductSpecs(db.Model):
    __tablename__ = "product_specs"
    spec_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    specification = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# product colors
class ProductColors(db.Model):
    __tablename__ = "product_colors"
    color_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    hex_code = db.Column(db.String(7), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# product categories
class ProductCategories(db.Model):
    __tablename__ = "product_categories"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# product images
class ProductImages(db.Model):
    __tablename__ = "product_images"
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# carts
class Carts(db.Model):
    __tablename__ = "carts"
    cart_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# cart items
class CartItems(db.Model):
    __tablename__ = "cart_items"
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.cart_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# wishlists
class Wishlists(db.Model):
    __tablename__ = "wishlists"
    wishlist_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# wishlist items
class WishlistItems(db.Model):
    __tablename__ = "wishlist_items"
    wishlist_item_id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey("wishlists.wishlist_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# orders
class Orders(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    order_status = db.Column(db.String(20), nullable=False)  # e.g., pending, shipped, delivered
    amount = db.Column(db.Integer, nullable=False)  # Store total price in cents
    payment_method = db.Column(db.String(50))  # e.g., credit card, PayPal
    paid_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# order items
class OrderItems(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Integer, nullable=False)  # Store price at purchase time in cents
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# order addresses
class OrderAddresses(db.Model):
    __tablename__ = "order_addresses"
    address_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    address_type = db.Column(db.String(20), nullable=False, primary_key=True)  # e.g., shipping, billing
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# payments
class Payments(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., credit card, PayPal
    paid_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    amount = db.Column(db.Integer, nullable=False)  # Store payment amount in cents
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# reviews
class Reviews(db.Model):
    __tablename__ = "reviews"
    review_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., 1-5
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())





#     def get_id(self): return self.email
#     def get_email(self): return self.get_id()




# price formatter for jinja template. call like {{154|priceFormat}}
@app.template_filter()
def priceFormat(value):
    formatted = str(value)[:-2] + "." + str(value)[-2:]
    if int(value) < 10:
        formatted = formatted[:-1] + "0" + formatted[-1:]
    if int(value) < 100:
        formatted = "0" + formatted

    return formatted
    # return f"{ round( int(value)/100, 2):.2f }"

# date formatter for jinja template
@app.template_filter()
def dateFormat(value: datetime.datetime) -> str:
    # formats like "Dec 05, 2026 11:59 PM"
    return value.strftime("%b %d, %Y %I:%M %p")

# date formatter for jinja template
@app.template_filter()
def dateOnlyFormat(value: datetime.datetime) -> str:
    # formats like "Dec 05, 2026"
    return value.strftime("%b %d, %Y")

# date formatter for jinja template
@app.template_filter()
def timeOnlyFormat(value: datetime.datetime) -> str:
    # formats like "09:10:32 PM"
    return value.strftime("%I:%M:%S %p")

@app.template_filter()
def chatDateFormat(value: datetime.datetime) -> str:
    """Sets the date to Today or Yesterday if that's true"""
    currentTime = datetime.datetime.now()
    if value.date() == currentTime.date():
        # formats like "Today at 11:59 PM"
        return value.strftime("Today at %-I:%M %p")
    elif value.date() == currentTime.date() - datetime.timedelta(1):
        # formats like "Yesterday at 11:59 PM"
        return value.strftime("Yesterday at %-I:%M %p")
    # formats like "Sun, Dec 05, 2026 11:59 PM"
    return value.strftime("%a, %b %d, %Y %-I:%M %p")
