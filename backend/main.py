from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.nlp import generate_response
from services.safety import check_emergency, emergency_response


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Medical Assistant API",
    description="NLP-based Medical Assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Medical Assistant API is running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.strip()

    # -----------------------------------------------------
    # 1. EMPTY MESSAGE
    # -----------------------------------------------------

    if not user_message:

        return {
            "intent": "invalid",
            "confidence": 1.0,
            "problem": "Empty Question",

            "general_care": [
                "Please enter a health-related question."
            ],

            "medicine_information":
                "No medicine information is available because "
                "no question was provided.",

            "dose_guidance":
                "No dose guidance is available.",

            "overdose_warning":
                "No overdose information is available.",

            "doctor_advice":
                "Please enter a medical or health-related question."
        }

    # -----------------------------------------------------
    # 2. EMERGENCY CHECK
    # -----------------------------------------------------

    if check_emergency(user_message):
        return emergency_response()

    # -----------------------------------------------------
    # 3. NLP MODEL
    # -----------------------------------------------------

    return generate_response(user_message)


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )