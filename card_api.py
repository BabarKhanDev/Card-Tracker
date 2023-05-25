# These will handle the requests from the web ui
from flask import Flask, request, render_template
from flask_cors import CORS

import pickle

# Load the set details pickle file
with open("tcg_cache/all_sets.pkl", "rb") as file:
    all_sets = pickle.load(file)

app = Flask(__name__)
CORS(app)

# This will return all sets in a dictionary
@app.get("/all_sets")
def get_all_sets():
    return all_sets

# This will return all of the cards in a set
@app.get("/set/<set_id>")
def get_set(set_id):

    try:
        with open(f"tcg_cache/card_data/{set_id}.pkl", "rb") as file:
            cards_in_set =  pickle.load(file)
        
        return cards_in_set

    except:
        return "Set Not Found"

# This will allow you to explore a given set
@app.get("/explore/<set_id>")
def explore_set(set_id):
    set_name = next(iter(filter(lambda x: x["id"] == set_id, all_sets)))["name"]
    return render_template('set.html', set_name = set_name)

# This will allow you to explore all sets
@app.get("/explore")
def explore_sets():
    return render_template('explore.html')

# This will allow you to explore the library
@app.get("/library")
def explore_library():
    return render_template('library.html')

# This will return the wishlished cards and allow you to add/remove a card from the wishlist
@app.route("/wishlist", methods = ["GET", "POST"])
def get_wishlist():
    # GET - Send the wishlist
    if request.method == 'GET':
        with open("user_library/wishlist.pkl", "rb") as file:
            return pickle.load(file)
    
    # POST - Add the amount specified to the wishlist
    with open("user_library/wishlist.pkl", "rb") as file:
        wishlist = pickle.load(file)

    print(request.form)
    card_id = request.form["card_id"]
    amount  = int(request.form["amount"])

    if card_id in wishlist:
        wishlist[card_id] += amount
    else:
        wishlist[card_id]  = amount

    if wishlist[card_id] <= 0:
        wishlist.pop(card_id)

    with open("user_library/wishlist.pkl", "wb") as file:
        pickle.dump(wishlist, file)

    return wishlist