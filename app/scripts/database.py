import psycopg
from pokemontcgsdk import Set
from pokemontcgsdk import Card

import requests
from io import BytesIO
from PIL import Image


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
                "id": set_id,
                "image_url": image_uri,
                "name": name,
                "series": series,
                "release_date": release_date
            } for set_id, image_uri, name, series, release_date in all_sets]


# Get the details of a specific set
def get_set_details(config, set_id):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                select id, image_uri, name, series, release_date 
                from sdk_cache.set
                where id = %s
            """, (set_id,))

            response = cur.fetchone()
            if response is None:
                return None

            set_id, image_uri, name, series, release_date = response

            return {
                "id": set_id,
                "image_url": image_uri,
                "name": name,
                "series": series,
                "release_date": release_date
            }


# Get all cards in a set
def get_cards(config, set_id: str):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("select * from sdk_cache.card where set_id = %s", (set_id,))
            cards = cur.fetchall()
            return [{
                "id": c[0],
                "image_url_large": c[1],
                "image_url_small": c[2],
                "name": c[3],
                "set_id": c[4]
            } for c in cards]


# Get the details of a card from its id
def get_card_from_id(config, card_id: str):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                select id, set_id, image_uri_large, image_uri_small, name 
                from sdk_cache.card 
                where id = %s
            """, (card_id,))

            response = cur.fetchone()
            if response is None:
                return None

            card_id, set_id, image_uri_large, image_uri_small, name = response

            return {
                "id": card_id,
                "image_url_large": set_id,
                "image_url_small": image_uri_large,
                "name": image_uri_small,
                "set_id": name
            }


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


def get_library(config):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    match.card_id AS card_id,
                    card.image_uri_small AS image_url,
                    upload.image_path AS upload_path
                FROM user_data.match
                JOIN sdk_cache.card ON match.card_id = card.id
                JOIN user_data.upload ON match.upload_id = upload.id
            """)

            return [{
                "card_id": card_id,
                "image_url": image_url,
                "upload_path": upload_path
            } for card_id, image_url, upload_path in cur.fetchall()]


def add_upload(config, image_path) -> str:
    pass


def add_match(config, upload_id, card_id):
    pass


def in_library(config, card_id: str):
    library = get_library()
    return card_id in {card["card_id"] for card in library}
