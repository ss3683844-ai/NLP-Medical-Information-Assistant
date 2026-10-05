import re


# ============================================================
# EMERGENCY KEYWORDS / PHRASES
# ============================================================

EMERGENCY_KEYWORDS = [
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "unable to breathe",
    "not breathing",
    "severe chest pain",
    "heavy bleeding",
    "severe bleeding",
    "unconscious",
    "loss of consciousness",
    "seizure",
    "stroke",
]


# ============================================================
# NEGATIVE PHRASES
# ============================================================

NEGATIVE_PHRASES = [
    "no chest pain",
    "don't have chest pain",
    "do not have chest pain",
    "without chest pain",

    "no difficulty breathing",
    "don't have difficulty breathing",
    "do not have difficulty breathing",
    "without difficulty breathing",

    "no severe bleeding",
    "don't have severe bleeding",
    "do not have severe bleeding",
]


# ============================================================
# CHECK EMERGENCY
# ============================================================

def check_emergency(text: str) -> bool:

    if not isinstance(text, str):
        return False

    text = text.lower().strip()

    if not text:
        return False


    # --------------------------------------------------------
    # Remove obvious negative phrases before checking
    # --------------------------------------------------------

    for phrase in NEGATIVE_PHRASES:
        text = text.replace(phrase, "")


    # --------------------------------------------------------
    # Check emergency phrases
    # --------------------------------------------------------

    for keyword in EMERGENCY_KEYWORDS:

        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text):
            return True


    return False


# ============================================================
# EMERGENCY RESPONSE
# ============================================================

def emergency_response():

    return {
        "intent": "emergency",

        "confidence": 1.0,

        "problem": (
            "Your message may describe a potentially serious "
            "medical emergency."
        ),

        "general_care": [
            "Seek immediate medical attention.",
            "Contact your local emergency medical service.",
            "Do not delay emergency care while waiting for "
            "the chatbot."
        ],

        "medicine_information": (
            "Do not rely on the chatbot for emergency medicine "
            "instructions."
        ),

        "dose_guidance": (
            "Do not take extra medication in an attempt to "
            "treat a potentially serious emergency."
        ),

        "overdose_warning": (
            "If an overdose or poisoning may be involved, "
            "seek emergency medical help immediately."
        ),

        "doctor_advice": (
            "Please contact your local emergency medical service "
            "or go to the nearest emergency department."
        )
    }