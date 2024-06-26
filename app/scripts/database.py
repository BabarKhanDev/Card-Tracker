import psycopg
from pokemontcgsdk import Set
from pokemontcgsdk import Card

import requests
from io import BytesIO
from PIL import Image
import numpy as np
from pgvector.psycopg import register_vector


def connect(config):
    # connecting to the PostgreSQL server
    try:
        with psycopg.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg, Exception) as error:
        print(error)


# Cache a set and all of its cards
def cache_set(conn, cur, s: Set, model, preprocess, device) -> None:
    # If the set is already cached then skip
    cur.execute("select count(*) from sdk_cache.set where id = %s", (s.id,))
    if cur.fetchone()[0] > 0:
        return

    # Cache the set details in the DB
    cur.execute("INSERT INTO sdk_cache.set (id, image_uri, name, series, release_date) VALUES (%s, %s, %s, %s, %s)",
                (s.id, s.images.logo, s.name, s.series, s.releaseDate))

    cards = Card.where(q=f'set.id:{s.id}')
    for card in cards:

        try:
            # Calculate Features
            response = requests.get(card.images.large)
            if response.status_code != 200:
                raise Exception("Failed to download image")

            image = Image.open(BytesIO(response.content)).convert('RGB')
            batch = preprocess(image).unsqueeze(0).to(device)
            features = model(batch).squeeze(0).cpu().detach().numpy()

            # Cache the card details in the DB
            cur.execute(
                "INSERT INTO sdk_cache.card (id, image_uri_large, image_uri_small, name, set_id, features) VALUES (%s, %s, %s, %s, %s, %s)",
                (card.id, card.images.large, card.images.small, card.name, s.id, features,))

        except Exception as e:
            with open("setup.log", "a") as file:
                file.write(f"Failed to download: {card.id}\n")
                file.write(f"{e}\n")

            cur.execute(
                "INSERT INTO sdk_cache.card (id, image_uri_large, image_uri_small, name, set_id) VALUES (%s, %s, %s, %s, %s)",
                (card.id, card.images.large, card.images.small, card.name, s.id,))

    conn.commit()


# Get all sets
def get_sets(config):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("select id, image_uri, name, series, release_date from sdk_cache.set")
            all_sets = cur.fetchall()
            return [{
                "id": s[0],
                "image_url": s[1],
                "name": s[2],
                "series": s[3],
                "release_date": s[4]
            } for s in all_sets]


# Get all cards in a set
def get_cards(config, set_id: str):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            # Check if we have cached the cards already
            cur.execute("select * from sdk_cache.card where set_id = %s", (set_id,))
            cards = cur.fetchall()
            return [{
                "id": c[0],
                "image_url_large": c[1],
                "image_url_small": c[2],
                "name": c[3],
                "set_id": c[4]
            } for c in cards]


# Get the cached details of a card from its id
def get_card_from_id(config, card_id: str):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from sdk_cache.card where id = %s", (card_id,))
            d = cur.fetchone()
            return {"id": d[0], "image_url_large": d[1], "image_url_small": d[2], "name": d[3], "set_id": d[4]}


def get_wishlist(config):
    # Returns a map from card_id to wishlist quantity for all cards that are wish-listed
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select id, wishlist_quantity
                from sdk_cache.card 
                where wishlist_quantity > 0
            """)

            return {card_id: quantity for (card_id, quantity) in cur.fetchall()}


def remove_from_wishlist(config, card_id: str, quantity: int = 1):
    return add_to_wishlist(config, card_id, quantity * -1)


def add_to_wishlist(config, card_id: str, quantity: int):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                update sdk_cache.card
                set wishlist_quantity = greatest(0, wishlist_quantity + %s) 
                where id = %s;
            """, (quantity, card_id,))
            conn.commit()


def in_wishlist(config, card_id: str):
    wishlist = get_wishlist(config)
    return card_id in wishlist.keys()


def get_library(conn):
    with conn.cursor() as cur:
        cur.execute("select * from user_data.library")
        library_cards = cur.fetchall()
        return {card[0]: card[1] for card in library_cards}


def add_to_library(conn, card_id: str, quantity: int = None):
    if not in_library(conn, card_id):
        with conn.cursor() as cur:
            cur.execute("insert into user_data.library values (%s, 0) ", (card_id, ))
            conn.commit()

    if quantity is None:
        with conn.cursor() as cur:
            cur.execute("delete from user_data.library where card_id = %s", (card_id,))
            conn.commit()
        return

    with conn.cursor() as cur:
        cur.execute("UPDATE user_data.library SET quantity = quantity + %s WHERE card_id = %s", (quantity, card_id,))
        cur.execute("delete from user_data.library where quantity <= 0")
        conn.commit()


def in_library(conn, card_id: str):
    library = get_library(conn)
    return card_id in library
