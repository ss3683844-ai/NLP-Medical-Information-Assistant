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

CONFIDENCE_THRESHOLD = 0.15


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
# EXACT MEDICAL TOPIC MAP
# =========================================================

EXACT_TOPIC_MAP = {
    "fever": "fever",
    "headache": "headache",
    "migraine": "migraine",
    "cold": "cold",
    "flu": "flu",
    "cough": "cough",
    "sore throat": "sore_throat",
    "allergy": "allergy",
    "asthma": "asthma",
    "dengue": "dengue",
    "malaria": "malaria",
    "typhoid": "typhoid",
    "food poisoning": "food_poisoning",
    "stomach pain": "stomach_pain",
    "stomach ache": "stomach_pain",
    "vomiting": "vomiting",
    "vomit": "vomiting",
    "diarrhea": "diarrhea",
    "constipation": "constipation",
    "acidity": "acidity",
    "motion sickness": "motion_sickness",
    "skin rash": "skin_rash",
    "rash": "skin_rash",
    "eye problem": "eye_problem",
    "ear problem": "ear_problem",
    "earache": "ear_problem",
    "toothache": "toothache",
    "chest pain": "chest_pain",
    "breathing problem": "breathing_problem",
    "blood pressure": "blood_pressure",
    "diabetes": "diabetes",
    "back pain": "back_pain",
    "joint pain": "joint_pain",
    "dizziness": "dizziness",
    "fatigue": "fatigue",
    "itching": "itching",
    "anxiety": "anxiety"
}


# =========================================================
# MEDICAL KEYWORDS
# =========================================================

MEDICAL_KEYWORDS = {
    "pain",
    "ache",
    "headache",
    "migraine",
    "fever",
    "temperature",
    "cold",
    "flu",
    "cough",
    "throat",
    "sore",
    "allergy",
    "asthma",
    "breathing",
    "breathe",
    "chest",
    "dengue",
    "malaria",
    "typhoid",
    "food poisoning",
    "stomach",
    "vomiting",
    "vomit",
    "nausea",
    "diarrhea",
    "constipation",
    "acidity",
    "rash",
    "skin",
    "itch",
    "itching",
    "itchy",
    "eye",
    "ear",
    "tooth",
    "dizziness",
    "dizzy",
    "fatigue",
    "tired",
    "weak",
    "energy",
    "anxiety",
    "worried",
    "blood pressure",
    "pressure",
    "diabetes",
    "back",
    "joint",
    "medicine",
    "medication",
    "symptom",
    "symptoms",
    "health",
    "sick",
    "ill",
    "doctor",
    "disease"
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
# MEDICAL QUESTION CHECK
# =========================================================

def is_medical_question(text: str) -> bool:

    if not isinstance(text, str):
        return False

    cleaned_text = text.lower().strip()

    # Exact medical topic
    if cleaned_text in EXACT_TOPIC_MAP:
        return True

    # Medical keyword inside a sentence
    for keyword in MEDICAL_KEYWORDS:

        if keyword in cleaned_text:
            return True

    return False


# =========================================================
# OUT OF DOMAIN RESPONSE
# =========================================================

def out_of_domain_response():

    return {
        "intent": "out_of_domain",
        "confidence": 1.0,
        "message":
            "Sorry, I am your Medical Assistant. "
            "I can answer only medical and health-related questions."
    }


# =========================================================
# UNKNOWN RESPONSE
# =========================================================

def unknown_response(confidence=0.0):

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
    # MEDICAL / NON-MEDICAL CHECK
    # -----------------------------------------------------

    if not is_medical_question(text):

        return out_of_domain_response()


    # -----------------------------------------------------
    # EXACT TOPIC OR ML PREDICTION
    # -----------------------------------------------------

    cleaned_text = text.lower().strip()

    # Short/exact medical topics
    if cleaned_text in EXACT_TOPIC_MAP:

        intent = EXACT_TOPIC_MAP[cleaned_text]
        confidence = 1.0

    # Longer medical sentences
    else:

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
    # RETURN MEDICAL RESPONSE
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