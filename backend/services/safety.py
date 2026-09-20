EMERGENCY_KEYWORDS = [
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe chest pain",
    "chest pain",
    "unconscious",
    "loss of consciousness",
    "seizure",
    "stroke",
    "heavy bleeding",
    "severe bleeding",
    "not breathing"
]


def check_emergency(text: str):
    text = text.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text:
            return True

    return False