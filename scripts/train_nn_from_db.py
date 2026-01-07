# scripts/train_nn_from_db.py

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from models.net import FirewallNet

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "afw",
    "user": "your_user",
    "password": "your_password",
}

MODEL_PATH = "models/firewall_nn.pt"
REPORT_PATH = "outputs/metrics_nn_report.txt"
CONFUSION_IMG = "outputs/confusion_matrix.png"

FEATURES = ["event_count", "failed_logins", "dst_port", "ip_score"]
LABEL_COLUMN = "label"

def load_data():
    conn = psycopg2.connect(**DB_CONFIG)
    query = f"SELECT {', '.join(FEATURES + [LABEL_COLUMN])} FROM vw_event_summary"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def train_model(df):
    X = torch.tensor(df[FEATURES].values, dtype=torch.float32)
    le = LabelEncoder()
    y = torch.tensor(le.fit_transform(df[LABEL_COLUMN]), dtype=torch.long)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = FirewallNet(input_size=X.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(100):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = loss_fn(output, y_train)
        loss.backward()
        optimizer.step()

    # Evaluación
    model.eval()
    y_pred = torch.argmax(model(X_test), dim=1)
    y_true = y_test

    labels = le.classes_
    report = classification_report(y_true, y_pred, target_names=labels, digits=4)
    print(report)

    with open(REPORT_PATH, "w") as f:
        f.write(report)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(CONFUSION_IMG)
    print(f"✅ Report saved to {REPORT_PATH}, confusion matrix to {CONFUSION_IMG}")

    torch.save({
        "model_state_dict": model.state_dict(),
        "label_encoder": le,
        "feature_order": FEATURES,
    }, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    df = load_data()
    train_model(df)
