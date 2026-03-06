import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import func
from extensions import db
from models import (
    Promotion,
    PromotionTarget,
    PromotionCondition,
    PromotionRedemption,
    OrderDiscount,
    Vendors,
    Products,
    ProductCategories,
    Users,
    Orders,
    OrderItems
)

fake = Faker()

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
            if order.order_subtotal < int(condition.condition_valjue):
                return False
            elif condition.condition_type == "first_order_only":
                previous_orders = Orders.query.filter(
                    Orders.customer_id == customer.id,
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
            if promo.scope_type == "category" and target.category_id == item.product.category_id:
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
            if not checkUsageLimits(promo, customer.id):
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
                customer_id=customer.id,
            )

            order_discount = OrderDiscount(
                order_id=order.order_id,
                promotion_id=promo.promotion_id,
                code_used=promo.code,
                discount_amount=discount_amount
            )

            db.session.add(redemption)
            db.session.add(order_discount)

            if not promo.stackable:
                applied_non_stackable = True

    db.session.commit()
    print("Inserted promotions, targets, and redemptions")