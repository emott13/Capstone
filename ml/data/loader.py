import pandas as pd

from models import UserInteractions
from extensions import db
from datetime import datetime, timezone

"""
This module is responsible for loading the data from the database and preparing it for preprocessing.
Think of it like: Database → Pandas DataFrame → Ready for model training
"""

"""
This function pulls all user/product interactions from the database and convers them into a formal the ML model can use.
For example, it will take raw data like:
    user_id: 100234
    product_id: 987654321
    interaction_value: 5.0
    created_at: 2024-01-01 12:00:00
and convert it into a DataFrame with columns like:
    user_id | product_id | value
    100234  | 987654321  | 5.0 (after applying time decay)
"""
def load_data():
    # Query all interactions from the database
    interactions = db.session.query(UserInteractions).all()

    # Convert DB objects to Python dictionaries
    data = [{
        "user_id": i.user_id,
        "product_id": i.product_id,
        # applying time decay to interaction value means that more recent interactions will have a higher value than older ones, 
        # which can help the model to better capture current user preferences and trends.
        "value": apply_time_decay(i.interaction_value, i.created_at) 
    } for i in interactions]

    # Convert list of dictionaries to Pandas DataFrame
    df = pd.DataFrame(data)
    return df

"""
This function helps reduce the importance of older interactions and increase the importance of recent ones through time delay.
For example, if a user interacted with a product 30 days ago, the value of that interaction will be reduced by a factor of 0.95^30, making it less influential in the model's training compared to a more recent interaction.
"""

def apply_time_decay(value, created_at):
    # Calculate how many days old the interaction is
    days_old = (datetime.now(timezone.utc) - created_at).days
    # Compute decay factor
    decay = 0.95 ** days_old
    return value * decay