import torch
from torch.utils.data import DataLoader
import os
import pickle
from extensions import app

from ml.data.loader import load_data
from ml.data.preprocessing import encode_ids
from ml.training.dataset import BPRDataset
from ml.models.recommender_model import RecommenderModel


# ---------- CONFIG ----------
BATCH_SIZE = 64
EPOCHS = 5
LEARNING_RATE = 0.001

MODEL_PATH = "ml/saved_models/recommender.pt"
MAPPINGS_PATH = "ml/saved_models/mappings.pkl"


def bpr_loss(pos_scores, neg_scores):
    """
    Bayesian Personalized Ranking loss

    Encourages:
        pos_score > neg_score
    """
    return -torch.mean(torch.log(torch.sigmoid(pos_scores - neg_scores) + 1e-8))


def train():
    print("Loading data...")
    df = load_data()

    if df.empty:
        raise ValueError("No interaction data found. Did you backfill?")

    print(f"Loaded {len(df)} interactions")

    # ---------- ENCODE IDS ----------
    print("Encoding IDs...")
    df, user_map, product_map = encode_ids(df)

    num_users = len(user_map)
    num_items = len(product_map)

    print(f"Users: {num_users}, Items: {num_items}")

    # ---------- DATASET (BPR VERSION) ----------
    dataset = BPRDataset(df, num_items)
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    # ---------- DEVICE ----------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # ---------- MODEL ----------
    model = RecommenderModel(num_users, num_items).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # ---------- TRAIN LOOP ----------
    print("Starting BPR training...\n")

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for user, pos_item, neg_item in dataloader:
            user = user.to(device)
            pos_item = pos_item.to(device)
            neg_item = neg_item.to(device)

            # ---------- FORWARD PASS ----------
            pos_scores = model(user, pos_item)
            neg_scores = model(user, neg_item)

            # ---------- LOSS ----------
            loss = bpr_loss(pos_scores, neg_scores)

            # ---------- BACKPROP ----------
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{EPOCHS} - BPR Loss: {avg_loss:.4f}")

    # ---------- SAVE MODEL ----------
    os.makedirs("ml/saved_models", exist_ok=True)

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    # ---------- SAVE MAPPINGS ----------
    with open(MAPPINGS_PATH, "wb") as f:
        pickle.dump({
            "user_map": user_map,
            "product_map": product_map
        }, f)

    print(f"Mappings saved to {MAPPINGS_PATH}")


if __name__ == "__main__":
    with app.app_context():
        train()