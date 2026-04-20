import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
# seeder_sqlalchemy_full.py
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import func
from extensions import db, app, bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from models import UserInteractions, Users, Roles, UserRoles, Admins, Vendors, Customers
from models import PhoneNumbers, UserPhoneNumbers, Addresses
from models import Products, ProductSpecs, ProductColors, ProductCategories
from models import Carts, CartItems, Wishlists, WishlistItems
from models import Orders, OrderItems, OrderAddresses, Payments, Reviews
from models import Promotion, PromotionTarget, PromotionCondition, PromotionRedemption, OrderDiscount
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
    for _ in range(30):
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
    for _ in range(50):
        phone = PhoneNumbers(phone_number=fake.phone_number())
        db.session.add(phone)
        phone_list.append(phone)
    db.session.commit()

    # Assign phones to users
    for user in users_list:
        assigned_phones = sample(phone_list, randint(1, 2))
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
        for _ in range(randint(15, 20)):
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
    categories = ['Soils','Fertilizers', 'Seeds', 'Bulbs', 'Plants', 'Trees', 'Pots', 'Lawn Care', 'Garden Tools', 'Outdoor Furniture', 'Outdoor Decor', 'Indoor Gardening']
    for cat in categories:
        match (cat):
            case 'Soils': 
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://www.thetreecenter.com/c/uploads/2018/01/Garden_Soil_1-copy-jpg.webp'))
            case 'Fertilizers':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://www.gardendesign.com/pictures/images/900x705Max/site_3/applying-fertilizer-blue-trowel-fertilizing-tomato-plant-shutterstock-com_15275.jpg'))
            case 'Seeds':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://cdn.mos.cms.futurecdn.net/2KimaEYUTZk2qzNZjnLWYP.jpg'))
            case 'Bulbs':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://millcreekgardens.com/wp-content/uploads/2017/08/Depositphotos_65388297_m-2015.jpg'))
            case 'Plants':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://www.wagnergreenhouses.com/wp-content/uploads/2017/01/shutterstock_2061262208-1-scaled.jpg'))
            case 'Trees':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://t3.ftcdn.net/jpg/14/62/47/02/360_F_1462470203_3wXjC5IeReCDn6LgJwQFxFxvmH3iLzUX.jpg'))
            case 'Pots':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://mulhalls.com/wp-content/uploads/2024/01/Template-Website-Post-Image3.jpg'))
            case 'Lawn Care':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://huntersgardencentre.com/wp-content/uploads/2025/04/Blog-Post-Featured-Pic-lawn-care.jpg'))
            case 'Garden Tools':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://m.media-amazon.com/images/I/81BPQvrklaL._AC_UF350,350_QL80_.jpg'))
            case 'Outdoor Furniture':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://images.thdstatic.com/productImages/d86b6b44-e9c5-4005-aebd-2986d252ce6f/svn/hooowooo-fire-pit-patio-sets-rfp54-tbs210-64_600.jpg'))
            case 'Outdoor Decor':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://resources.itemint.com/hs-fs/hubfs/acogedor-patio-trasero-flores-al-atardecer.webp?width=1000&height=667&name=acogedor-patio-trasero-flores-al-atardecer.webp'))
            case 'Indoor Gardening':
                db.session.add(ProductCategories(
                    category_name=cat,
                    category_image='https://www.greengenius.com.au/cdn/shop/articles/6809d4a59bd9ce97f26c0270-1745475945147_3f99913f-dca2-487c-bcd4-300cd6b3de39.jpg?v=1755573292'))
    
    db.session.commit()
    print("Inserted product colors and categories")

    # --- ASSIGN PRODUCTS TO CATEGORIES (Many-to-Many) --- #
    # can be adjusted later to hard code categories for specific products if needed
    categories_list = ProductCategories.query.all()

    # hardcoded count: 47

    # soils
    for product in products_list[:5]:
        product.categories.append(categories_list[0])

    # fertilizers
    for product in products_list[6:11]:
        product.categories.append(categories_list[1])

    # seeds
    for product in products_list[12:18]:
        product.categories.append(categories_list[2])

    # bulbs
    for product in products_list[19:23]:
        product.categories.append(categories_list[3])

    # plants
    for product in products_list[24:27]:
        product.categories.append(categories_list[4])

    # trees
    for product in products_list[28:32]:
        product.categories.append(categories_list[5])

    # pots
    for product in products_list[33:37]:
        product.categories.append(categories_list[6])

    # lawn care
    for product in products_list[38:42]:
        product.categories.append(categories_list[7])

    # garden tools
    for product in products_list[43:47]:
        product.categories.append(categories_list[8])

    # randomly assignmed
    for product in products_list[48:]:
        # each product gets 1–3 random categories
        assigned_categories = sample(categories_list, randint(1, 3))

        for category in assigned_categories:
            product.categories.append(category)

    db.session.commit()
    print("Assigned categories to products")

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
        for _ in range(randint(5, 15)):
            product = choice(products_list)
            db.session.add(CartItems(
                cart_id=cart.cart_id,
                product_id=product.product_id,
                quantity=randint(1, 5),
            ))
    db.session.commit()
    print("Inserted carts and cart_items")

    # Wishlist items
    wishlists_list = Wishlists.query.all()
    for wishlist in wishlists_list:
        for _ in range(randint(5, 15)):
            product = choice(products_list)
            db.session.add(WishlistItems(
                wishlist_id=wishlist.wishlist_id,
                product_id=product.product_id,
                quantity=randint(1, 5)
            ))
    db.session.commit()
    print("Inserted wishlists and wishlist_items")


    # --- BUILD CATEGORY-BASED BUNDLES --- #
    category_map = {}

    for product in products_list:
        for category in product.categories:
            category_map.setdefault(category.category_id, []).append(product)

    product_bundles = []

    for category_id, products in category_map.items():
        if len(products) >= 3:
            # create multiple bundles per category
            for _ in range(3):
                bundle_size = randint(3, 5)
                bundle = sample(products, bundle_size)
                product_bundles.append(bundle)

    print(f"Created {len(product_bundles)} bundles")

    # --- CROSS CATEGORY BUNDLES --- #
    cross_bundles = []

    for _ in range(20):
        bundle = sample(products_list, randint(3, 5))
        cross_bundles.append(bundle)

    product_bundles.extend(cross_bundles)

    # --- HOT BUNDLES --- #
    hot_bundles = sample(product_bundles, min(10, len(product_bundles)))

    # --- ORDERS --- #
    for customer in customers_list:
        for _ in range(randint(5, 10)):
            order = Orders(
                customer_id=customer.customer_id,
                order_status=choice(['pending', 'shipped', 'delivered', 'cancelled']),
                order_date=fake.date_time_this_year(),
                order_subtotal=0,
                order_tax=0,
                order_total=0
            )
            db.session.add(order)

    db.session.commit()


    # --- ORDER ITEMS + PAYMENTS --- #
    orders_list = Orders.query.all()
    addresses_all = Addresses.query.all()

    for order in orders_list:

        use_bundle = random.random() < 0.75  # 75% bundle-based orders
        subtotal = 0

        if use_bundle and product_bundles:

            # 60% chance: reuse a hot bundle for stronger cooccurrance
            if random.random() < 0.6:
                bundle = choice(hot_bundles)
            else:
                bundle = choice(product_bundles)

            for product in bundle:
                qty = randint(1, 5)
                subtotal += product.price * qty

                db.session.add(OrderItems(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=qty,
                    price_at_purchase=product.price
                ))

        else:
            # fallback random products
            items = sample(products_list, randint(2, 4))

            for product in items:
                qty = randint(1, 3)
                subtotal += product.price * qty

                db.session.add(OrderItems(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=qty,
                    price_at_purchase=product.price
                ))

        # --- Update totals based on actual items --- #
        tax = int(subtotal * 0.06)
        total = subtotal + tax

        order.order_subtotal = subtotal
        order.order_tax = tax
        order.order_total = total

        # --- Addresses --- #
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

        # --- Payment --- #
        db.session.add(Payments(
            order_id=order.order_id,
            customer_id=order.customer_id,
            amount=total,
            payment_method=choice(['credit_card','paypal','bank_transfer']),
            paid_at=fake.date_time_this_year()
        ))

    db.session.commit()
    print("Inserted orders, order_items, order_addresses, payments")

    # --- REVIEWS --- #
    orders = Orders.query.all()

    reviews_created = 0

    for order in orders:
        # Only allow reviews for delivered orders (more realistic)
        if order.order_status != "delivered":
            continue

        # Get all products in this order
        order_items = OrderItems.query.filter_by(order_id=order.order_id).all()

        for item in order_items:
            # 80% chance a purchased product gets reviewed
            if random.random() < 0.8:
                review = Reviews(
                    customer_id=order.customer_id,
                    product_id=item.product_id,
                    rating=randint(3, 5) if random.random() < 0.8 else randint(1, 2),  
                    title=fake.sentence(nb_words=6),
                    description=fake.text(max_nb_chars=200)
                )

                try:
                    db.session.add(review)
                    db.session.flush()  # prevents full commit spam
                    reviews_created += 1
                except IntegrityError:
                    db.session.rollback()

    db.session.commit()
    print(f"Inserted {reviews_created} realistic reviews")
    # --- PROMOTIONS --- #

    # --- UTILITY FUNCTIONS --- #

    def now():
        return datetime.utcnow()

    # Check if a promotion is active based on current date and promotion's start/end dates
    def promotionIsActive(promo, order_date):
        if not promo.is_active:
            return False
        if promo.starts_at and order_date < promo.starts_at:
            return False
        if promo.ends_at and order_date > promo.ends_at:
            return False
        return True

    def checkUsageLimits(promo, customer_id):
        total_usage = db.session.query(func.count(PromotionRedemption.promotion_redemption_id)).filter_by(promotion_id=promo.promotion_id).scalar()

        if promo.usage_limit and total_usage >= promo.usage_limit:
            return False
        
        customer_usage = db.session.query(func.count(PromotionRedemption.promotion_redemption_id)).filter_by(promotion_id=promo.promotion_id, customer_id=customer_id).scalar()

        if promo.per_customer_limit and customer_usage >= promo.per_customer_limit:
            return False
        
        return True

    # Check if the promotion applies to the order based on its conditions
    def checkConditions(promo, order, customer):
        conditions = PromotionCondition.query.filter_by(promotion_id=promo.promotion_id).all()

        for condition in conditions:
            if condition.condition_type == "min_cart_total":
                if order.order_subtotal < int(condition.condition_value):
                    return False
                elif condition.condition_type == "first_order_only":
                    previous_orders = Orders.query.filter(
                        Orders.customer_id == customer.user_id,
                        Orders.order_date < order.order_date
                    ).count()
                    if previous_orders > 0:
                        return False
                elif condition.condition_type == "customer_role":
                    if not customer.has_role(condition.condition_value): # issue if condition value is not "customer"
                        return False
                    
        return True

    # Check if the promotion applies to the order based on its scope and targets
    def scopeMatches(promo, order):
        if promo.scope_type == "cart":
            return True

        order_items = OrderItems.query.filter_by(order_id=order.order_id).all()

        targets = PromotionTarget.query.filter_by(
            promotion_id=promo.promotion_id
        ).all()

        for item in order_items:
            for target in targets:
                if promo.scope_type == "product" and target.product_id == item.product_id:
                    return True
                if promo.scope_type == "vendor" and target.vendor_id == item.product.vendor_id:
                    return True
                if promo.scope_type == "category":
                    for category in item.product.categories:
                        if category.category_id == target.category_id:
                            return True

        return False

    # Calculate the discount amount based on the promotion's discount type and value
    def calculateDiscount(promo, order):
        if promo.discount_type == "percentage":
            return int(order.order_subtotal * (promo.discount_value / 100))
        elif promo.discount_type == "fixed_amount":
            return min(promo.discount_value, order.order_subtotal)
        elif promo.discount_type == "bogo":
            return int(order.order_subtotal / 2)  # Simplified BOGO: 50% off if applicable
        return 0


    # --- SEEDING FUNCTION --- #

    def seedPromotions(num_promotions=15):

        vendors = Vendors.query.all()
        products = Products.query.all()
        categories = ProductCategories.query.all()
        users = Users.query.all()
        orders = Orders.query.all()

        promotions = []

        # -- create promotions -- #
        for _ in range(num_promotions):

            discount_type = random.choice([
                "percentage",
                "fixed_amount",
                "bogo"
            ])

            scope_type = random.choice([
                "cart",
                "product",
                "vendor",
                "category"
            ])

            created_by_admin = random.choice([True, False])
            vendor = random.choice(vendors) if not created_by_admin else None

            if discount_type == "percentage":
                discount_value = random.randint(10, 50)  # 10% to 50%
            elif discount_type == "fixed_amount":
                discount_value = random.randint(500, 3000)  # $5 to $30 in cents
            else:  # bogo
                discount_value = 0  # BOGO doesn't have a direct discount value
            
            start_date = fake.date_time_between(start_date='-30d', end_date='+10d')
            end_date = start_date + timedelta(days=random.randint(10, 90))

            promo = Promotion(
                name=fake.catch_phrase(),
                code=fake.unique.bothify("SALE-####"),
                description=fake.text(200),
                discount_type=discount_type,
                discount_value=discount_value,
                scope_type=scope_type,
                created_by_admin=created_by_admin,
                vendor_id=vendor.vendor_id if vendor else None,
                usage_limit=random.randint(50, 300),
                per_customer_limit=random.choice([1, 2, 3]),
                stackable=random.choice([True, False]),
                starts_at=start_date,
                ends_at=end_date,
                is_active=random.choice([True, True, False])
            )

            db.session.add(promo)
            promotions.append(promo)

        db.session.commit()

        # -- promotion targets -- #
        for promo in promotions:
            if promo.scope_type == "cart":
                continue

            for _ in range(random.randint(1, 3)):
                target = PromotionTarget(promotion_id=promo.promotion_id)

                if promo.scope_type == "product":
                    target.product_id = random.choice(products).product_id
                elif promo.scope_type == "vendor":
                    target.vendor_id = random.choice(vendors).vendor_id
                elif promo.scope_type == "category":
                    target.category_id = random.choice(categories).category_id

                db.session.add(target)

        db.session.commit()

        # -- redemptions -- #
        for order in orders:
            customer = Users.query.get(order.customer_id)
            applied_non_stackable = False

            for promo in promotions:
                if not promotionIsActive(promo, order.order_date):
                    continue
                if not checkUsageLimits(promo, customer.user_id):
                    continue
                if not checkConditions(promo, order, customer):
                    continue
                if not scopeMatches(promo, order):
                    continue

                if applied_non_stackable and not promo.stackable:
                    continue
                discount_amount = calculateDiscount(promo, order)
                if discount_amount <= 0:
                    continue

                # record the redemption
                redemption = PromotionRedemption(
                    promotion_id=promo.promotion_id,
                    order_id=order.order_id,
                    customer_id=customer.user_id,
                )

                order_discount = OrderDiscount(
                    order_id=order.order_id,
                    promotion_id=promo.promotion_id,
                    code_used=promo.code,
                    discount_amount_applied=discount_amount
                )

                db.session.add(redemption)
                db.session.add(order_discount)

                if not promo.stackable:
                    applied_non_stackable = True
    print(type(random))
    seedPromotions(num_promotions=15) # call seeding function

    db.session.commit()
    print("Inserted promotions, targets, and redemptions")
        
    # --- USER INTERACTIONS --- #
    # simulating user interactions like adding items to cart, placing orders, writing reviews, etc.

    # --- purchases (5) ---
    orders = db.session.query(OrderItems).all()
    for item in orders:
        interaction = UserInteractions(
            user_id=item.order.customer_id,
            product_id=item.product_id,
            interaction_type="purchase",
            interaction_value=5.0
        )
        db.session.add(interaction)

    # --- carts (3) ---
    cart_items = db.session.query(CartItems).all()
    for item in cart_items:
        interaction = UserInteractions(
            user_id=item.cart.customer_id,
            product_id=item.product_id,
            interaction_type="add_to_cart",
            interaction_value=3.0
        )
        db.session.add(interaction)

    # --- wishlists (2) ---
    wishlist_items = db.session.query(WishlistItems).all()
    for item in wishlist_items:
        interaction = UserInteractions(
            user_id=item.wishlist.customer_id,
            product_id=item.product_id,
            interaction_type="add_to_wishlist",
            interaction_value=2.0
        )
        db.session.add(interaction)

    # --- reviews (rating) ---
    reviews = db.session.query(Reviews).all()
    for review in reviews:
        interaction = UserInteractions(
            user_id=review.customer_id,
            product_id=review.product_id,
            interaction_type="review",
            interaction_value=float(review.rating)  # using rating as interaction value
        )
        db.session.add(interaction)

    db.session.commit() # commit all interactions

    print('User Interactions seeded successfully')
        
    print("Seeder finished successfully")

