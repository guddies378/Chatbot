import threading
import subprocess
from pymongo import MongoClient
from pymongo.errors import PyMongoError

def train_model():
    try:
        result = subprocess.run(['python', 'train.py'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr)
        print("Model trained successfully.")
    except Exception as e:
        print(f"Error training model: {e}")

def listen_to_changes():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['chatbot']
    intents_collection = db['intents']

    try:
        with intents_collection.watch() as stream:
            for change in stream:
                print("Change detected:", change)
                train_model()
    except PyMongoError as e:
        print(f"Error listening to changes: {e}")

if __name__ == "__main__":
    listener_thread = threading.Thread(target=listen_to_changes)
    listener_thread.start()