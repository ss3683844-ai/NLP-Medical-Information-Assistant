import json
import os
from collections import Counter

import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# 1. FILE PATHS
# ============================================================

DATA_FILE = "data/medical_data.json"
MODEL_FILE = "models/intent_model.pkl"


# ============================================================
# 2. LOAD DATASET
# ============================================================

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Make sure medical_data.json is inside the data folder."
    )

with open(DATA_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


# ============================================================
# 3. VALIDATE DATASET STRUCTURE
# ============================================================

if not isinstance(data, list):
    raise ValueError(
        "medical_data.json must contain a JSON array/list."
    )

questions = []
labels = []

for item in data:

    if not isinstance(item, dict):
        raise ValueError(
            "Every item in medical_data.json must be an object."
        )

    if "intent" not in item:
        raise ValueError(
            "An item is missing the 'intent' field."
        )

    if "questions" not in item:
        raise ValueError(
            f"Intent '{item['intent']}' is missing the "
            "'questions' field."
        )

    intent = item["intent"]
    intent_questions = item["questions"]

    if not isinstance(intent, str) or not intent.strip():
        raise ValueError(
            "Every intent must be a non-empty string."
        )

    if not isinstance(intent_questions, list):
        raise ValueError(
            f"'questions' for intent '{intent}' must be a list."
        )

    if len(intent_questions) == 0:
        raise ValueError(
            f"Intent '{intent}' has no training questions."
        )

    for question in intent_questions:

        if not isinstance(question, str):
            raise ValueError(
                f"Invalid question in intent '{intent}'. "
                "Every question must be a string."
            )

        question = question.strip()

        if question:
            questions.append(question)
            labels.append(intent.strip())


# ============================================================
# 4. DATASET INFORMATION
# ============================================================

unique_intents = sorted(set(labels))

print("\n" + "=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print(f"Total training questions : {len(questions)}")
print(f"Total intents             : {len(unique_intents)}")

print("\nQuestions per intent:")
print("-" * 60)

intent_counts = Counter(labels)

for intent in unique_intents:
    print(f"{intent:25} : {intent_counts[intent]}")


# ============================================================
# 5. CHECK DUPLICATE INTENTS
# ============================================================

intent_names = [
    item["intent"].strip().lower()
    for item in data
]

duplicate_intents = [
    intent
    for intent, count in Counter(intent_names).items()
    if count > 1
]

if duplicate_intents:

    print("\nWARNING: Duplicate intent objects found:")

    for intent in duplicate_intents:
        print(" -", intent)

else:
    print("\nOK: No duplicate intent objects found.")


# ============================================================
# 6. CHECK DUPLICATE QUESTIONS
# ============================================================

question_counts = Counter(
    question.lower().strip()
    for question in questions
)

duplicate_questions = [
    question
    for question, count in question_counts.items()
    if count > 1
]

if duplicate_questions:

    print("\nWARNING: Duplicate questions found:")

    for question in duplicate_questions[:20]:
        print(" -", question)

    if len(duplicate_questions) > 20:
        print(
            f"... and {len(duplicate_questions) - 20} "
            "more duplicates."
        )

else:
    print("\nOK: No duplicate questions found.")


# ============================================================
# 7. CHECK QUESTIONS THAT APPEAR UNDER DIFFERENT INTENTS
# ============================================================

question_to_intents = {}

for question, intent in zip(questions, labels):

    normalized_question = question.lower().strip()

    if normalized_question not in question_to_intents:
        question_to_intents[normalized_question] = set()

    question_to_intents[normalized_question].add(intent)


cross_intent_duplicates = {
    question: intents
    for question, intents in question_to_intents.items()
    if len(intents) > 1
}

if cross_intent_duplicates:

    print("\nWARNING: Same question used for multiple intents:")

    for question, intents in list(
        cross_intent_duplicates.items()
    )[:20]:

        print(
            f" - {question} -> "
            f"{', '.join(sorted(intents))}"
        )

else:
    print(
        "\nOK: No questions shared between different intents."
    )


# ============================================================
# 8. CHECK MINIMUM QUESTIONS
# ============================================================

print("\n" + "=" * 60)
print("DATASET QUALITY CHECK")
print("=" * 60)

minimum_questions = min(intent_counts.values())

if minimum_questions < 10:

    print(
        "WARNING: Some intents have fewer than 10 questions."
    )

else:

    print(
        "OK: Every intent has at least 10 questions."
    )


if minimum_questions < 25:

    print(
        "NOTE: Dataset is relatively small. "
        "The model may have low confidence on new wording."
    )


# ============================================================
# 9. CHECK FOR VERY SMALL INTENTS
# ============================================================

small_intents = [
    intent
    for intent, count in intent_counts.items()
    if count < 15
]

if small_intents:

    print("\nIntents with fewer than 15 questions:")

    for intent in sorted(
        small_intents,
        key=lambda x: intent_counts[x]
    ):

        print(
            f" - {intent}: "
            f"{intent_counts[intent]} questions"
        )

else:

    print(
        "\nOK: Every intent has at least 15 questions."
    )


# ============================================================
# 10. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    questions,
    labels,
    test_size=0.20,
    random_state=42,
    stratify=labels
)

print("\n" + "=" * 60)
print("TRAIN / TEST SPLIT")
print("=" * 60)

print(f"Training examples : {len(X_train)}")
print(f"Testing examples  : {len(X_test)}")


# ============================================================
# 11. CREATE MODEL PIPELINE
# ============================================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,

            # IMPORTANT:
            # Use Python None, not the string "None".
            #
            # stop_words="None"  <-- WRONG
            # stop_words=None    <-- CORRECT
            stop_words=None,

            # Unigrams + bigrams
            ngram_range=(1, 2),

            # Helps reduce the effect of repeated words
            sublinear_tf=True,

            # Keep words that appear at least once
            min_df=1
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=2000
        )
    )
])


# ============================================================
# 12. TRAIN MODEL
# ============================================================

print("\n" + "=" * 60)
print("TRAINING MODEL")
print("=" * 60)

model.fit(X_train, y_train)

print(
    "Model training completed successfully."
)


# ============================================================
# 13. PREDICTION
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 14. ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ============================================================
# 15. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")
print("-" * 60)

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# 16. SHOW INCORRECT TEST PREDICTIONS
# ============================================================

print("\n" + "=" * 60)
print("INCORRECT TEST PREDICTIONS")
print("=" * 60)

wrong_count = 0

test_probabilities = model.predict_proba(
    X_test
)

for (
    question,
    actual,
    predicted,
    probabilities
) in zip(
    X_test,
    y_test,
    y_pred,
    test_probabilities
):

    if actual != predicted:

        predicted_index = probabilities.argmax()

        confidence = float(
            probabilities[predicted_index]
        )

        print("\nQuestion   :", question)
        print("Actual     :", actual)
        print("Predicted  :", predicted)
        print(
            "Confidence :",
            f"{confidence * 100:.2f}%"
        )

        wrong_count += 1


if wrong_count == 0:

    print(
        "No incorrect predictions found."
    )

else:

    print(
        f"\nTotal incorrect predictions: "
        f"{wrong_count}"
    )


# ============================================================
# 17. SAVE MODEL
# ============================================================

model_folder = os.path.dirname(
    MODEL_FILE
)

if model_folder:
    os.makedirs(
        model_folder,
        exist_ok=True
    )

joblib.dump(
    model,
    MODEL_FILE
)

print("\n" + "=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(
    f"Saved to: {MODEL_FILE}"
)


# ============================================================
# 18. TEST SAMPLE QUESTIONS
# ============================================================

print("\n" + "=" * 60)
print("SAMPLE PREDICTIONS")
print("=" * 60)

sample_questions = [

    # Fever
    "I have a very high temperature",

    # Headache
    "My head is hurting badly",

    # Cold
    "I have a runny nose and sneezing",

    # Cough
    "I am coughing a lot",

    # Chest pain
    "My chest hurts",

    # Breathing
    "I am having difficulty breathing",

    # Blood pressure
    "My blood pressure is high",

    # Dizziness
    "I feel dizzy",

    # Stomach pain
    "I have stomach pain",

    # Vomiting
    "I have vomiting",

    # Itching
    "My skin is very itchy",

    # Ear
    "My ear hurts",

    # Tooth
    "I have dental pain",

    # Constipation
    "I have hard stools",

    # Acidity
    "I have stomach acid",

    # Motion sickness
    "I feel nauseous in a car",

    # Flu
    "Tell me about influenza",

    # Fatigue
    "I am extremely tired"
]


for question in sample_questions:

    prediction = model.predict(
        [question]
    )[0]

    probabilities = model.predict_proba(
        [question]
    )[0]

    predicted_index = probabilities.argmax()

    confidence = float(
        probabilities[predicted_index]
    )

    print("\nQuestion   :", question)
    print("Prediction :", prediction)
    print(
        "Confidence :",
        f"{confidence * 100:.2f}%"
    )


# ============================================================
# 19. FINISHED
# ============================================================

print("\n" + "=" * 60)
print("TRAINING FINISHED SUCCESSFULLY")
print("=" * 60)