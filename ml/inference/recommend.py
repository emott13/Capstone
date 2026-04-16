import torch
import pickle
import os

from ml.models.recommender_model import RecommenderModel
from extensions import db
from models import OrderItems, UserInteractions
from sqlalchemy import func


MODEL_PATH = "ml/saved_models/recommender.pt"
MAPPINGS_PATH = "ml/saved_models/mappings.pkl"

"""
This module is responsible for generating product recommendations for users based on the trained model.
The file creates a hybrid recommendation system:
    1. ML model-based recommendations for users with interaction history
    2. Popular product recommendations for new users (cold start)
    3. Seen filtering to avoid recommending products the user has already interacted with
"""

# ---------- LOAD MODEL + MAPPINGS ----------
"""
This function loads the trained model and the user/product mappings from disk. 
It also handles cases where the model or mappings are missing, prompting the user to train the model
"""
def load_model_and_mappings():
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Train it first.")
    # Check if mappings exist
    if not os.path.exists(MAPPINGS_PATH):
        raise FileNotFoundError("Mappings not found. Train it first.")

    # Load mappings
    with open(MAPPINGS_PATH, "rb") as f:
        mappings = pickle.load(f)

    # Extract user and product maps
    user_map = mappings["user_map"]
    product_map = mappings["product_map"]

    num_users = len(user_map)
    num_items = len(product_map)

    # Recreate model architecture
    model = RecommenderModel(num_users, num_items)
    # Load model weights
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    # Set model to evaluation mode (turns off training behaviors like dropout and randomness)
    model.eval()

    return model, user_map, product_map


# ---------- RECOMMENDATION FUNCTION ----------
"""
Takes a user ID and returns a list of recommended product IDs based on the trained model's predictions.
It handles cold start users (those with no interactions) by recommending popular products.
"""
def recommend_for_user(user_id, top_k=5):
    # Load cached model and mappings
    model, user_map, product_map = get_cached_model()

    # Handle new users (cold start)
    if user_id not in user_map:
        print(f"User {user_id} not in training data (cold start)")
        return []

    # Get user index from mapping
    user_idx = user_map[user_id]

    # Create tensors for all items
    all_item_indices = torch.arange(len(product_map))
    user_tensor = torch.tensor([user_idx] * len(product_map))

    # Run model prediction
    with torch.no_grad():
        scores = model(user_tensor, all_item_indices)

    # Get top K items
    top_items = torch.topk(scores, top_k).indices.tolist()

    # Convert back to real product IDs
    reverse_product_map = {v: k for k, v in product_map.items()}
    recommended_product_ids = [
        reverse_product_map[i.item() if hasattr(i, "item") else i] for i in top_items
    ]

    return [int(i) for i in recommended_product_ids]


"""
Caching the model and mappings in memory to avoid loading them from disk on every recommendation request.
"""

_model = None
_user_map = None
_product_map = None

def get_cached_model():
    global _model, _user_map, _product_map

    # Store in memory
    if _model is None:
        _model, _user_map, _product_map = load_model_and_mappings()

    return _model, _user_map, _product_map


# Helper function to get products a user has already interacted with, to avoid recommending them again
def get_seen_products(user_id):
    # Query interactions for the user
    interactions = db.session.query(UserInteractions.product_id)\
        .filter_by(user_id=user_id).all()
    # Convert to set of product IDs
    return set([i[0] for i in interactions])


# Helper function to get popular products for cold start users (those with no interactions)
def get_popular_products(limit=5):
    # Query the most popular products based on interaction counts
    results = db.session.query(
        OrderItems.product_id,
        func.count().label("count")
    ).group_by(OrderItems.product_id)\
     .order_by(func.count().desc())\
     .limit(limit).all()

    return [r[0] for r in results]