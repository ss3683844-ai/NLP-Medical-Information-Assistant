import json
import os
import joblib


# =========================================================
# FILE PATHS
# =========================================================

MODEL_FILE = "models/intent_model.pkl"
DATA_FILE = "data/medical_data.json"


# =========================================================
# CONFIDENCE THRESHOLD
# =========================================================

CONFIDENCE_THRESHOLD = 0.40


# =========================================================
# GREETING WORDS
# =========================================================

GREETING_WORDS = {
    "hi",
    "hello",
    "hey",
    "hii",
    "hiii",
    "good morning",
    "good afternoon",
    "good evening"
}


# =========================================================
# FILE CHECKS
# =========================================================

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(
        f"Model file not found: {MODEL_FILE}. "
        f"Run train_model.py first."
    )

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Medical data file not found: {DATA_FILE}"
    )


# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(MODEL_FILE)


# =========================================================
# LOAD MEDICAL DATA
# =========================================================

with open(DATA_FILE, "r", encoding="utf-8") as file:
    medical_data = json.load(file)


# =========================================================
# RESPONSE DATA
# =========================================================

responses = {
    item["intent"]: item.get("response", {})
    for item in medical_data
}


# =========================================================
# GREETING CHECK
# =========================================================

def is_greeting(text: str) -> bool:

    if not isinstance(text, str):
        return False

    cleaned_text = text.lower().strip()

    return cleaned_text in GREETING_WORDS


# =========================================================
# UNKNOWN RESPONSE
# =========================================================

def unknown_response(confidence=0.15):

    return {
        "intent": "unknown",
        "confidence": confidence,

        "problem":
            "I could not confidently understand "
            "the medical topic.",

        "general_care": [
            "Please describe your symptoms more clearly.",
            "Include the main symptom and how long "
            "you have had it."
        ],

        "medicine_information":
            "I cannot provide medicine information until "
            "the medical topic is understood clearly.",

        "dose_guidance":
            "Do not take medicine based only on a low-confidence "
            "chatbot prediction.",

        "overdose_warning":
            "Never take more medicine than recommended.",

        "doctor_advice":
            "If symptoms are severe, persistent, or worsening, "
            "consult a healthcare professional."
    }


# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_response(text: str):

    # -----------------------------------------------------
    # EMPTY INPUT
    # -----------------------------------------------------

    if not isinstance(text, str) or not text.strip():
        return unknown_response()


    # -----------------------------------------------------
    # GREETING
    # -----------------------------------------------------

    if is_greeting(text):

        response_data = responses.get("greeting")

        if response_data:

            return {
                "intent": "greeting",
                "confidence": 1.0,

                "problem":
                    response_data.get(
                        "problem",
                        "Hello! How can I help you with your health question?"
                    ),

                "general_care":
                    response_data.get(
                        "general_care",
                        []
                    ),

                "medicine_information":
                    response_data.get(
                        "medicine_information",
                        "I can provide general medical information."
                    ),

                "dose_guidance":
                    response_data.get(
                        "dose_guidance",
                        "Follow healthcare professional or "
                        "product-label instructions."
                    ),

                "overdose_warning":
                    response_data.get(
                        "overdose_warning",
                        "Never exceed the recommended dose."
                    ),

                "doctor_advice":
                    response_data.get(
                        "doctor_advice",
                        "Consult a healthcare professional when needed."
                    )
            }


    # -----------------------------------------------------
    # PREDICT PROBABILITIES
    # -----------------------------------------------------

    probabilities = model.predict_proba([text])[0]

    index = probabilities.argmax()

    intent = model.classes_[index]

    confidence = float(probabilities[index])


    # -----------------------------------------------------
    # CONFIDENCE CHECK
    # -----------------------------------------------------

    if confidence < CONFIDENCE_THRESHOLD:
        return unknown_response(confidence)


    # -----------------------------------------------------
    # GET RESPONSE DATA
    # -----------------------------------------------------

    response_data = responses.get(intent)

    if response_data is None:
        return unknown_response(confidence)


    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return {
        "intent": intent,
        "confidence": confidence,

        "problem":
            response_data.get(
                "problem",
                "Medical information"
            ),

        "general_care":
            response_data.get(
                "general_care",
                []
            ),

        "medicine_information":
            response_data.get(
                "medicine_information",
                "No medicine information available."
            ),

        "dose_guidance":
            response_data.get(
                "dose_guidance",
                "Follow the product label or "
                "healthcare professional's instructions."
            ),

        "overdose_warning":
            response_data.get(
                "overdose_warning",
                "Never exceed the recommended dose."
            ),

        "doctor_advice":
            response_data.get(
                "doctor_advice",
                "Consult a healthcare professional "
                "if symptoms persist or worsen."
            )
    }