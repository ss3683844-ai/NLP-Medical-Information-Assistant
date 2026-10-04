import { useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I am your Medical Assistant. How can I help you?"
    }
  ]);

  const [loading, setLoading] = useState(false);

  // --------------------------------------------------
  // Send Message
  // --------------------------------------------------
  const sendMessage = async () => {
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        sender: "user",
        text: userMessage
      }
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: userMessage
          })
        }
      );

      if (!response.ok) {
        throw new Error("Server error");
      }

      const data = await response.json();

      // --------------------------------------------------
      // OUT-OF-DOMAIN RESPONSE
      // --------------------------------------------------
      if (data.intent === "out_of_domain") {
        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text:
              "I can provide only medical and health-related information. Please ask a health-related question.",
            outOfDomain: true
          }
        ]);

        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // INVALID / EMPTY RESPONSE
      // --------------------------------------------------
      if (data.intent === "invalid") {
        setMessages((prev) => [
          ...prev,
          {
            sender: "bot",
            text: "Please enter a health-related question."
          }
        ]);

        setLoading(false);
        return;
      }

      // --------------------------------------------------
      // NORMAL MEDICAL / EMERGENCY RESPONSE
      // --------------------------------------------------
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          problem: data.problem,
          generalCare: data.general_care,
          medicineInformation: data.medicine_information,
          doseGuidance: data.dose_guidance,
          overdoseWarning: data.overdose_warning,
          doctorAdvice: data.doctor_advice,
          intent: data.intent,
          confidence: data.confidence
        }
      ]);
    } catch (error) {
      console.error("Error:", error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "Sorry, I could not connect to the medical assistant server."
        }
      ]);
    }

    setLoading(false);
  };

  // --------------------------------------------------
  // Enter Key
  // --------------------------------------------------
  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  // --------------------------------------------------
  // Clear Chat
  // --------------------------------------------------
  const clearChat = () => {
    setMessages([
      {
        sender: "bot",
        text: "Hello! I am your Medical Assistant. How can I help you?"
      }
    ]);
  };

  // --------------------------------------------------
  // Suggestions
  // --------------------------------------------------
  const suggestions = [
    "Fever",
    "Headache",
    "Cold",
    "Cough",
    "Stomach Pain",
    "Doctor Visit"
  ];

  const handleSuggestion = (suggestion) => {
    setMessage(suggestion);
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------
  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div>
          <h1>Medical Assistant</h1>
          <p>NLP-Based Medical Information Assistant</p>
        </div>

        <button
          className="clear-button"
          onClick={clearChat}
        >
          Clear Chat
        </button>
      </header>


      {/* Chat Area */}
      <main className="chat-container">

        {messages.map((msg, index) => (

          <div
            key={index}
            className={`message-wrapper ${msg.sender}`}
          >

            {/* Avatar */}
            <div className="avatar">
              {msg.sender === "bot" ? "🤖" : "👤"}
            </div>


            {/* Message */}
            <div
              className={`message ${msg.sender}`}
            >

              {/* Name */}
              <div className="message-name">
                {msg.sender === "bot"
                  ? "Medical Assistant"
                  : "You"}
              </div>


              {/* Normal Text Message */}
              {msg.text && (
                <div className="message-text">
                  {msg.text}
                </div>
              )}


              {/* ------------------------------------------------
                  OUT-OF-DOMAIN MESSAGE
                  ------------------------------------------------ */}
              {msg.outOfDomain && (
                <div className="out-of-domain-message">
                  <div className="out-of-domain-title">
                    🩺 Medical Assistant
                  </div>

                  <div className="out-of-domain-text">
                    I can provide only medical and health-related
                    information.
                  </div>

                  <div className="out-of-domain-text">
                    Please ask a health-related question.
                  </div>
                </div>
              )}


              {/* ------------------------------------------------
                  STRUCTURED MEDICAL RESPONSE
                  ------------------------------------------------ */}
              {msg.sender === "bot" &&
                msg.problem &&
                !msg.outOfDomain && (

                <div className="medical-response">

                  {/* Problem */}
                  <div className="medical-section problem-section">

                    <div className="section-title">
                      🩺 Possible Topic
                    </div>

                    <div className="section-content">
                      {msg.problem}
                    </div>

                  </div>


                  {/* General Care */}
                  {msg.generalCare &&
                    msg.generalCare.length > 0 && (

                    <div className="medical-section">

                      <div className="section-title">
                        🏠 General Care
                      </div>

                      <ul>
                        {msg.generalCare.map(
                          (item, i) => (
                            <li key={i}>
                              {item}
                            </li>
                          )
                        )}
                      </ul>

                    </div>
                  )}


                  {/* Medicine */}
                  <div className="medical-section medicine-section">

                    <div className="section-title">
                      💊 Medicine Information
                    </div>

                    <div className="section-content">
                      {msg.medicineInformation}
                    </div>

                  </div>


                  {/* Dose */}
                  <div className="medical-section dose-section">

                    <div className="section-title">
                      📏 Dose Safety
                    </div>

                    <div className="section-content">
                      {msg.doseGuidance}
                    </div>

                  </div>


                  {/* Overdose */}
                  <div className="medical-section overdose-section">

                    <div className="section-title">
                      ⚠️ Overdose Warning
                    </div>

                    <div className="section-content">
                      {msg.overdoseWarning}
                    </div>

                  </div>


                  {/* Doctor */}
                  <div className="medical-section doctor-section">

                    <div className="section-title">
                      🏥 When to See a Doctor
                    </div>

                    <div className="section-content">
                      {msg.doctorAdvice}
                    </div>

                  </div>


                  {/* NLP Information */}
                  {msg.intent &&
                    msg.confidence !== undefined && (

                    <div className="nlp-info">

                      <span>
                        Intent: {msg.intent}
                      </span>

                      <span>
                        Confidence:{" "}
                        {(msg.confidence * 100).toFixed(1)}%
                      </span>

                    </div>
                  )}

                </div>
              )}

            </div>

          </div>

        ))}


        {/* Thinking */}
        {loading && (

          <div className="message-wrapper bot">

            <div className="avatar">
              🤖
            </div>

            <div className="message bot">

              <div className="message-name">
                Medical Assistant
              </div>

              <div className="thinking">
                Thinking...
              </div>

            </div>

          </div>

        )}

      </main>


      {/* Suggestions */}
      <div className="suggestions">

        {suggestions.map((suggestion) => (

          <button
            key={suggestion}
            onClick={() =>
              handleSuggestion(suggestion)
            }
          >
            {suggestion}
          </button>

        ))}

      </div>


      {/* Input */}
      <div className="input-area">

        <input
          type="text"
          placeholder="Ask a health-related question..."
          value={message}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          onKeyDown={handleKeyPress}
          disabled={loading}
        />

        <button
          onClick={sendMessage}
          disabled={loading}
        >
          {loading ? "..." : "Send"}
        </button>

      </div>


      {/* Disclaimer */}
      <div className="disclaimer">
        This application provides general health information
        for educational purposes only. It does not provide
        diagnosis or personalized medical treatment.
      </div>

    </div>
  );
}

export default App;