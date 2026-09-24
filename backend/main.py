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


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "Medical Assistant API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # Check for possible emergency symptoms first
    if check_emergency(request.message):

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
                "Do not rely on this application for emergency medication "
                "instructions. Follow instructions from emergency medical professionals."
            ),

            "dose_guidance": (
                "Do not delay emergency treatment to calculate or take medication."
            ),

            "overdose_warning": (
                "If an overdose or poisoning may have occurred, seek urgent "
                "medical help or contact your local poison-control service."
            ),

            "doctor_advice": (
                "This may describe a medical emergency. Contact your local "
                "emergency service immediately or go to the nearest hospital."
            )
        }

    # Normal NLP-based response
    return generate_response(request.message)