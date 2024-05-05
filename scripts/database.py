import psycopg2
from pokemontcgsdk import Set


def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def cache_set(conn, set:Set) -> None:
    with conn.cursor() as cur:

        cur.execute("select count(*) from sdk_cache.set where id = %s", (set.id,))
        if cur.fetchone()[0] > 0:
            return

        cur.execute("INSERT INTO sdk_cache.set (id, image_uri, name, series, release_date) VALUES (%s, %s, %s, %s, %s)",
                    (set.id, set.images.logo, set.name, set.series, set.releaseDate))
        conn.commit()
