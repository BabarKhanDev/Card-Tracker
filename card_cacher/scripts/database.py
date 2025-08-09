import psycopg
import multiprocessing as mp
import requests
from io import BytesIO
from PIL import Image
from pokemontcgsdk import Set
from pokemontcgsdk import Card
from pgvector.psycopg import register_vector

from scripts.vision import create_model_and_preprocess

def connect(config):
    # connecting to the PostgreSQL server
    try:
        with psycopg.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg, Exception) as error:
        print(error)


# Cache a set and all of its cards
# This does not calculate the features of the card
def cache_set(cur, s: Set) -> None:

    # If the set is already cached then skip
    cur.execute("select count(*) from sdk_cache.set where id = %s", (s.id,))
    if cur.fetchone()[0] > 0:
        return

    # Add the set details to the DB
    cur.execute("INSERT INTO sdk_cache.set (id, image_uri, name, series, release_date) VALUES (%s, %s, %s, %s, %s)",
                (s.id, s.images.logo, s.name, s.series, s.releaseDate))

    cards = Card.where(q=f'set.id:{s.id}')
    for card in cards:

        cur.execute("""
        INSERT INTO sdk_cache.card (id, image_uri_large, image_uri_small, name, set_id) 
        VALUES (%s, %s, %s, %s, %s)
        """, (card.id, card.images.large, card.images.small, card.name, s.id,))


def calculate_features_of_all_cards(config, calculating_features: mp.Value) -> None:
    model, preprocess, device = create_model_and_preprocess()
    calculating_features.value = 1

    with psycopg.connect(**config) as conn:
        register_vector(conn)
        with conn.cursor() as cur:

            cur.execute("select id, image_uri_large from sdk_cache.card where features is NULL")
            for card_id, url in cur.fetchall():

                response = requests.get(url)
                if response.status_code != 200:
                    continue

                image = Image.open(BytesIO(response.content)).convert('RGB')
                batch = preprocess(image).unsqueeze(0).to(device)
                features = model(batch).squeeze(0).cpu().detach().numpy()
                cur.execute("UPDATE sdk_cache.card SET features = %s WHERE id = %s ", (features, card_id))

    calculating_features.value = 0


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
            cur.execute("""
                SELECT 
                    c.id, 
                    c.image_uri_large, 
                    c.image_uri_small, 
                    c.name, 
                    c.set_id, 
                    c.wishlist_quantity,
                    COUNT(m.card_id) AS library
                FROM sdk_cache.card c
                LEFT JOIN user_data.match m ON c.id = m.card_id
                WHERE c.set_id = %s
                GROUP BY 
                    c.id, 
                    c.name
            """, (set_id,))
            cards = cur.fetchall()
            return [{
                "id": card_id,
                "image_url_large": image_large,
                "image_url_small": image_small,
                "name": name,
                "set_id": set_id,
                "wishlist": wishlist,
                "library": library
            } for card_id, image_large, image_small, name, set_id, wishlist, library in cards]


# Get the details of a card from its id
def get_card_from_id(config, card_id: str):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            # TODO update to send wishlist and library
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
                "image_url_large": image_uri_large,
                "image_url_small": image_uri_small,
                "name": name,
                "set_id": set_id
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


def get_library(config, user_card_dir: str = "static/user_cards/"):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    upload.image_path AS upload_path,
                    upload.id as upload_id
                FROM user_data.upload
            """)

            return [{
                "imgsrc": f"{user_card_dir}{upload_path}",
                "upload_id": upload_id
            } for upload_path, upload_id in cur.fetchall()]


def get_matches(config, upload_id: str):
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
                WHERE upload_id = %s
            """, (upload_id, ))

            return [{
                "card_id": card_id,
                "image_url": image_url,
                "upload_path": upload_path
            } for card_id, image_url, upload_path in cur.fetchall()]


def get_match_counts(config, card_id):
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(card_id)
                FROM user_data.match
                WHERE card_id = %s
            """, (card_id, ))

            return cur.fetchone()[0]


def add_upload(config, image_path) -> str:
    pass


def add_match(config, upload_id, card_id):
    pass


def in_library(config, card_id: str):
    library = get_library()
    return card_id in {card["card_id"] for card in library}
