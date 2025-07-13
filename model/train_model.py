import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv('../data/login_attempts.csv')

# Convert categorical 'ip_address_risk' to numerical using one-hot encoding
df = pd.get_dummies(df, columns=['ip_address_risk'], drop_first=True)

# Define features (X) and target (y)
X = df.drop('is_locked', axis=1)
y = df['is_locked']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the RandomForestClassifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Save the trained model
joblib.dump(model, 'classical_agent_model.pkl')

# Save the columns used for training
joblib.dump(X.columns.tolist(), 'model_columns.pkl')