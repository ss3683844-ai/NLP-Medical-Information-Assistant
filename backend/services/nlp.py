import json
import joblib


# Load trained NLP model
model = joblib.load(
    "models/intent_model.pkl"
)


# Load medical data
with open(
    "data/medical_data.json",
    "r",
    encoding="utf-8"
) as file:
    medical_data = json.load(file)


# Create intent -> response mapping
responses = {
    item["intent"]: item["response"]
    for item in medical_data
}


def generate_response(text: str):

    # Get prediction probabilities
    probabilities = model.predict_proba([text])[0]

    # Find highest probability
    index = probabilities.argmax()

    # Get predicted intent
    intent = model.classes_[index]

    # Get confidence
    confidence = probabilities[index]

    # Get structured medical response
    response_data = responses.get(
        intent,
        responses.get("unknown")
    )

    return {
        "intent": intent,
        "confidence": round(float(confidence), 3),

        "problem": response_data.get(
            "problem",
            "General Health Information"
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
            "Follow the medicine label or professional medical advice."
        ),

        "overdose_warning": response_data.get(
            "overdose_warning",
            "Never exceed the recommended dose."
        ),

        "doctor_advice": response_data.get(
            "doctor_advice",
            "Consult a healthcare professional if symptoms are concerning."
        )
    }