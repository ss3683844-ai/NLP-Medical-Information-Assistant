import json
import os
import re
import joblib


# ============================================================
# FILE PATHS
# ============================================================

MODEL_FILE = "models/intent_model.pkl"
DATA_FILE = "data/medical_data.json"

CONFIDENCE_THRESHOLD = 0.15


# ============================================================
# LOAD MODEL
# ============================================================

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}\n"
        "Run train_model.py first."
    )

model = joblib.load(MODEL_FILE)


# ============================================================
# LOAD MEDICAL DATA
# ============================================================

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Medical data not found: {DATA_FILE}"
    )

with open(DATA_FILE, "r", encoding="utf-8") as file:
    medical_data = json.load(file)


# ============================================================
# CREATE RESPONSE LOOKUP
# ============================================================

RESPONSES = {}

for item in medical_data:
    intent = item.get("intent")

    if intent:
        RESPONSES[intent] = item


# ============================================================
# GREETINGS
# ============================================================

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


# ============================================================
# EXACT MEDICAL TOPIC MAP
# ============================================================

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
    "exhausted": "fatigue",

    "itching": "itching",
    "itchy": "itching",

    "anxiety": "anxiety"
}


# ============================================================
# COMMON PHRASE MAP
# ============================================================

PHRASE_TOPIC_MAP = {

    # Fever
    "very high temperature": "fever",
    "high temperature": "fever",
    "i have a fever": "fever",
    "i have fever": "fever",
    "having fever": "fever",
    "feeling feverish": "fever",

    # Headache
    "head hurts": "headache",
    "head is hurting": "headache",
    "head pain": "headache",
    "pain in my head": "headache",
    "my head hurts": "headache",

    # Ear
    "ear hurts": "ear_problem",
    "ear is hurting": "ear_problem",
    "ears are hurting": "ear_problem",
    "my ears hurt": "ear_problem",
    "my ear hurts": "ear_problem",
    "pain in my ear": "ear_problem",
    "pain in my ears": "ear_problem",

    # Tooth
    "dental pain": "toothache",
    "tooth hurts": "toothache",
    "tooth is hurting": "toothache",
    "pain in my tooth": "toothache",
    "pain in my teeth": "toothache",
    "teeth hurt": "toothache",
    "my tooth hurts": "toothache",

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
    "extremely tired": "fatigue",
    "very tired": "fatigue",
    "feeling exhausted": "fatigue",
    "i feel exhausted": "fatigue",
    "no energy": "fatigue",
    "low energy": "fatigue"
}


# ============================================================
# MEDICAL KEYWORDS
# ============================================================

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
    "chest",
    "dengue",
    "malaria",
    "typhoid",
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
    "exhausted",
    "weak",
    "anxiety",
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


# ============================================================
# CHECK GREETING
# ============================================================

def is_greeting(text):

    cleaned = text.lower().strip()

    if cleaned in GREETING_WORDS:
        return True

    return False


# ============================================================
# CHECK MEDICAL QUESTION
# ============================================================

def is_medical_question(text):

    cleaned = text.lower().strip()

    # Exact known medical topic
    if cleaned in EXACT_TOPIC_MAP:
        return True

    # Known phrase
    if cleaned in PHRASE_TOPIC_MAP:
        return True

    # Medical keywords
    words = re.findall(r"\b[a-zA-Z]+\b", cleaned)

    for word in words:
        if word in MEDICAL_KEYWORDS:
            return True

    # Multi-word keyword check
    for keyword in MEDICAL_KEYWORDS:
        if " " in keyword and keyword in cleaned:
            return True

    return False


# ============================================================
# OUT OF DOMAIN RESPONSE
# ============================================================

def out_of_domain_response():

    return {
        "intent": "out_of_domain",
        "confidence": 1.0,
        "topic": "Non-medical question",
        "general_care": [
            "I can help with general medical and health-related questions.",
            "Please ask me about a symptom, health condition, or general medical topic."
        ],
        "medicine_information": (
            "I cannot provide medicine information for a "
            "non-medical topic."
        ),
        "dose_safety": (
            "Do not take medicine based on an unrelated "
            "chatbot response."
        ),
        "overdose_warning": (
            "Never take more medicine than recommended."
        ),
        "when_to_see_doctor": (
            "For serious health concerns, consult a healthcare professional."
        )
    }


# ============================================================
# UNKNOWN RESPONSE
# ============================================================

def unknown_response(confidence=0.0):

    return {
        "intent": "unknown",
        "confidence": confidence,
        "topic": "Possible Topic",
        "general_care": [
            "Please describe your symptoms more clearly.",
            "Include the main symptom and how long you have had it."
        ],
        "medicine_information": (
            "I cannot provide medicine information until "
            "the medical topic is understood clearly."
        ),
        "dose_safety": (
            "Do not take medicine based only on a "
            "low-confidence chatbot prediction."
        ),
        "overdose_warning": (
            "Never take more medicine than recommended."
        ),
        "when_to_see_doctor": (
            "If symptoms are severe, persistent, or worsening, "
            "consult a healthcare professional."
        )
    }


# ============================================================
# GREETING RESPONSE
# ============================================================

def greeting_response():

    return {
        "intent": "greeting",
        "confidence": 1.0,
        "topic": "Greeting",
        "general_care": [
            "Hello! I am your Medical Assistant.",
            "You can tell me about a symptom or health concern."
        ],
        "medicine_information": (
            "I can provide general health information, "
            "but I cannot replace a doctor."
        ),
        "dose_safety": (
            "Do not take medicine without following "
            "appropriate medical advice."
        ),
        "overdose_warning": (
            "Never take more medicine than recommended."
        ),
        "when_to_see_doctor": (
            "If you have severe or concerning symptoms, "
            "consult a healthcare professional."
        )
    }


# ============================================================
# GET RESPONSE FROM JSON
# ============================================================

def build_response(intent, confidence):

    item = RESPONSES.get(intent)

    if not item:
        return unknown_response(confidence)

    return {
        "intent": intent,
        "confidence": confidence,
        "topic": item.get(
            "intent",
            intent
        ),
        "general_care": item.get(
            "general_care",
            []
        ),
        "medicine_information": item.get(
            "medicine_information",
            "Please consult a healthcare professional for medicine advice."
        ),
        "dose_safety": item.get(
            "dose_safety",
            "Do not take medicine without appropriate medical advice."
        ),
        "overdose_warning": item.get(
            "overdose_warning",
            "Never take more medicine than recommended."
        ),
        "when_to_see_doctor": item.get(
            "when_to_see_doctor",
            "If symptoms are severe, persistent, or worsening, consult a healthcare professional."
        )
    }


# ============================================================
# MAIN RESPONSE FUNCTION
# ============================================================

def generate_response(text):

    if not text or not text.strip():
        return unknown_response(0.0)

    cleaned_text = text.lower().strip()

    # --------------------------------------------------------
    # 1. GREETING
    # --------------------------------------------------------

    if is_greeting(cleaned_text):
        return greeting_response()

    # --------------------------------------------------------
    # 2. NON-MEDICAL
    # --------------------------------------------------------

    if not is_medical_question(cleaned_text):
        return out_of_domain_response()

    # --------------------------------------------------------
    # 3. EXACT TOPIC MATCH
    # --------------------------------------------------------

    if cleaned_text in EXACT_TOPIC_MAP:

        intent = EXACT_TOPIC_MAP[cleaned_text]

        return build_response(
            intent,
            1.0
        )

    # --------------------------------------------------------
    # 4. COMMON PHRASE MATCH
    # --------------------------------------------------------

    if cleaned_text in PHRASE_TOPIC_MAP:

        intent = PHRASE_TOPIC_MAP[cleaned_text]

        return build_response(
            intent,
            1.0
        )

    # --------------------------------------------------------
    # 5. ML MODEL
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        [text]
    )[0]

    index = probabilities.argmax()

    intent = model.classes_[index]

    confidence = float(
        probabilities[index]
    )

    # --------------------------------------------------------
    # 6. LOW CONFIDENCE
    # --------------------------------------------------------

    if confidence < CONFIDENCE_THRESHOLD:

        return unknown_response(
            confidence
        )

    # --------------------------------------------------------
    # 7. RESPONSE LOOKUP
    # --------------------------------------------------------

    return build_response(
        intent,
        confidence
    )


# ============================================================
# COMMAND LINE CHAT
# ============================================================

def print_response(response):

    print("\n🤖 Medical Assistant\n")

    print(
        "🩺 Possible Topic:"
    )

    print(
        response["topic"]
    )

    print("\n🏠 General Care")

    for advice in response["general_care"]:
        print(f"- {advice}")

    print("\n💊 Medicine Information")

    print(
        response["medicine_information"]
    )

    print("\n📏 Dose Safety")

    print(
        response["dose_safety"]
    )

    print("\n⚠️ Overdose Warning")

    print(
        response["overdose_warning"]
    )

    print("\n🏥 When to See a Doctor")

    print(
        response["when_to_see_doctor"]
    )

    print(
        f"\nIntent: {response['intent']}"
    )

    print(
        f"Confidence: "
        f"{response['confidence'] * 100:.1f}%"
    )


# ============================================================
# START CHAT
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🩺 MEDICAL ASSISTANT")
    print("=" * 60)

    print(
        "\nHello! I am your Medical Assistant. "
        "How can I help you?"
    )

    print(
        "\nType 'exit' to quit."
    )

    while True:

        try:
            user_input = input("\nYou: ").strip()

        except (KeyboardInterrupt, EOFError):

            print(
                "\n\nGoodbye!"
            )

            break

        if user_input.lower() in {
            "exit",
            "quit",
            "bye"
        }:

            print(
                "\nMedical Assistant: "
                "Goodbye! Take care."
            )

            break

        response = generate_response(
            user_input
        )

        print_response(
            response
        )