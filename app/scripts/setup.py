from pokemontcgsdk import Set
from pokemontcgsdk import RestClient
import psycopg
from pgvector.psycopg import register_vector
from tqdm import tqdm
import os
from datetime import datetime
import json

from scripts.config import load_database_config, load_tcg_api_key
from scripts.database import cache_set
from scripts.vision import create_model_and_preprocess


def setup_database():

    with open("../../setup.log", "a") as file:
        file.write(f"Performing database setup: {datetime.now().isoformat()}")

    config = load_database_config("../config.ini")
    with psycopg.connect(**config) as conn:
        register_vector(conn)

        with conn.cursor() as cur:

            cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            print("Successfully registered vector extension")

            # Cache all cards
            serialised_features = None
            if os.path.isfile("../serialised_features.json"):
                print("Serialised features found")
                with open("../serialised_features.json", "r") as file:
                    serialised_features = json.load(file)

            tcg_api_key = load_tcg_api_key("../config.ini")
            RestClient.configure(tcg_api_key)
            model, preprocess, device = create_model_and_preprocess()
            for s in tqdm(Set.all()):
                cache_set(cur, s, model, preprocess, device, serialised_features)
                conn.commit()
            print("Successfully Cached All Sets")

        conn.commit()


if "__main__" == __name__:
    # TODO maybe we should have a separate microservice that does this rather than manually running it?
    setup_database()
