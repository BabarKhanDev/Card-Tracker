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

    try:
        with open(f"card_db/card_data/{set_id}.pkl", "rb") as file:
            cards_in_set =  pickle.load(file)
        

        return cards_in_set

    except:
        return "Set Not Found"
    
@app.route("/wishlist", methods = ["GET", "POST"])
def get_wishlist():
    # GET - Send the wishlist
    if request.method == 'GET':
        with open("wishlist.pkl", "rb") as file:
            return pickle.load(file)
    
    # POST - Add the amount specified to the wishlist
    with open("wishlist.pkl", "rb") as file:
        wishlist = pickle.load(file)

    card_id = request.form["card_id"]
    amount  = int(request.form["amount"])

    if card_id in wishlist:
        wishlist[card_id] += amount
    else:
        wishlist[card_id]  = amount

    if wishlist[card_id] == 0:
        wishlist.pop(card_id)

    with open("wishlist.pkl", "wb") as file:
        pickle.dump(wishlist, file)

    return wishlist