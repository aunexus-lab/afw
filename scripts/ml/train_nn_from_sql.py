import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from joblib import dump
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

PG_DSN = os.getenv("PG_DSN")

# Step 1: Fetch data from the view
query = "SELECT * FROM event_features_for_nn"
with psycopg2.connect(PG_DSN) as conn:
    df = pd.read_sql(query, conn)

# Step 2: Encode categorical features
categorical_cols = ['action', 'parse_status']
df = pd.get_dummies(df, columns=categorical_cols)

# Step 3: Encode labels
le = LabelEncoder()
df['label'] = le.fit_transform(df['label_action'])
df.drop(columns=['label_action', 'ip', 'timestamp'], inplace=True)

# Step 4: Prepare features and target
X = df.drop(columns=['label'])
y = df['label']

# Save column order for future inference
dump(X.columns.tolist(), 'models/nn_firewall_feature_order.joblib')

# Step 5: Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 6: Train neural network
model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)
model.fit(X_train_scaled, y_train)

# Step 7: Save model and scaler
dump(model, 'models/nn_firewall_model.joblib')
dump(scaler, 'models/nn_firewall_scaler.joblib')
dump(le, 'models/nn_firewall_label_encoder.joblib')

print("✅ Neural network trained and saved successfully.")
