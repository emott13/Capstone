import torch
from torch.utils.data import Dataset
import random


class BPRDataset(Dataset):
    """
    Dataset for Bayesian Personalized Ranking (BPR)

    Returns:
        user_idx
        positive_item_idx
        negative_item_idx
    """

    def __init__(self, df, num_items):
        self.df = df
        self.num_items = num_items

        # Build user → interacted items map (fast lookup)
        self.user_items = self._build_user_items()

        # Store unique users for sampling
        self.users = list(self.user_items.keys())

    def _build_user_items(self):
        user_items = {}

        for _, row in self.df.iterrows():
            user = row["user_idx"]
            item = row["product_idx"]

            if user not in user_items:
                user_items[user] = set()

            user_items[user].add(item)

        return user_items

    def __len__(self):
        # We generate samples dynamically, so length = number of interactions
        return len(self.df)

    def __getitem__(self, idx):
        # 1. Pick a random user (NOT based on idx)
        user = random.choice(self.users)

        # 2. Pick a positive item for that user
        pos_item = random.choice(list(self.user_items[user]))

        # 3. Sample a negative item (not interacted with)
        while True:
            neg_item = random.randint(0, self.num_items - 1)
            if neg_item not in self.user_items[user]:
                break

        return (
            torch.tensor(user, dtype=torch.long),
            torch.tensor(pos_item, dtype=torch.long),
            torch.tensor(neg_item, dtype=torch.long)
        )