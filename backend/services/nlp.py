import json
import joblib


# --------------------------------------------------
# Load trained NLP model
# --------------------------------------------------
model = joblib.load(
    "models/intent_model.pkl"
)


# --------------------------------------------------
# Load medical data
# --------------------------------------------------
with open(
    "data/medical_data.json",
    "r",
    encoding="utf-8"
) as file:
    medical_data = json.load(file)


# --------------------------------------------------
# Create intent -> response mapping
# --------------------------------------------------
responses = {
    item["intent"]: item["response"]
    for item in medical_data
}


# --------------------------------------------------
# Generate Response
# --------------------------------------------------
def generate_response(text: str):

    # Get prediction probabilities
    probabilities = model.predict_proba([text])[0]

    # Find highest probability
    index = probabilities.argmax()

    # Get predicted intent
    intent = model.classes_[index]

    # Get confidence
    confidence = float(probabilities[index])


    # --------------------------------------------------
    # Confidence Threshold
    # --------------------------------------------------
    # If the model is not confident enough,
    # treat the question as unknown.
    #
    # 0.50 = 50%
    #
    CONFIDENCE_THRESHOLD = 0.50


    if confidence < CONFIDENCE_THRESHOLD:

        return {
            "intent": "unknown",
            "confidence": round(confidence, 3),

            "problem": "I don't know",

            "general_care": [
                "I don't have enough information to answer this question accurately."
            ],

            "medicine_information": (
                "I don't have reliable information about this specific question."
            ),

            "dose_guidance": (
                "I cannot provide dose guidance when I am not "
                "confident about the medical topic."
            ),

            "overdose_warning": (
                "If this question involves an overdose or poisoning, "
                "seek urgent medical help."
            ),

            "doctor_advice": (
                "Please consult a qualified healthcare professional "
                "for accurate advice."
            )
        }


    # --------------------------------------------------
    # Get structured response
    # --------------------------------------------------
    response_data = responses.get(intent)


    # --------------------------------------------------
    # Intent not found in medical data
    # --------------------------------------------------
    if response_data is None:

        return {
            "intent": "unknown",
            "confidence": round(confidence, 3),

            "problem": "I don't know",

            "general_care": [
                "I don't have enough information to answer this question accurately."
            ],

            "medicine_information": (
                "I don't have reliable information about this specific question."
            ),

            "dose_guidance": (
                "I cannot provide dose guidance for this question."
            ),

            "overdose_warning": (
                "If this involves an overdose or poisoning, "
                "seek urgent medical help."
            ),

            "doctor_advice": (
                "Please consult a qualified healthcare professional."
            )
        }


    # --------------------------------------------------
    # Return known medical response
    # --------------------------------------------------
    return {
        "intent": intent,
        "confidence": round(confidence, 3),

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