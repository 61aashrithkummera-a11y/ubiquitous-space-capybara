from flask import Flask, request, jsonify, render_template
import os, time, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# MOCK_MODE True => never call external APIs
MOCK_MODE = True

# Load env vars but ignore them in mock mode
API_KEY = os.getenv("LLM_API_KEY", "").strip()
API_URL = os.getenv("API_URL", "").strip()
MODEL = os.getenv("MODEL", "mock-model").strip()

if MOCK_MODE:
    logging.info("Running in MOCK_MODE: external API calls are disabled.")
else:
    if not API_KEY or not API_URL:
        raise RuntimeError("Real API mode enabled but LLM_API_KEY or API_URL is missing.")

CONVERSATIONS = {"default": [
    {"role": "system", "content": "You are KummeraAI, a helpful assistant (mock mode)."}
]}

def mock_llm_reply(messages):
    last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last = m.get("content", "")
            break
    time.sleep(0.2)
    if not last:
        return "Hello — I'm KummeraAI (mock). Ask me anything!"
    if "help" in last.lower():
        return "Sure — explain what you need help with, and I'll pretend to assist."
    return f"(mock) I heard: \"{last}\" — here's a friendly reply from KummeraAI."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True)
    user_msg = body.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "empty message"}), 400

    convo = CONVERSATIONS["default"]
    convo.append({"role": "user", "content": user_msg})

    if MOCK_MODE:
        reply = mock_llm_reply(convo)
    else:
        # Safety: this block will only run if MOCK_MODE is False and API_KEY/API_URL present
        # Implement your real call_llm here when you decide to use a real model.
        reply = "(real API mode placeholder)"

    convo.append({"role": "assistant", "content": reply})
    if len(convo) > 40:
        CONVERSATIONS["default"] = [convo[0]] + convo[-38:]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
