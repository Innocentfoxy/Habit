from flask import Flask
from routes import pages
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)
    
    # Connect to MongoDB
    try:
        client = MongoClient(os.environ.get("MONGO_URI"))
        # Use "daily" database
        db = client["daily"]
        # Create "track" collection and make it available to the app
        app.track_collection = db["track"]
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)