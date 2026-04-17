import pandas as pd
import random

"""
This module contains functions for preprocessing the data before feeding it into the model.
Think of it like: Raw database data → Cleaned & formatted → Ready for AI model
"""


"""
Converts raw user and product IDs into integer indices for the model, and creates mapping dictionaries

For example, database has information like
    user_id: 100234
    product_id: 987654321
but the model needs
    user_idx: 0
    product_idx: 0
and we have to remember that user_id 100234 corresponds to user_idx 0, hence the mappings.
"""
def encode_ids(df):
    # Get unique IDs
    user_ids = df["user_id"].unique()
    product_ids = df["product_id"].unique()

    # Create mappings
    user_map = {id: i for i, id in enumerate(user_ids)}
    product_map = {id: i for i, id in enumerate(product_ids)}

    # Map original IDs to indices
    df["user_idx"] = df["user_id"].map(user_map)
    df["product_idx"] = df["product_id"].map(product_map)

    return df, user_map, product_map

"""
Normalizes the values in the DataFrame to a range between 0 and 1.

Values can look like:
    'purchase' → 5.0,
    'add_to_cart' → 3.0,
    'view' → 1.0

After normalization, they will be scaled to:
    'purchase' → 1.0,
    'add_to_cart' → 0.6,
    'view' → 0.2
"""
def normalize_values(df):
    # Normalize the 'value' column to be between 0 and 1
    df["value"] = df["value"] / df["value"].max()
    return df

"""
Adds negative samples to the dataset for better training of the model.
"""
def add_negative_samples(df, num_items, num_negatives=2):
    # Get all possible items
    all_items = set(range(num_items))
    new_rows = []

    # Loop through each user
    for user in df["user_idx"].unique():
        # Get items the user has interacted with
        user_items = set(df[df["user_idx"] == user]["product_idx"])

        # Get negative samples (items the user has NOT interacted with)
        negative_items = list(all_items - user_items)

        if not negative_items:
            continue

        # Randomly sample negative items (you can adjust the number of negatives per user)
        samples = random.sample(
            negative_items,
            min(len(negative_items), num_negatives)
        )

        # Add new rows for negative samples with value 0
        for item in samples:
            new_rows.append({
                "user_idx": user,
                "product_idx": item,
                "value": 0.0
            })

    # Append new negative samples to the original DataFrame
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    return df