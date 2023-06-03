# These will handle the requests from the web ui
from flask import Flask, request, render_template
from flask_cors import CORS

import pickle
from PIL import Image
import numpy as np

# Load the set details pickle file
with open("tcg_cache/all_sets.pkl", "rb") as file:
    all_sets = pickle.load(file)

app = Flask(__name__)
CORS(app)

#################
# JSON DELIVERY #
#################

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

# This will return the wishlished cards 
# Posting allows you to add/remove a card from the wishlist
@app.route("/wishlist_json", methods = ["GET", "POST"])
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

@app.get("/wishlist_cards")
def get_wishlist_cards():

    with open("user_library/wishlist.pkl", "rb") as file:
        wishlist = pickle.load(file)

    card_data = []
    for card in wishlist:

        # Split the wishlist item up into the set and number
        card_set = card.split("-")[0]
        card_number = card.split("-")[1]

        # Remove leading zeros from string
        non_zero_found = False
        for char in card_number[:]:
            if char == '0':
                card_number = card_number[1:]
            else:
                break

        # Load the cached data for that set
        with open(f"tcg_cache/card_data/{card_set}.pkl", "rb") as file:
            entire_set = pickle.load(file)

        # Find the card within that set that has the right number
        filtered_cards = list(filter(lambda x: x.number == card_number, entire_set))
        card_data.append(filtered_cards[0])
    
    return card_data

@app.get("/set_id_to_name/<set_id>")
def set_id_to_name(set_id):
    try:
        set_name = next(iter(filter(lambda x: x["id"] == set_id, all_sets)))["name"]
        return set_name
    except:
        return "Set ID not found"

@app.route("/upload_cards", methods = ['POST'])
def upload_cards():
    try:
        files = request.files.getlist("file")
        print(files)
        for file in files:
            image = Image.open(file)
            image.save(f"upload_test/{file.filename[:-4]}.png", "PNG")

        return "Success"
    except:
        return "Upload Failed"

#################
# HTML DELIVERY #
#################

# This will allow you to explore a given set
@app.get("/explore/<set_id>")
def explore_set(set_id):
    set_name = set_id_to_name(set_id)
    return render_template('set.html', set_name = set_name)


# This will allow you to explore all sets
@app.get("/explore")
def explore_sets():
    return render_template('explore.html')

# This will allow you to explore the library
@app.get("/library")
def explore_library():
    return render_template('library.html')

@app.get("/wishlist")
def explore_wishlist():
    return render_template('wishlist.html')