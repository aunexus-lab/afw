import os
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from datetime                   import datetime
from dotenv                     import load_dotenv
from joblib                     import dump
import psycopg2
from sklearn.model_selection    import train_test_split
from sklearn.preprocessing      import StandardScaler, LabelEncoder
from sklearn.metrics            import recall_score
from models.net                 import FirewallNet
from config.config              import MODEL_PATH 
from core.context.utils         import get_active_strategy_view
from core.context.utils         import is_valid_view_name
from core.context.utils         import register_training_run
from core.context.utils         import adopt_strategy
import time 

load_dotenv()
PG_DSN = os.getenv("PG_DSN")

def train_firewall_model():
    # 1. Load data from view `event_features_for_nn`
    view_name = get_active_strategy_view()
    print(f"Using active materialized view: {view_name}")

    if not is_valid_view_name(view_name):
        raise ValueError(f"Invalid view name: {view_name}. Ensure it is a valid identifier without special characters.")

    query = f"SELECT * FROM {view_name}"
    print(f"Loading data from materialized view {view_name} ...")

    with psycopg2.connect(PG_DSN) as conn:
        df = pd.read_sql(query, conn)

    # 2. Preprocessing ... 
    categorical_cols = ['action', 'parse_status']
    df_enriched = pd.get_dummies(df, columns=categorical_cols)

    le = LabelEncoder()
    df_enriched['label'] = le.fit_transform(df_enriched['label_action'])
    df_enriched.drop(columns=['label_action', 'ip', 'timestamp'], inplace=True)

    X = df_enriched.drop(columns=['label'])
    y = df_enriched['label']

    # Save feature order and label encoder
    print("📦 Saving feature order and label encoder ...")

    dump(X.columns.tolist(), 'models/nn_firewall_feature_order.joblib')
    dump(le, 'models/nn_firewall_label_encoder.joblib')

    # 3. Split data and scale features
    print("Splitting data and scaling features ...")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    dump(scaler, 'models/nn_firewall_scaler.joblib')

    # Tracking the training start time
    training_start_time = time.time()

    # 4. Training the model
    print("Training the FirewallNet model ...")

    device = torch.device("cpu")
    input_size = X_train_scaled.shape[1]
    output_size = len(le.classes_)
    model = FirewallNet(input_size=input_size, output_size=output_size)
    model.to(device)

    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    EPOCHS = 100
    BATCH_SIZE = 64
    patience = 5
    best_loss = float('inf')
    epochs_without_improvement = 0
    best_model_state = None
    best_accuracy = 0.0
    best_recall = 0.0

    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)

    print("Training model FirewallNet with enrich context ...")

    for epoch in range(EPOCHS):
        model.train()
        permutation = torch.randperm(X_train_tensor.size(0))
        epoch_loss = 0.0
        total_samples = 0

        for i in range(0, X_train_tensor.size(0), BATCH_SIZE):
            indices = permutation[i:i+BATCH_SIZE]
            batch_x = X_train_tensor[indices]
            batch_y = y_train_tensor[indices]

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            batch_size_actual = batch_x.size(0)
            epoch_loss += loss.item() * batch_size_actual
            total_samples += batch_size_actual

        avg_loss = epoch_loss / total_samples
        print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.4f}")

        model.eval()
        with torch.no_grad():
            logits = model(X_test_tensor)
            preds = torch.argmax(logits, dim=1)
            acc = (preds == y_test_tensor).float().mean().item()
            recall = recall_score(y_test_tensor.numpy(), preds.numpy(), average='macro')

            print(f"  Accuracy: {acc:.4f}")
            print(f"  Recall: {recall:.4f}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            best_model_state = model.state_dict()
            best_accuracy = acc
            best_recall = recall
            epochs_without_improvement = 0
            print("New best model")
        else:
            epochs_without_improvement += 1
            print(f"No improvement ({epochs_without_improvement})")

        if epochs_without_improvement >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

    
    print("Traninig completed and model saved to", MODEL_PATH)

    training_duration = time.time() - training_start_time
    print(f"Training duration: {training_duration:.2f} seconds")

    if adopt_strategy(best_recall):
        print("New model is better than previous, will be adopted.")

        # Store the best model if model will be adopted
        torch.save({
            'model_state_dict'  : best_model_state,
            'feature_order'     : X.columns.tolist(),
            'label_encoder'     : le
        }, MODEL_PATH)

        # Register the training run
        register_training_run(
            accuracy            =   best_accuracy,
            recall              =   best_recall,
            loss                =   best_loss,
            notes               =   "auto-training with enriched context",
            training_duration   =   training_duration,
            model_hash          =   True,
            compress            =   True   
        )

    else:
        print("New model is not better than previous, will not be adopted.")


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    train_firewall_model()
