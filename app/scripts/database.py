import psycopg
from pokemontcgsdk import Set
from pokemontcgsdk import Card

import requests
from io import BytesIO
from PIL import Image


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
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


def get_cards(conn, set_id: str):
    with conn.cursor() as cur:
        # Check if we have cached the cards already
        cur.execute("select * from sdk_cache.card where set_id = %s", (set_id,))
        cached_cards = cur.fetchall()
        if len(cached_cards) > 0:
            return [{
                "id": c[0],
                "image_url_large": c[1],
                "image_url_small": c[2],
                "name": c[3],
                "set_id": c[4]
            } for c in cached_cards]

        # We have not cached the cards yet, cache them and return
        cards = Card.where(q=f'set.id:{set_id}')
        for card in cards:
            cur.execute("INSERT INTO sdk_cache.card (id, image_uri_large, image_uri_small, name, set_id) VALUES (%s, %s, %s, %s, %s)",
                        (card.id, card.images.large, card.images.small, card.name, set_id))
        conn.commit()
        return [{
            "id": c.id,
            "image_uri_large": c.images.large,
            "image_uri_small": c.images.small,
            "name": c.name,
            "set_id": set_id
        } for c in cards]


def get_card_from_id(conn, card_id: str):
    with conn.cursor() as cur:
        cur.execute("select * from sdk_cache.card where id = %s", (card_id,))
        d = cur.fetchone()
        return {"id": d[0], "image_url_large": d[1], "image_url_small": d[2], "name": d[3], "set_id": d[4]}


def get_sets(conn):
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


def get_wishlist(conn):
    with conn.cursor() as cur:
        cur.execute("select * from user_data.wishlist")
        wishlist_cards = cur.fetchall()
        return {card[0]: card[1] for card in wishlist_cards}


def remove_from_wishlist(conn, card_id: str, quantity: int = 1):
    return add_to_wishlist(conn, card_id, quantity * -1)


def add_to_wishlist(conn, card_id: str, quantity: int = None):

    if not in_wishlist(conn, card_id):
        with conn.cursor() as cur:
            cur.execute("insert into user_data.wishlist values (%s, 0) ", (card_id, ))
            conn.commit()

    if quantity is None:
        with conn.cursor() as cur:
            cur.execute("delete from user_data.wishlist where card_id = %s", (card_id,))
            conn.commit()
        return

    with conn.cursor() as cur:
        cur.execute("UPDATE user_data.wishlist SET quantity = quantity + %s WHERE card_id = %s", (quantity, card_id,))
        cur.execute("delete from user_data.wishlist where quantity <= 0")
        conn.commit()


def in_wishlist(conn, card_id: str):
    wishlist = get_wishlist(conn)
    return card_id in wishlist


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
