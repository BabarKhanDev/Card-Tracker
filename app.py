# These will handle the requests from the web ui
from flask import Flask, request, render_template
from flask_cors import CORS

import pickle
from PIL import Image

from scripts.cards import cache_all_sets
from scripts.config import load_tcg_api_key, load_database_config
from scripts.database import connect, get_cards, get_sets, get_wishlist, add_to_wishlist, remove_from_wishlist

# Connect to database
config = load_database_config("config.ini")
conn = connect(config)

# Cache all sets
tcg_api_key = load_tcg_api_key("config.ini")
cache_all_sets(tcg_api_key, conn)

# Set up flask
app = Flask(__name__)
CORS(app)


#################
# JSON DELIVERY #
#################

# This returns some details about every set
@app.get("/all_sets")
def get_all_sets():
    return get_sets(conn)


# This will return all the cards in a set
@app.get("/set/<set_id>")
def get_set(set_id):
    return get_cards(conn, set_id)


# This will return the wishlished cards
# Posting allows you to add/remove a card from the wishlist
@app.route("/wishlist", methods=["GET", "POST"])
def get_wishlist():
    # GET - Send the wishlist
    if request.method == 'GET':
        return get_wishlist()

    # POST - Add/Remove card from the wishlist
    card_id = request.form["card_id"]
    amount = int(request.form["amount"])

    if amount > 0:
        add_to_wishlist(conn, card_id)
    else:
        remove_from_wishlist(conn, card_id)

    return get_wishlist()


# Get the name of a set with its id
@app.get("/set_id_to_name/<set_id>")
def set_id_to_name(set_id):
    try:
        with conn.cursor() as cur:
            cur.execute("select name from sdk_cache.set where id = %s", (set_id,))
            return cur.fetchone()[0]
    except Exception as e:
        return f"Set ID not found: {e}"


@app.route("/upload_cards", methods=['POST'])
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
