import psycopg2
from pokemontcgsdk import Set
from pokemontcgsdk import Card


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def cache_set(conn, s: Set) -> None:
    with conn.cursor() as cur:

        cur.execute("select count(*) from sdk_cache.set where id = %s", (s.id,))
        if cur.fetchone()[0] > 0:
            return

        cur.execute("INSERT INTO sdk_cache.set (id, image_uri, name, series, release_date) VALUES (%s, %s, %s, %s, %s)",
                    (s.id, s.images.logo, s.name, s.series, s.releaseDate))
        conn.commit()
    return


def get_cards(conn, set_id: str):
    with conn.cursor() as cur:
        # Check if we have cached the cards already
        cur.execute("select * from sdk_cache.card where set_id = %s", (set_id,))
        cached_cards = cur.fetchall()
        if len(cached_cards) > 0:
            return [{"id": c[0], "image_url": c[1], "name": c[2], "set_id": c[3]} for c in cached_cards]

        # We have not cached the cards yet, cache them and return
        cards = Card.where(q=f'set.id:{set_id}')
        for card in cards:
            cur.execute("INSERT INTO sdk_cache.card (id, image_uri, name, set_id) VALUES (%s, %s, %s, %s)",
                        (card.id, card.images.large, card.name, set_id))
        conn.commit()
        return [{"id": c.id, "image_uri": c.images.large, "name": c.name, "set_id": set_id} for c in cards]


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
        return [{"id": card[0]} for card in wishlist_cards]


def add_to_wishlist(conn, card_id: str):
    with conn.cursor() as cur:
        if cur.execute("select count(*) from user_data.wishlist where card_id = %s", (card_id,)).fetchone()[0] == 0:
            cur.execute("insert into user_data.wishlist (card_id) values (%s)", (card_id,))


def remove_from_wishlist(conn, card_id: str):
    with conn.cursor() as cur:
        cur.execute("delete from user_data.wishlist where card_id = %s", (card_id,))
