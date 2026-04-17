from collections import defaultdict
from models import OrderItems
from extensions import db
import math

def get_also_bought(product_id, limit=5):
    print('get_also_bought called with: ', product_id)
    cooccurrence, product_counts = get_cooccurrence_cached()

    # debug
    print("cooccurrence keys:", list(cooccurrence.keys())[:10])
    print("checking product_id:", product_id)

    if product_id not in cooccurrence:
        print('early fail') # debug
        return []

    related = cooccurrence[product_id]
    print('related items', related) # debug
    total_A = product_counts[product_id]

    scored_products = []

    for other_product, cooccur_count in related.items():
        if cooccur_count < 2:
            continue
        if cooccur_count / total_A < 0.05:
            continue

        total_B = product_counts[other_product]
        score = cooccur_count / math.sqrt(total_A * total_B)
        scored_products.append((other_product, score))

    # Sort by score
    sorted_products = sorted(
        scored_products,
        key=lambda x: x[1],
        reverse=True
    )

    for p in sorted_products[:limit]:
        print('product: ', p)

    return [p[0] for p in sorted_products[:limit]]


def build_cooccurrence():
    cooccurrence = defaultdict(lambda: defaultdict(int))
    product_counts = defaultdict(int)  

    orders = db.session.query(OrderItems.order_id).distinct().all()

    for (order_id,) in orders:
        items = db.session.query(OrderItems.product_id)\
            .filter_by(order_id=order_id).all()

        product_ids = [i[0] for i in items]

        # Count individual product frequency
        for p in product_ids:
            product_counts[p] += 1

        # Count co-occurrence
        for i in product_ids:
            for j in product_ids:
                if i != j:
                    cooccurrence[i][j] += 1

    return cooccurrence, product_counts


_cooccurrence_cache = None
_product_counts_cache = None

def get_cooccurrence_cached():
    global _cooccurrence_cache, _product_counts_cache

    if _cooccurrence_cache is None:
        _cooccurrence_cache, _product_counts_cache = build_cooccurrence()

    return _cooccurrence_cache, _product_counts_cache