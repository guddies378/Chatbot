import json
import torch
import random
import logging
from nltk_utils import bag_of_words, tokenize
from model import NeuralNet
from pymongo import MongoClient

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['chatbot']
intents_collection = db['intents']
unanswered_collection = db['unanswered_questions']

def get_intents():
    document = intents_collection.find_one({}, {"_id": 0, "intents": 1})
    if document and 'intents' in document:
        return document['intents']
    return []

intents = get_intents()

FILE = "models/chatbot_model.pth"

def load_model():
    global model, all_words, tags
    data = torch.load(FILE, map_location=device)

    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data["all_words"]
    tags = data["tags"]
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

load_model()

def get_response(msg):
    global all_words, tags
    try:
        sentence = tokenize(msg)
        X = bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)
        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        if prob.item() > 0.75:
            for intent in intents:
                if tag == intent["tag"]:
                    return random.choice(intent['responses']), False

        response = "I apologize, I don't get it. Your inquiry is being addressed by the administrator. Kindly return later with the same inquiry. Thank you!"
        log_unanswered_question(msg)
        return response, True
    except Exception as e:
        logging.error(f"Error in get_response: {e}")
        return "An error occurred. Please try again later.", True

def log_unanswered_question(question):
    logging.info(f"Unanswered question: {question}")
    try:
        if not unanswered_collection.find_one({"question": question}):
            unanswered_collection.insert_one({"question": question})
    except Exception as e:
        logging.error(f"Error logging unanswered question: {e}")