import torch
import torch.nn as nn


class RecommenderModel(nn.Module):
    """
    Neural Collaborative Filtering Model with Bias Terms
    """

    def __init__(self, num_users, num_items, embedding_dim=32):
        super(RecommenderModel, self).__init__()

        # Embeddings
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)

        # Bias terms
        self.user_bias = nn.Embedding(num_users, 1)
        self.item_bias = nn.Embedding(num_items, 1)

        # Neural Network (MLP)
        self.fc = nn.Sequential(
            nn.Linear(embedding_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 1)
        )

        self._init_weights()

    def _init_weights(self):
        """Initialize embeddings for better training"""
        nn.init.normal_(self.user_embedding.weight, std=0.01)
        nn.init.normal_(self.item_embedding.weight, std=0.01)

        # Initialize biases
        nn.init.zeros_(self.user_bias.weight)
        nn.init.zeros_(self.item_bias.weight)

    def forward(self, user_ids, item_ids):
        user_vec = self.user_embedding(user_ids)
        item_vec = self.item_embedding(item_ids)

        # Concatenate embeddings
        x = torch.cat([user_vec, item_vec], dim=1)

        # Pass through neural network
        output = self.fc(x)

        # Add bias
        bias = self.user_bias(user_ids) + self.item_bias(item_ids)

        return output.squeeze() + bias.squeeze()