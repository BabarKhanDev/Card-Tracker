from flask import Flask, request, render_template, redirect, Response
from flask_cors import CORS
from PIL import Image

from cardtracker.scripts.config import load_tcg_api_key, load_database_config
from scripts.database import (get_cards, get_sets, get_wishlist, add_to_wishlist, get_library, add_to_library,
                                  get_card_from_id)
from setup import setup_database
from scripts.responses import WishlistResponse, AllSetsResponse, AllCardsResponse, CardDetailsResponse, LibraryResponse

# App Configuration
config = load_database_config("config.ini")
tcg_api_key = load_tcg_api_key("config.ini")

# Set up flask
app = Flask(__name__)
CORS(app)

# Cache Cards
print("Checking if card features created. \n Note: if running for the first time this may take a while.")
setup_database()


#################
# JSON DELIVERY #
#################

# Return a list containing details for every set
# When we start the app we cache all sets in the database
# Each set contains:
#   id           - str,
#   image_url    - str, logo of the set
#   name         - str, display name for the set
#   series       - str, the series that the set belongs to, e.g. diamond and pearl
#   release_date - str, day, dd Mmm YYYY 00:00:00 GMT # TODO maybe I should trim the time
@app.get("/all_sets")
def get_all_sets():
    return AllSetsResponse(get_sets(config))


# Return a list of details for each card in a given set
# First we check if we have cached the cards in our database
# Each card contains:
#   id              - str
#   image_url_large - str, high-res image of card
#   image_url_small - str, low-res image of card
#   name            - str, display name of card
#   set_id          - str, the set that owns this card
@app.get("/set/<set_id>")
def get_set(set_id):
    try:
        return AllCardsResponse(get_cards(config, set_id))
    except Exception as e:
        return Response(str(e), status=404, mimetype='application/json')


# Return a dictionary with the details of our card
# These are the same as described above
# Note: we only look in our cached cards here, if it's not in the cache we return a 404,
#   even if the card might exist
@app.get("/card/<card_id>")
def get_card(card_id):
    try:
        return CardDetailsResponse(get_card_from_id(config, card_id))
    except Exception as e:
        return Response(str(e), status=404, mimetype='application/json')


# Return a dictionary of card_id : quantity wishlisted
# POST request allows you to adjust the quantity of wishlisted cards by a quantity
# POST parameters:
#   card_id - str, the card to adjust
#   amount  - int, the amount the adjust quantity by
@app.route("/wishlist_id", methods=["GET", "POST"])
def wishlist():
    # GET - Send the wishlist
    if request.method == 'GET':
        return WishlistResponse(get_wishlist(config))

    # POST - Add/Remove cards from the wishlist
    card_id = request.form["card_id"]
    amount = int(request.form["amount"])
    add_to_wishlist(config, card_id, amount)

    return WishlistResponse(get_wishlist(config))


# Return a dictionary of card_id : quantity in library
# Basically identical to wishlisting
# POST request allows you to adjust the quantity of library cards by a quantity
# POST parameters:
#   card_id - str, the card to adjust
#   amount  - int, the amount the adjust quantity by
@app.route("/library_id", methods=["GET", "POST"])
def library():
    # GET - Send the wishlist
    if request.method == 'GET':
        return LibraryResponse(get_library(conn))

    # POST - Add/Remove cards from the wishlist
    card_id = request.form["card_id"]
    amount = int(request.form["amount"])
    add_to_library(conn, card_id, amount)

    return LibraryResponse(get_library(conn))


# Return the display name of a set
# TODO maybe we want an endpoint to get all details of a card/set from it's id?
@app.get("/set_id_to_name/<set_id>")
def set_id_to_name(set_id):
    try:
        with conn.cursor() as cur:
            cur.execute("select name from sdk_cache.set where id = %s", (set_id,))
            return str(cur.fetchone()[0])
    except Exception as e:
        return Response(f"Set not found: {e}", status=404, mimetype='application/json')


# TODO improve this, will do when re-implementing card uploading
@app.route("/upload_cards", methods=['POST'])
def upload_cards():
    if 'file' not in request.files:
        return Response({"error": "No image file in request"}, status=400)

    files = request.files.getlist("file")
    for file in files:
        image = Image.open(file)
        image.save(f"upload_test/{file.filename[:-4]}.png", "PNG")

    return "Success"


#################
# HTML DELIVERY #
#################

@app.get("/")
def default():
    return redirect("/library")


# This will allow you to explore a given set
@app.get("/explore/<set_id>")
def explore_set(set_id):
    set_name = set_id_to_name(set_id)
    return render_template('set.html', set_name=set_name)


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
