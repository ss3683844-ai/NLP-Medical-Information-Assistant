import json
import os
import re
import joblib


# =========================================================
# FILE PATHS
# =========================================================

MODEL_FILE = "models/intent_model.pkl"
DATA_FILE = "data/medical_data.json"

CONFIDENCE_THRESHOLD = 0.15


# =========================================================
# GREETINGS
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
# EXACT MEDICAL TOPICS
# =========================================================

EXACT_TOPIC_MAP = {
    "fever": "fever",
    "temperature": "fever",
    "high temperature": "fever",
    "headache": "headache",
    "migraine": "migraine",
    "cold": "cold",
    "flu": "flu",
    "influenza": "flu",
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
    "ear pain": "ear_problem",
    "toothache": "toothache",
    "dental pain": "toothache",
    "tooth pain": "toothache",
    "teeth pain": "toothache",
    "chest pain": "chest_pain",
    "breathing problem": "breathing_problem",
    "blood pressure": "blood_pressure",
    "diabetes": "diabetes",
    "back pain": "back_pain",
    "joint pain": "joint_pain",
    "dizziness": "dizziness",
    "dizzy": "dizziness",
    "fatigue": "fatigue",
    "tired": "fatigue",
    "tiredness": "fatigue",
    "itching": "itching",
    "itchy": "itching",
    "anxiety": "anxiety"
}


# =========================================================
# COMMON MEDICAL PHRASES
# =========================================================

PHRASE_TOPIC_MAP = {

    # Headache
    "i have a headache": "headache",
    "i have headache": "headache",
    "my head hurts": "headache",
    "my head is hurting": "headache",
    "head is hurting": "headache",
    "head pain": "headache",
    "pain in my head": "headache",
    "why does my head hurt": "headache",
    "i am having a headache": "headache",

    # Fever
    "i have a fever": "fever",
    "i have fever": "fever",
    "having fever": "fever",
    "feeling feverish": "fever",
    "my temperature is high": "fever",
    "very high temperature": "fever",

    # Ear
    "my ear hurts": "ear_problem",
    "my ears hurt": "ear_problem",
    "my ears are hurting": "ear_problem",
    "ear is hurting": "ear_problem",
    "pain in my ear": "ear_problem",
    "pain in my ears": "ear_problem",

    # Tooth
    "dental pain": "toothache",
    "tooth pain": "toothache",
    "my tooth hurts": "toothache",
    "my teeth hurt": "toothache",
    "pain in my tooth": "toothache",
    "pain in my teeth": "toothache",

    # Constipation
    "hard stool": "constipation",
    "hard stools": "constipation",
    "cannot pass stool": "constipation",
    "can't pass stool": "constipation",
    "difficulty passing stool": "constipation",
    "difficult bowel movement": "constipation",

    # Acidity
    "stomach acid": "acidity",
    "stomach acid problem": "acidity",
    "acid in my stomach": "acidity",
    "acid reflux": "acidity",
    "burning after meals": "acidity",
    "burning in my stomach": "acidity",
    "heartburn": "acidity",

    # Motion sickness
    "nauseous in a car": "motion_sickness",
    "nauseous while travelling": "motion_sickness",
    "sick in a car": "motion_sickness",
    "sick while travelling": "motion_sickness",
    "car sickness": "motion_sickness",
    "carsick": "motion_sickness",

    # Flu
    "tell me about influenza": "flu",
    "influenza symptoms": "flu",
    "signs of influenza": "flu",
    "i have influenza": "flu",

    # Fatigue
    "very tired": "fatigue",
    "extremely tired": "fatigue",
    "feeling exhausted": "fatigue",
    "i feel exhausted": "fatigue",
    "no energy": "fatigue",
    "low energy": "fatigue"
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
    "influenza",
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
# CHECK FILES
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

    # Exact topic
    if cleaned_text in EXACT_TOPIC_MAP:
        return True

    # Common phrase
    if cleaned_text in PHRASE_TOPIC_MAP:
        return True

    # Multi-word medical keywords
    for keyword in MEDICAL_KEYWORDS:
        if " " in keyword and keyword in cleaned_text:
            return True

    # Single-word medical keywords
    words = set(re.findall(r"\b\w+\b", cleaned_text))

    for keyword in MEDICAL_KEYWORDS:
        if keyword in words:
            return True

    return False


# =========================================================
# OUT OF DOMAIN
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
# UNKNOWN
# =========================================================

def unknown_response(confidence=0.0):

    return {
        "intent": "unknown",
        "confidence": confidence,
        "problem":
            "I could not confidently understand the medical topic.",
        "general_care": [
            "Please describe your symptoms more clearly.",
            "Include the main symptom and how long you have had it."
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

    # Empty input
    if not isinstance(text, str) or not text.strip():
        return unknown_response()

    # Greeting
    if is_greeting(text):

        response_data = responses.get("greeting", {})

        return {
            "intent": "greeting",
            "confidence": 1.0,
            "problem": response_data.get(
                "problem",
                "Hello! How can I help you with your health question?"
            ),
            "general_care": response_data.get(
                "general_care",
                []
            ),
            "medicine_information": response_data.get(
                "medicine_information",
                "I can provide general medical information."
            ),
            "dose_guidance": response_data.get(
                "dose_guidance",
                "Follow healthcare professional or product-label instructions."
            ),
            "overdose_warning": response_data.get(
                "overdose_warning",
                "Never exceed the recommended dose."
            ),
            "doctor_advice": response_data.get(
                "doctor_advice",
                "Consult a healthcare professional when needed."
            )
        }

    # Medical / non-medical check
    if not is_medical_question(text):
        return out_of_domain_response()

    cleaned_text = text.lower().strip()

    # =====================================================
    # EXACT TOPIC
    # =====================================================

    if cleaned_text in EXACT_TOPIC_MAP:

        intent = EXACT_TOPIC_MAP[cleaned_text]
        confidence = 1.0

    # =====================================================
    # COMMON PHRASE
    # =====================================================

    elif cleaned_text in PHRASE_TOPIC_MAP:

        intent = PHRASE_TOPIC_MAP[cleaned_text]
        confidence = 1.0

    # =====================================================
    # ML MODEL
    # =====================================================

    else:

        probabilities = model.predict_proba([text])[0]

        index = probabilities.argmax()

        intent = model.classes_[index]

        confidence = float(probabilities[index])

    # Confidence check
    if confidence < CONFIDENCE_THRESHOLD:
        return unknown_response(confidence)

    # Response data
    response_data = responses.get(intent)

    if response_data is None:
        return unknown_response(confidence)

    # Final response
    return {
        "intent": intent,
        "confidence": confidence,

        "problem": response_data.get(
            "problem",
            "Medical information"
        ),

        "general_care": response_data.get(
            "general_care",
            []
        ),

        "medicine_information": response_data.get(
            "medicine_information",
            "No medicine information available."
        ),

        "dose_guidance": response_data.get(
            "dose_guidance",
            "Follow the product label or healthcare professional's instructions."
        ),

        "overdose_warning": response_data.get(
            "overdose_warning",
            "Never exceed the recommended dose."
        ),

        "doctor_advice": response_data.get(
            "doctor_advice",
            "Consult a healthcare professional if symptoms persist or worsen."
        )
    }