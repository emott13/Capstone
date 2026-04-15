import torch
from torch.utils.data import Dataset

class InteractionDataset(Dataset):
    def __init__(self, df):
        self.users = torch.tensor(df["user_idx"].values)
        self.items = torch.tensor(df["product_idx"].values)
        self.labels = torch.tensor(df["value"].values, dtype=torch.float32)

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]