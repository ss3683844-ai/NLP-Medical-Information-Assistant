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

  // -------------------------------
  // Send Message
  // -------------------------------
  const sendMessage = async () => {
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();

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
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Sorry, I could not connect to the medical assistant server."
        }
      ]);
    }

    setLoading(false);
  };

  // -------------------------------
  // Enter Key
  // -------------------------------
  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  // -------------------------------
  // Clear Chat
  // -------------------------------
  const clearChat = () => {
    setMessages([
      {
        sender: "bot",
        text: "Hello! I am your Medical Assistant. How can I help you?"
      }
    ]);
  };

  return (
    <div className="app">

      <div className="chat-container">

        {/* Header */}
        <div className="header">

          <div className="header-top">

            <h1>🩺 Medical Assistant</h1>

            <button
              className="clear-button"
              onClick={clearChat}
            >
              Clear Chat
            </button>

          </div>

          <p>
            NLP-Based Medical Information Assistant
          </p>

          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>

        </div>


        {/* Chat */}
        <div className="chat-box">

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`message-wrapper ${msg.sender}`}
            >

              <div className="avatar">
                {msg.sender === "bot" ? "🤖" : "👤"}
              </div>

              <div
                className={`message ${msg.sender}`}
              >

                <div className="message-name">
                  {msg.sender === "bot"
                    ? "Medical Assistant"
                    : "You"}
                </div>


                {/* Normal text message */}
                {msg.text && (
                  <div className="message-text">
                    {msg.text}
                  </div>
                )}


                {/* Structured Medical Response */}
                {msg.sender === "bot" &&
                  msg.problem && (

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


                      {/* NLP */}
                      {msg.intent &&
                        msg.confidence !== undefined && (

                          <div className="nlp-info">

                            <span>
                              Intent: {msg.intent}
                            </span>

                            <span>
                              Confidence:{" "}
                              {(msg.confidence * 100).toFixed(1)}
                              %
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

        </div>


        {/* Suggestions */}
        <div className="suggestions">

          <button
            onClick={() =>
              setMessage("I have a fever")
            }
          >
            🤒 Fever
          </button>

          <button
            onClick={() =>
              setMessage("I have a headache")
            }
          >
            🤕 Headache
          </button>

          <button
            onClick={() =>
              setMessage("I have a cold")
            }
          >
            🤧 Cold
          </button>

          <button
            onClick={() =>
              setMessage("I have a cough")
            }
          >
            😷 Cough
          </button>

          <button
            onClick={() =>
              setMessage("I have stomach pain")
            }
          >
            🤢 Stomach Pain
          </button>

          <button
            onClick={() =>
              setMessage("When should I see a doctor?")
            }
          >
            🏥 Doctor Visit
          </button>

        </div>


        {/* Input Area */}
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
          ⚠️ This application provides general health
          information only. It is not a substitute for
          professional medical advice.
        </div>

      </div>

    </div>
  );
}

export default App;