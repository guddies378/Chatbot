from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from chat import get_response, log_unanswered_question, load_model
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot']
intents_collection = db['intents']

@app.post("/predict")
def predict():
    try:
        text = request.get_json().get("message")
        response, is_unanswered = get_response(text)
        message = {"answer": response}

        if is_unanswered:
            log_unanswered_question(text)

        return jsonify(message)
    except Exception as e:
        logging.error(f"Error in /predict: {e}")
        return jsonify({
            "answer": "An error occurred. Please try again."
        }), 200

@app.post("/reload_model")
def reload_model():
    try:
        load_model()
        return jsonify({"status": "Model reloaded successfully"}), 200
    except Exception as e:
        logging.error(f"Error in /reload_model: {e}")
        return jsonify({"status": "Failed to reload model"}), 500

@app.get("/faqs")
def get_faqs():
    try:
        documents = list(intents_collection.find({}, {"_id": 0, "intents": 1}))
        intents = []
        for doc in documents:
            intents.extend(doc.get("intents", []))
        return jsonify(intents), 200
    except Exception as e:
        logging.error(f"Error in /faqs: {e}")
        return jsonify({"status": "Failed to load FAQs"}), 500

if __name__ == "__main__":
    app.run(debug=True)