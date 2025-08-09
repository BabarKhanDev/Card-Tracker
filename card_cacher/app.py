from flask import Flask
from flask_cors import CORS
import multiprocessing as mp

from scripts.config import load_tcg_api_key, load_database_config
from scripts.setup import setup_database
from scripts.database import calculate_features_of_all_cards

print("Starting Card Cacher")

# App Configuration
config = load_database_config("config.ini")
tcg_api_key = load_tcg_api_key("config.ini")

# Database Setup
setup_database(config, tcg_api_key)

# Feature processor setup
calculating_features = mp.Value("i", 0)
feature_process = mp.Process(target=calculate_features_of_all_cards, args=(config, calculating_features))
feature_process.start()
feature_process.join()

# Set up flask
app = Flask(__name__)
CORS(app)
app.run(port=5001)

@app.get("/status")
def status():
    return {
        "calculating_features": calculating_features.value
    }