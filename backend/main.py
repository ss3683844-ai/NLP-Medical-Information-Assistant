from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.nlp import generate_response
from services.safety import check_emergency


app = FastAPI(
    title="Medical Assistant API",
    description="NLP-based Medical Assistant",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------
# Allows the React frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


# ---------------------------------------------------------
# Medical Keywords
# ---------------------------------------------------------
# Used to identify whether a question is related to
# health or medicine before sending it to the NLP model.
MEDICAL_KEYWORDS = [
    "health",
    "healthy",
    "medical",
    "medicine",
    "medication",
    "medicines",
    "doctor",
    "hospital",
    "clinic",
    "symptom",
    "symptoms",
    "disease",
    "diseases",
    "illness",
    "pain",
    "fever",
    "headache",
    "cold",
    "cough",
    "flu",
    "allergy",
    "allergic",
    "stomach",
    "vomiting",
    "vomit",
    "nausea",
    "diarrhea",
    "diarrhoea",
    "rash",
    "infection",
    "blood",
    "bleeding",
    "breathing",
    "breath",
    "chest",
    "heart",
    "dizzy",
    "dizziness",
    "fatigue",
    "weakness",
    "tablet",
    "tablets",
    "drug",
    "drugs",
    "dose",
    "dosage",
    "overdose",
    "pregnancy",
    "pregnant",
    "anxiety",
    "stress",
    "sleep",
    "insomnia",
    "sick",
    "sickness",
    "injury",
    "injured",
    "body",
    "temperature",
    "blood pressure",
    "bp",
    "sugar",
    "diabetes",
    "vomiting",
    "constipation",
    "migraine",
    "throat",
    "ear",
    "eye",
    "skin",
    "tooth",
    "teeth"
]


# ---------------------------------------------------------
# Check Whether Question Is Medical
# ---------------------------------------------------------
def is_medical_question(text: str):
    text = text.lower().strip()

    for keyword in MEDICAL_KEYWORDS:
        if keyword in text:
            return True

    return False


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Medical Assistant API is running"
    }


# ---------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.strip()


    # -----------------------------------------------------
    # 1. Empty Question Check
    # -----------------------------------------------------
    if not user_message:

        return {
            "intent": "invalid",
            "confidence": 1.0,
            "problem": "Empty Question",

            "general_care": [
                "Please enter a health-related question."
            ],

            "medicine_information": (
                "No medicine information is available because "
                "no question was provided."
            ),

            "dose_guidance": (
                "No dose guidance is available."
            ),

            "overdose_warning": (
                "No overdose information is available."
            ),

            "doctor_advice": (
                "Please enter a medical or health-related question."
            )
        }


    # -----------------------------------------------------
    # 2. Emergency Check
    # -----------------------------------------------------
    # Emergency questions are checked before normal
    # medical classification.
    if check_emergency(user_message):

        return {
            "intent": "emergency",
            "confidence": 1.0,
            "problem": "Possible Medical Emergency",

            "general_care": [
                "Seek urgent medical attention immediately.",
                "Contact your local emergency service or go to the nearest emergency department.",
                "Do not delay emergency care while using this application."
            ],

            "medicine_information": (
                "Do not rely on this application for emergency "
                "medication instructions. Follow instructions from "
                "emergency medical professionals."
            ),

            "dose_guidance": (
                "Do not delay emergency treatment to calculate "
                "or take medication."
            ),

            "overdose_warning": (
                "If an overdose or poisoning may have occurred, "
                "seek urgent medical help or contact your local "
                "poison-control service."
            ),

            "doctor_advice": (
                "This may describe a medical emergency. Contact "
                "your local emergency service immediately or go "
                "to the nearest hospital."
            )
        }


    # -----------------------------------------------------
    # 3. Non-Medical Question Check
    # -----------------------------------------------------
    # This prevents the NLP model from classifying unrelated
    # questions such as:
    #
    # "What is the capital of India?"
    # "Write a Python program."
    # "Who is the president?"
    #
    # as medical intents such as "greeting", "fever", etc.
    if not is_medical_question(user_message):

        return {
            "intent": "out_of_domain",
            "confidence": 1.0,
            "problem": "Question Outside Medical Scope",

            "general_care": [
                "I can provide only medical and health-related information.",
                "Please ask a health-related question."
            ],

            "medicine_information": (
                "Medicine information is available only "
                "for health-related questions."
            ),

            "dose_guidance": (
                "Dose guidance is available only "
                "for health-related questions."
            ),

            "overdose_warning": (
                "For medication or poisoning concerns, "
                "please ask a medical question."
            ),

            "doctor_advice": (
                "Please ask a medical or health-related question."
            )
        }


    # -----------------------------------------------------
    # 4. Normal NLP-Based Medical Response
    # -----------------------------------------------------
    return generate_response(user_message)