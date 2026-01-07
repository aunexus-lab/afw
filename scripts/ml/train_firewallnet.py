import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from joblib import dump
import psycopg2
import os
from dotenv import load_dotenv
from models.net import FirewallNet
from config.config import MODEL_PATH  # OR fixed path to your model directory
from sklearn.metrics import accuracy_score, recall_score, confusion_matrix
import numpy as np
from sklearn.utils.class_weight import compute_class_weight


# Load environment variables
load_dotenv()
PG_DSN = os.getenv("PG_DSN")
query = "SELECT * FROM event_features_for_nn"
with psycopg2.connect(PG_DSN) as conn:
    df = pd.read_sql(query, conn)

print(df["label_action"].value_counts())

# One-hot encoding categorical columns 
categorical_cols = ['action', 'parse_status']
df = pd.get_dummies(df, columns=categorical_cols)

# Labe encoding label action
le = LabelEncoder()
df['label'] = le.fit_transform(df['label_action'])
df.drop(columns=['label_action', 'ip', 'timestamp'], inplace=True)

# Split features and labels
X = df.drop(columns=['label'])
y = df['label']
feature_order = X.columns.tolist()

# Save feature order and label encoder
dump(feature_order, 'models/nn_firewall_feature_order.joblib')
dump(le, 'models/nn_firewall_label_encoder.joblib')

# Data Splitting
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scalar features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
dump(scaler, 'models/nn_firewall_scaler.joblib')

# Tensor conversion
X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)

# Class weights for imbalanced dataset
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y),
    y=y
)

# Create model and optimizer
input_size = X_train_tensor.shape[1]
output_size = len(le.classes_)  # class's count
model = FirewallNet(input_size=input_size, output_size=output_size)
optimizer = optim.Adam(model.parameters(), lr=0.001)

class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

# criterion = nn.CrossEntropyLoss()

# Training loop
EPOCHS = 100
BATCH_SIZE = 64

# Improvement control variable
best_loss = float('inf')
patience = 5
epochs_without_improvement = 0
best_model_state = None
epoch_loss = 0.0
total_batches = 0
num_samples = 0

print("Data distribution by classes :")
print(y.value_counts(normalize=True))


for epoch in range(EPOCHS):
    model.train()
    permutation = torch.randperm(X_train_tensor.size(0))
    for i in range(0, X_train_tensor.size(0), BATCH_SIZE):
        indices = permutation[i:i+BATCH_SIZE]
        batch_x, batch_y = X_train_tensor[indices], y_train_tensor[indices]

        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

        batch_size_actual = batch_x.size(0)
        epoch_loss += loss.item() * batch_size_actual  # Ponderación correcta
        num_samples += batch_size_actual

    avg_loss = epoch_loss / num_samples
    print(f"Epoch {epoch+1}/{EPOCHS} - Avg. Loss: {avg_loss:.4f}")

    model.eval()
    with torch.no_grad():
        logits = model(X_test_tensor)
        preds = torch.argmax(logits, dim=1)

        acc = accuracy_score(y_test_tensor.numpy(), preds.numpy())
        recall = recall_score(y_test_tensor.numpy(), preds.numpy(), average='macro')

        print(f"🔎 Accuracy: {acc:.4f} | Recall (macro): {recall:.4f}")


    if loss.item() < best_loss:
        best_loss = loss.item()
        epochs_without_improvement = 0
        best_model_state = model.state_dict()  # Guardamos el mejor estado
        print(f"New Loss: {best_loss:.4f}")
    else:
        epochs_without_improvement += 1
        print(f"Without improvement: {epochs_without_improvement}")

    if epochs_without_improvement >= patience:
        print(f"Early training stop at epoch {epoch+1}")
        break


# Save the model as checkpoint
torch.save({
    'model_state_dict': best_model_state,
    'feature_order': feature_order,
    'label_encoder': le,
}, MODEL_PATH)

print("Traninig completed and model saved to", MODEL_PATH)
