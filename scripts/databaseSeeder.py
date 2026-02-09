import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
# seeder_sqlalchemy_full.py
from extensions import db, app, bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from extensions import Users, Roles, UserRoles, Admins, Vendors, Customers
from extensions import PhoneNumbers, UserPhoneNumbers, Addresses
from extensions import Products, ProductSpecs, ProductColors, ProductCategories, ProductImages
from extensions import Carts, CartItems, Wishlists, WishlistItems
from extensions import Orders, OrderItems, OrderAddresses, Payments, Reviews
from faker import Faker
from random import randint, sample, choice

fake = Faker()

with app.app_context():

    confirm = input("This will DROP ALL TABLES and reseed. Type YES to continue: ")
    if confirm != "YES":
        print("Seeder cancelled")
        exit()

    print("Dropping all tables...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()

    # --- USERS --- #
    users_list = []
    for _ in range(10):
        password = bcrypt.generate_password_hash("password").decode("utf-8")
        user = Users(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password=password,
            dob=fake.date_of_birth()
        )
        db.session.add(user)
        users_list.append(user)
    db.session.commit()
    print(f"Inserted {len(users_list)} users")

    # --- ROLES --- #
    role_names = ["admin", "vendor", "customer"]
    roles_list = []
    for name in role_names:
        role = Roles(role_name=name)
        db.session.add(role)
        roles_list.append(role)
    db.session.commit()
    print(f"Inserted {len(roles_list)} roles")

    # --- ASSIGN ROLES TO USERS --- #
    for user in users_list:
        assigned_roles = sample(roles_list, randint(1, 3))
        for role in assigned_roles:
            user.roles.append(role)
    db.session.commit()
    print("Assigned roles to users")

    # --- ROLE PROFILES --- #
    for user in users_list:
        role_names = [role.role_name for role in user.roles]
        if "admin" in role_names:
            db.session.add(Admins(admin_id=user.user_id))
        if "vendor" in role_names:
            db.session.add(Vendors(vendor_id=user.user_id, store_name=fake.company()))
        if "customer" in role_names:
            db.session.add(Customers(customer_id=user.user_id))
    db.session.commit()
    print("Inserted admin/vendor/customer profiles")

    # --- PHONE NUMBERS --- #
    phone_list = []
    for _ in range(20):
        phone = PhoneNumbers(phone_number=fake.phone_number())
        db.session.add(phone)
        phone_list.append(phone)
    db.session.commit()

    # Assign phones to users
    for user in users_list:
        assigned_phones = sample(phone_list, randint(0, 2))
        for phone in assigned_phones:
            db.session.add(UserPhoneNumbers(user_id=user.user_id, phone_id=phone.phone_id))
    db.session.commit()
    print("Inserted phone numbers and user_phone_numbers")

    # --- ADDRESSES --- #
    addresses_list = []
    for user in users_list:
        for _ in range(randint(1, 3)):
            addr = Addresses(
                user_id=user.user_id,
                address1=fake.street_address(),
                address2=fake.secondary_address() if fake.boolean() else None,
                city=fake.city(),
                state=fake.state(),
                country=fake.country(),
                zip_code=fake.postcode()
            )
            db.session.add(addr)
            addresses_list.append(addr)
    db.session.commit()
    print(f"Inserted {len(addresses_list)} addresses")

    # --- PRODUCTS --- #
    vendors_list = Vendors.query.all()
    products_list = []
    for vendor in vendors_list:
        for _ in range(randint(1, 5)):
            product = Products(
                vendor_id=vendor.vendor_id,
                product_name=fake.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=round(fake.random_number(digits=5)/100, 2)
            )
            db.session.add(product)
            products_list.append(product)
    db.session.commit()
    print(f"Inserted {len(products_list)} products")

    # Product specs
    for product in products_list:
        for _ in range(randint(1, 5)):
            db.session.add(ProductSpecs(product_id=product.product_id, specification=fake.sentence()))
    db.session.commit()
    print("Inserted product specifications")

    # Product colors
    for product in products_list:
        db.session.add(ProductColors(product_id=product.product_id, hex_code=fake.hex_color()))
    db.session.commit()

    # Product categories
    categories = ['Soils','Pots','Seeds','Tools','Fertilizers']
    for cat in categories:
        db.session.add(ProductCategories(category_name=cat))
    db.session.commit()
    print("Inserted product colors and categories")

    # Product images
    # runs photoSeeder.sql to seed
    with open("scripts/photoSeeder.sql", "r") as file:
        postgresql = file.read()
    db.session.execute(text(postgresql))
    db.session.commit()
    print("Inserted product images from photoSeeder.sql")

    # --- CARTS AND WISHLISTS --- #
    customers_list = Customers.query.all()
    for customer in customers_list:
        cart = Carts(customer_id=customer.customer_id)
        db.session.add(cart)

        wishlist = Wishlists(customer_id=customer.customer_id, title=fake.sentence(nb_words=3))
        db.session.add(wishlist)
    db.session.commit()

    # Cart items
    cart_list = Carts.query.all()
    for cart in cart_list:
        for _ in range(randint(1, 5)):
            product = choice(products_list)
            db.session.add(CartItems(
                cart_id=cart.cart_id,
                product_id=product.product_id,
                quantity=randint(1, 10),
            ))
    db.session.commit()
    print("Inserted carts and cart_items")

    # Wishlist items
    wishlists_list = Wishlists.query.all()
    for wishlist in wishlists_list:
        for _ in range(randint(1, 5)):
            product = choice(products_list)
            db.session.add(WishlistItems(
                wishlist_id=wishlist.wishlist_id,
                product_id=product.product_id
            ))
    db.session.commit()
    print("Inserted wishlists and wishlist_items")

    # --- ORDERS AND PAYMENTS --- #
    for customer in customers_list:
        for _ in range(randint(1, 3)):
            order = Orders(
                customer_id=customer.customer_id,
                order_status=choice(['pending', 'shipped', 'delivered', 'cancelled']),
                amount=round(fake.random_number(digits=5)/100, 2)
            )
            db.session.add(order)
    db.session.commit()

    orders_list = Orders.query.all()
    addresses_all = Addresses.query.all()
    for order in orders_list:
        for _ in range(randint(1, 3)):
            product = choice(products_list)
            db.session.add(OrderItems(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=randint(1, 5),
                price_at_purchase=product.price
            ))
            
        # Add shipping & billing addresses
        shipping_addr = choice(addresses_all)
        billing_addr = choice(addresses_all)
        
        db.session.add(OrderAddresses(
            order_id=order.order_id,
            address_id=shipping_addr.address_id,
            address_type="shipping"
        ))
        
        db.session.add(OrderAddresses(
            order_id=order.order_id,
            address_id=billing_addr.address_id,
            address_type="billing"
        ))

        # Payment
        db.session.add(Payments(
            order_id=order.order_id,
            amount=order.amount,
            payment_method=choice(['credit_card','paypal','bank_transfer']),
            paid_at=fake.date_time_this_year()
        ))
    db.session.commit()
    print("Inserted orders, order_items, order_addresses, payments")

    # --- REVIEWS --- #
    for _ in range(20):
        customer = choice(customers_list)
        product = choice(products_list)
        review = Reviews(
            customer_id=customer.customer_id,
            product_id=product.product_id,
            rating=randint(1,5),
            title=fake.sentence(nb_words=6),
            description=fake.text(max_nb_chars=200)
        )
        try:
            db.session.add(review)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # skip duplicate customer-product reviews
    print("Inserted reviews")

    print("Seeder finished successfully")
