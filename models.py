from sqlalchemy import text
from extensions import db
from flask_login import UserMixin

# product category map
product_category_map = db.Table(
    "product_category_map",
    db.Column(
        "product_id",
        db.Integer,
        db.ForeignKey("products.product_id", ondelete="CASCADE"),
        primary_key=True
    ),
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("product_categories.category_id", ondelete="CASCADE"),
        primary_key=True
    )
)


# ------------ #
# -- MODELS -- #
# ------------ #

# Users
class Users(UserMixin, db.Model):
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

    phone_numbers = db.relationship(
        "PhoneNumbers", 
        secondary="user_phone_numbers", 
        back_populates="users"
        )

    def get_id(self):
        return self.user_id
    
    def has_role(self, role_name):
        return any(role.role_name == role_name for role in self.roles)

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

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     # Custom initialization
    #     # this might not work. Sorry if this errors for one of you
    #     cart = Carts(customer_id=self.customer_id)
    #     db.session.add(cart)
    #     db.session.commit()
    
    def getUser(self):
        return db.one_or_404(db.select(Users).filter_by(user_id=self.customer_id))

    # def getCart(self):
    #     return Carts.query.filter_by(text("customer_id = :customer_id", {"customer_id": self.customer_id})).get_or_404()

# PhoneNumbers
class PhoneNumbers(db.Model):
    __tablename__ = "phone_numbers"
    phone_id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(22), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    
    users = db.relationship(
        "Users",
        secondary="user_phone_numbers",
        back_populates="phone_numbers"
    )

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
    product_id = db.Column(db.BigInteger, primary_key=True)
    vendor_id = db.Column(db.BigInteger, db.ForeignKey("vendors.vendor_id"), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # Store price in cents to avoid float issues
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    
    # Relationships
    categories = db.relationship(
        "ProductCategories",
        secondary=product_category_map,
        backref=db.backref("products", lazy="dynamic")
    )
    wishlist_items = db.relationship("WishlistItems", back_populates="product")

    specs = db.relationship(
        "ProductSpecs",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    colors = db.relationship(
        "ProductColors",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    images = db.relationship(
        "ProductImages",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
# product specs
class ProductSpecs(db.Model):
    __tablename__ = "product_specs"
    spec_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    specification = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship(
        "Products",
        back_populates="specs"
    )

# product colors
class ProductColors(db.Model):
    __tablename__ = "product_colors"
    color_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    hex_code = db.Column(db.String(7), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship(
        "Products",
        back_populates="colors"
    )

# product categories
class ProductCategories(db.Model):
    __tablename__ = "product_categories"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    category_image = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# product images
class ProductImages(db.Model):
    __tablename__ = "product_images"
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    product = db.relationship(
        "Products",
        back_populates="images"
    )

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

    cart = db.relationship("Carts", backref="cart_items")

# wishlists
class Wishlists(db.Model):
    __tablename__ = "wishlists"
    wishlist_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    items = db.relationship("WishlistItems", backref="wishlist", lazy=True)

# wishlist items
class WishlistItems(db.Model):
    __tablename__ = "wishlist_items"
    wishlist_item_id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey("wishlists.wishlist_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    product = db.relationship("Products", back_populates="wishlist_items")

# orders
class Orders(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
    order_status = db.Column(db.String(20), nullable=False)  # e.g., pending, shipped, delivered
    order_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    order_subtotal = db.Column(db.Integer, nullable=False)  # Store total price in cents
    order_tax = db.Column(db.Integer, nullable=False)  # Store tax amount in cents
    order_total = db.Column(db.Integer, nullable=False)  # Store total price in cents
    payment_method = db.Column(db.String(50))  # e.g., credit card, PayPal
    paid_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    
    # RELATIONSHIPS
    items = db.relationship(
        "OrderItems",
        backref="order",
        lazy=True
    )

# order items
class OrderItems(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Integer, nullable=False)  # Store price at purchase time in cents
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    # RELATIONSHIPS 
    product = db.relationship(
        "Products",
        backref="order_items"
    )

# order addresses
class OrderAddresses(db.Model):
    __tablename__ = "order_addresses"
    address_id = db.Column(db.Integer)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), primary_key=True, nullable=False)
    address_type = db.Column(db.String(20), nullable=False, primary_key=True)  # e.g., shipping, billing
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# payments
class Payments(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("customers.customer_id"), nullable=False)
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

    def getCustomer(self):
        return db.one_or_404(db.select(Customers).filter_by(customer_id=self.customer_id))

# discounts
class Promotion(db.Model):
    __tablename__ = "promotions"
    promotion_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)  # nullable for automatic discounts
    description = db.Column(db.Text)

    # Discount definition
    discount_type = db.Column(
        db.String(30),
        nullable=False
        # values:
        # 'percentage'
        # 'fixed_amount'
        # 'free_shipping'
        # 'bogo'
    )

    discount_value = db.Column(db.Integer, nullable=False)
    # cents if fixed_amount
    # integer percent if percentage

    # Scope
    scope_type = db.Column(
        db.String(30),
        nullable=False
        # 'cart'
        # 'product'
        # 'vendor'
        # 'category'
    )

    # Ownership
    created_by_admin = db.Column(db.Boolean, default=True)
    vendor_id = db.Column(
        db.BigInteger,
        db.ForeignKey("vendors.vendor_id"),
        nullable=True
    )  # null if global/admin promo

    # Limits
    usage_limit = db.Column(db.Integer)  # total uses allowed
    per_customer_limit = db.Column(db.Integer)

    stackable = db.Column(db.Boolean, default=False)

    # Time controls
    starts_at = db.Column(db.DateTime(timezone=True))
    ends_at = db.Column(db.DateTime(timezone=True))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())


    # RELATIONSHIPS
    targets = db.relationship(
        "PromotionTarget",
        backref="promotion",
        cascade="all, delete-orphan"
    )

    conditions = db.relationship(
        "PromotionCondition",
        backref="promotion",
        cascade="all, delete-orphan"
    )

    redemptions = db.relationship(
        "PromotionRedemption",
        backref="promotion",
        cascade="all, delete-orphan"
    )

    order_discounts = db.relationship(
        "OrderDiscount",
        backref="promotion",
        cascade="all, delete-orphan"
    )

# targets
# allows associating a promotion with specific products, vendors, or categories based on scope_type
class PromotionTarget(db.Model):
    __tablename__ = "promotion_targets"

    promotion_target_id = db.Column(db.Integer, primary_key=True)

    promotion_id = db.Column(
        db.Integer,
        db.ForeignKey("promotions.promotion_id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.product_id"),
        nullable=True
    )

    vendor_id = db.Column(
        db.BigInteger,
        db.ForeignKey("vendors.vendor_id"),
        nullable=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("product_categories.category_id"),
        nullable=True
    )

# promotion conditions
class PromotionCondition(db.Model):
    __tablename__ = "promotion_conditions"
    promotion_condition_id = db.Column(db.Integer, primary_key=True)

    promotion_id = db.Column(
        db.Integer,
        db.ForeignKey("promotions.promotion_id"),
        nullable=False
    )

    condition_type = db.Column(
        db.String(50),
        nullable=False
        # examples:
        # 'min_cart_total'
        # 'first_order_only'
        # 'customer_role'
    )

    condition_value = db.Column(db.String(100), nullable=False)

# promotion redemptions
class PromotionRedemption(db.Model):
    __tablename__ = "promotion_redemptions"
    promotion_redemption_id = db.Column(db.Integer, primary_key=True)

    promotion_id = db.Column(
        db.Integer,
        db.ForeignKey("promotions.promotion_id"),
        nullable=False
    )

    customer_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.order_id"),
        nullable=False
    )

    redeemed_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )

# order discounts
class OrderDiscount(db.Model):
    __tablename__ = "order_discounts"

    order_discount_id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.order_id"),
        nullable=False
    )

    promotion_id = db.Column(
        db.Integer,
        db.ForeignKey("promotions.promotion_id"),
        nullable=False
    )

    code_used = db.Column(db.String(50))
    discount_amount_applied = db.Column(db.Integer, nullable=False)  # in cents
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

# user interactions
class UserInteractions(db.Model):
    __tablename__ = "user_interactions"
    interaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # e.g., view, add_to_cart, purchase, wishlist, review
    interaction_value = db.Column(db.Float, default=1.0, nullable=True) 
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def log_interaction(user_id, product_id, interaction_type, value=1.0):
        interaction = UserInteractions(
            user_id=user_id,
            product_id=product_id,
            interaction_type=interaction_type,
            interaction_value=value
        )
        db.session.add(interaction)
        db.session.commit()

class Recommendations(db.Model):
    __tablename__ = "recommendations"

    recommendation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.user_id"))
    product_id = db.Column(db.BigInteger, db.ForeignKey("products.product_id"))
    score = db.Column(db.Float)