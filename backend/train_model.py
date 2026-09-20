import json
import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# Load dataset
with open(
    "data/medical_data.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


# Prepare training data
texts = []
labels = []

for item in data:
    for question in item["questions"]:
        texts.append(question)
        labels.append(item["intent"])


print("Total training examples:", len(texts))
print("Total intents:", len(set(labels)))


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)


# Create NLP pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000
        )
    )
])


# Train model
model.fit(X_train, y_train)


# Test model
predictions = model.predict(X_test)


# Calculate accuracy
accuracy = accuracy_score(y_test, predictions)

print("\nModel Evaluation")
print("------------------------")
print("Accuracy:", round(accuracy * 100, 2), "%")


# Classification report
print("\nClassification Report")
print("------------------------")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# Save model
os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/intent_model.pkl"
)

print("\nModel trained and saved successfully!")
print("Model file: models/intent_model.pkl")