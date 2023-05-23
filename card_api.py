# These will handle the requests from the web ui
from flask import Flask, request
from flask_cors import CORS

import pickle

# Load the set details pickle file
with open("all_sets.pkl", "rb") as file:
    all_sets = pickle.load(file)

# Flask API
app = Flask(__name__)
CORS(app)

@app.get("/set_details")
def get_set_details():
    requested_set = request.args.get('set') or -1
    
    print('data from client:', requested_set)
    dictToReturn = {'answer':42}


    return {"programming_languages":list(dictToReturn.values())}

@app.get("/all_sets")
def get_all_sets():
    
    # We want to send back all sets
    # We will send back the name of the set along with the url for an icon for it

    return all_sets