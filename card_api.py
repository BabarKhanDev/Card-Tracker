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
    return all_sets

@app.get("/set/<set_id>")
def get_set(set_id):

    print(list(filter(lambda x: x["id"] == set_id, all_sets)))

    try:
        with open(f"card_db/card_data/{set_id}.pkl", "rb") as file:
            cards_in_set =  pickle.load(file)
        

        return cards_in_set

    except:
        return "Set Not Found"