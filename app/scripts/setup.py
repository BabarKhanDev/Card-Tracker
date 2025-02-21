from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
import psycopg
from tqdm import tqdm

from scripts.database import cache_set


def setup_database(config, tcg_api_key):
    print("Beginning data caching")
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            print("Successfully registered vector extension")

            # Cache all cards
            RestClient.configure(tcg_api_key)
            for s in tqdm(Set.all()):
                cache_set(cur, s)
                conn.commit()
            print("Successfully Cached All Sets")

        conn.commit()
